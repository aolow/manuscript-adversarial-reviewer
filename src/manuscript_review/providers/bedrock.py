"""Amazon Bedrock Converse adapter with explicit opt-in and validated JSON output."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from time import perf_counter

from ..errors import ReviewError
from .contracts import REVIEW_SCHEMA, COMPARISON_SCHEMA, validate_payload

ENDPOINT = "bedrock-runtime:Converse"
DEFAULT_ROLES = ("scientific", "methods", "computational", "novelty", "reviewer2", "reproducibility")
SUPPORTED_ROLES = DEFAULT_ROLES + ("statistics", "clinical", "editor", "strategist")


# Bedrock tool schemas accept a deliberately limited JSON Schema subset across
# Anthropic model versions. Keep the full local contract for post-response
# validation, but normalize the schema sent to Bedrock.
_UNSUPPORTED_SCHEMA_KEYS = {
    "minLength", "maxLength", "pattern",
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
    "maxItems", "uniqueItems",
}


def _nullable_variant(value):
    if not isinstance(value, dict):
        return None
    variants = value.get("anyOf")
    if not isinstance(variants, list) or len(variants) != 2:
        return None
    nulls = [item for item in variants
             if isinstance(item, dict) and item.get("type") == "null"]
    non_nulls = [item for item in variants
                 if not (isinstance(item, dict) and item.get("type") == "null")]
    return non_nulls[0] if len(nulls) == 1 and len(non_nulls) == 1 else None


def _bedrock_schema(value):
    if isinstance(value, dict):
        nullable = _nullable_variant(value)
        if nullable is not None:
            return _bedrock_schema(nullable)

        nullable_properties = set()
        properties = value.get("properties")
        if isinstance(properties, dict):
            nullable_properties = {
                name for name, child in properties.items()
                if _nullable_variant(child) is not None
            }

        result = {}
        for key, child in value.items():
            if key in _UNSUPPORTED_SCHEMA_KEYS:
                continue
            if key == "minItems" and child not in (0, 1):
                continue
            if key == "required" and isinstance(child, list):
                required = [name for name in child if name not in nullable_properties]
                if required:
                    result[key] = required
                continue
            result[key] = _bedrock_schema(child)
        return result
    if isinstance(value, list):
        return [_bedrock_schema(item) for item in value]
    return value


@dataclass(frozen=True)
class BedrockSettings:
    model: str
    region: str = None
    temperature: float = None
    reasoning_effort: str = None
    json_mode: str = "tool"
    max_output_tokens: int = 6000
    max_request_chars: int = 240000
    timeout_seconds: float = 60

    def validate(self):
        if not isinstance(self.model, str) or not self.model.strip():
            raise ReviewError("LLM mode requires --model or MANUSCRIPT_REVIEW_MODEL; no model is selected automatically.")
        if not isinstance(self.region, str) or not self.region.strip():
            raise ReviewError(
                "Bedrock requires an explicit AWS region via --region, MANUSCRIPT_REVIEW_AWS_REGION, "
                "AWS_REGION, or AWS_DEFAULT_REGION.")
        if self.temperature is not None and (
                not math.isfinite(self.temperature) or not 0 <= self.temperature <= 1):
            raise ReviewError("Bedrock Converse temperature must be finite and between 0 and 1.")
        if self.reasoning_effort not in (None, "none", "low", "medium", "high", "xhigh"):
            raise ReviewError("Bedrock reasoning effort must be none, low, medium, high, or xhigh.")
        if self.temperature is not None and self.reasoning_effort not in (None, "none"):
            raise ReviewError("Do not combine temperature with non-none reasoning effort.")
        if self.json_mode not in ("tool", "prompt"):
            raise ReviewError("Bedrock JSON mode must be tool or prompt.")
        if self.json_mode == "tool" and self.reasoning_effort not in (None, "none"):
            raise ReviewError(
                "Bedrock forced tool mode cannot be combined with reasoning effort. "
                "Use --bedrock-json-mode prompt to use reasoning effort.")
        if type(self.max_output_tokens) is not int or not 256 <= self.max_output_tokens <= 32000:
            raise ReviewError("max_output_tokens must be between 256 and 32000.")
        if type(self.max_request_chars) is not int or not 1000 <= self.max_request_chars <= 2000000:
            raise ReviewError("max_request_chars must be between 1000 and 2000000.")
        if not math.isfinite(self.timeout_seconds) or not 1 <= self.timeout_seconds <= 300:
            raise ReviewError("Bedrock timeout must be between 1 and 300 seconds.")


def _converse(body, timeout, region):
    """Invoke Bedrock using the standard boto3 credential/provider chain."""
    try:
        import boto3
        from botocore.config import Config
        from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError, NoRegionError
    except ImportError:
        raise ReviewError(
            'Bedrock live mode needs boto3 on Python 3.10+: pip install -e ".[bedrock]". '
            "Dry runs do not require boto3.") from None
    try:
        config = Config(
            connect_timeout=timeout,
            read_timeout=timeout,
            retries={"total_max_attempts": 1, "mode": "standard"},
        )
        client = boto3.client("bedrock-runtime", region_name=region or None, config=config)
        return client.converse(**body)
    except NoCredentialsError:
        raise ReviewError(
            "Bedrock credentials were not available through the standard AWS credential chain. "
            "Authenticate with your approved AWS/SSO workflow; do not put access keys in this project.") from None
    except NoRegionError:
        raise ReviewError(
            "No AWS region is configured. Use --region, MANUSCRIPT_REVIEW_AWS_REGION, "
            "AWS_REGION, AWS_DEFAULT_REGION, or your AWS profile configuration.") from None
    except ClientError as exc:
        code = (getattr(exc, "response", {}) or {}).get("Error", {}).get("Code", "AWS error")
        raise ReviewError(
            "Bedrock request failed (%s). Check model access, region, IAM permission, model/inference-profile ID, "
            "and whether the selected model supports Converse structured output. No automatic retry was made." % code
        ) from None
    except BotoCoreError:
        raise ReviewError("Bedrock connection or AWS configuration failed. No automatic retry was made.") from None
    except (TimeoutError, OSError):
        raise ReviewError("Bedrock connection failed or timed out. No automatic retry was made.") from None


def _normalized_usage(value):
    if not isinstance(value, dict):
        return {}
    mapping = {
        "inputTokens": "input_tokens",
        "outputTokens": "output_tokens",
        "totalTokens": "total_tokens",
    }
    return {target: value[source] for source, target in mapping.items()
            if type(value.get(source)) is int and value[source] >= 0}


class BedrockReviewer:
    name = "bedrock"
    contract_version = 2

    def __init__(self, settings, dry_run=False, roles=None, transport=None):
        settings.validate()
        self.settings = settings
        self.dry_run = dry_run
        self.roles = tuple(roles or DEFAULT_ROLES)
        if not self.roles or len(set(self.roles)) != len(self.roles) or set(self.roles) - set(SUPPORTED_ROLES):
            raise ReviewError("LLM roles must be unique supported reviewer names.")
        self._transport = transport or (lambda body, timeout: _converse(body, timeout, self.settings.region))
        self.requests = []
        self.receipts = []
        self.calls = []

    def prepare(self, role, packet, schema=REVIEW_SCHEMA):
        source_data = {k: v for k, v in packet.items() if k != "instructions"}
        outbound_schema = _bedrock_schema(schema)
        inference = {"maxTokens": self.settings.max_output_tokens}
        if self.settings.temperature is not None:
            inference["temperature"] = self.settings.temperature

        instructions = packet["instructions"]
        body = {
            "modelId": self.settings.model,
            "system": [{"text": instructions}],
            "messages": [{"role": "user", "content": [{
                "text": json.dumps(source_data, ensure_ascii=False, sort_keys=True)
            }]}],
            "inferenceConfig": inference,
        }
        if self.settings.json_mode == "tool":
            tool_name = "manuscript_" + role
            body["toolConfig"] = {
                "tools": [{"toolSpec": {
                    "name": tool_name,
                    "description": "Return the structured manuscript review.",
                    "inputSchema": {"json": outbound_schema},
                }}],
                "toolChoice": {"tool": {"name": tool_name}},
            }
        else:
            schema_text = json.dumps(
                outbound_schema, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            body["system"] = [{"text": (
                instructions
                + "\n\nReturn exactly one JSON object matching this schema. "
                  "Do not wrap it in Markdown or add commentary.\n"
                + schema_text
            )}]
            if self.settings.reasoning_effort not in (None, "none"):
                body["outputConfig"] = {"effort": self.settings.reasoning_effort}
        encoded = json.dumps(body, ensure_ascii=False, allow_nan=False)
        if len(encoded) > self.settings.max_request_chars:
            raise ReviewError(
                "Request exceeds --max-request-chars. No text was silently truncated; "
                "supply a smaller document or explicitly raise the limit.")
        return body

    def _execute(self, role, packet, schema, empty):
        body = self.prepare(role, packet, schema)
        digest_input = {"endpoint": ENDPOINT, "region": self.settings.region, "body": body}
        digest = sha256(json.dumps(
            digest_input, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        self.requests.append({
            "role": role,
            "endpoint": ENDPOINT,
            "region": self.settings.region,
            "body": body,
            "sha256": digest,
            "contains_manuscript_text": True,
        })
        if self.dry_run:
            return empty

        call = {
            "role": role,
            "request_sha256": digest,
            "input_characters": len(body["messages"][0]["content"][0]["text"]),
            "request_bytes": len(json.dumps(body, ensure_ascii=False).encode("utf-8")),
            "status": "transport_error",
            "raw_findings": None,
        }
        self.calls.append(call)
        started = perf_counter()
        try:
            response = self._transport(body, self.settings.timeout_seconds)
        except ReviewError:
            raise
        except Exception:
            raise ReviewError(
                "Provider transport failed; details suppressed to protect manuscript text and credentials.") from None
        finally:
            call["elapsed_seconds"] = round(perf_counter() - started, 4)

        if isinstance(response, dict):
            usage = _normalized_usage(response.get("usage"))
            self.receipts.append({
                "role": role,
                "model": self.settings.model,
                "usage": usage,
                "request_sha256": digest,
                "stop_reason": response.get("stopReason"),
            })

        call["status"] = "provider_incomplete"
        if not isinstance(response, dict):
            raise ReviewError("Bedrock returned an invalid response envelope.")
        stop_reason = response.get("stopReason")
        if stop_reason in ("guardrail_intervened", "content_filtered"):
            call["status"] = "refused"
            raise ReviewError("Bedrock declined or filtered the request; no generated findings were accepted.")
        allowed_stops = ("tool_use", "end_turn", "stop_sequence") \
            if self.settings.json_mode == "tool" else ("end_turn", "stop_sequence")
        if stop_reason not in allowed_stops:
            raise ReviewError(
                "Bedrock response was not completed (possibly output/context limit); it was not accepted.")

        call["status"] = "invalid_response"
        message = response.get("output", {}).get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, list):
            raise ReviewError("Bedrock response has no valid message content.")

        if self.settings.json_mode == "tool":
            tool_inputs = [
                item["toolUse"].get("input")
                for item in content
                if isinstance(item, dict) and isinstance(item.get("toolUse"), dict)
                and isinstance(item["toolUse"].get("input"), dict)
            ]
            if not tool_inputs:
                raise ReviewError("Bedrock response contained no tool output.")
            payload = tool_inputs[0]
        else:
            texts = [item.get("text", "") for item in content
                     if isinstance(item, dict) and isinstance(item.get("text"), str)]
            if not texts:
                raise ReviewError("Bedrock response contained no text output.")
            try:
                payload = json.loads("".join(texts))
            except (ValueError, TypeError):
                raise ReviewError(
                    "Bedrock output was not valid JSON; no generated findings were accepted.") from None

        if isinstance(payload, dict) and isinstance(payload.get("findings"), list):
            call["raw_findings"] = len(payload["findings"])
        elif schema is COMPARISON_SCHEMA:
            call["raw_findings"] = 0
        call["status"] = "schema_rejected"
        validate_payload(payload, schema)
        call["status"] = "schema_accepted"
        return payload

    def review(self, role, packet):
        return self._execute(
            role, packet, REVIEW_SCHEMA,
            {"findings": [], "claims": [], "strengths": [], "limitations": []})

    def compare(self, packet):
        return self._execute(
            "comparison", packet, COMPARISON_SCHEMA,
            {"assessments": [], "limitations": []})

    def metadata(self):
        from ..diagnostics import usage_totals
        return {
            "provider": self.name,
            "dry_run": self.dry_run,
            "settings": asdict(self.settings),
            "roles": list(self.roles),
            "request_count": len(self.requests),
            "attempted_calls": len(self.calls),
            "completed_calls": sum(c["status"] == "schema_accepted" for c in self.calls),
            "receipts": self.receipts,
            "calls": self.calls,
            "usage": usage_totals(self.receipts, len(self.calls)),
            "web_retrieval": False,
            "store": None,
            "json_mode": self.settings.json_mode,
            "note": (
                "Uses the standard AWS credential chain; credentials are never serialized into review artifacts. "
                "The Bedrock tool mode uses one forced schema tool only to obtain structured output; it enables no "
                "external actions or retrieval. Provider data handling is governed by the configured AWS account and "
                "Amazon Bedrock service."
            ),
        }
