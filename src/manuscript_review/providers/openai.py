"""Small OpenAI Responses REST adapter. No SDK, tools, uploads, or implicit calls."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
import os
from time import perf_counter
from urllib import error, request

from ..errors import ReviewError
from .contracts import (REVIEW_SCHEMA, COMPARISON_SCHEMA, REVIEW_ENVELOPE_SCHEMA,
                        COMPARISON_ENVELOPE_SCHEMA, validate_payload)

ENDPOINT = "https://api.openai.com/v1/responses"
DEFAULT_ROLES = ("scientific", "methods", "computational", "novelty", "reviewer2", "reproducibility")
SUPPORTED_ROLES = DEFAULT_ROLES + ("statistics", "clinical", "editor", "strategist")


@dataclass(frozen=True)
class OpenAISettings:
    model: str
    temperature: float = None
    reasoning_effort: str = None
    max_output_tokens: int = 6000
    max_request_chars: int = 240000
    timeout_seconds: float = 60

    def validate(self):
        if not isinstance(self.model, str) or not self.model.strip():
            raise ReviewError("LLM mode requires --model or MANUSCRIPT_REVIEW_MODEL; no model is selected automatically.")
        if self.temperature is not None and (
                not math.isfinite(self.temperature) or not 0 <= self.temperature <= 2):
            raise ReviewError("Temperature must be finite and between 0 and 2.")
        if self.reasoning_effort not in (None, "none", "minimal", "low", "medium", "high", "xhigh"):
            raise ReviewError("Unsupported reasoning effort name.")
        if self.temperature is not None and self.reasoning_effort not in (None, "none"):
            raise ReviewError("Do not combine temperature with non-none reasoning effort.")
        if type(self.max_output_tokens) is not int or not 256 <= self.max_output_tokens <= 32000:
            raise ReviewError("max_output_tokens must be between 256 and 32000.")
        if type(self.max_request_chars) is not int or not 1000 <= self.max_request_chars <= 2000000:
            raise ReviewError("max_request_chars must be between 1000 and 2000000.")
        if not math.isfinite(self.timeout_seconds) or not 1 <= self.timeout_seconds <= 60:
            raise ReviewError("Timeout must be between 1 and 60 seconds.")


class NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ReviewError("Provider redirect refused; no credentials were forwarded.")


def _post(body, timeout):
    # Credentials are read only here, from the process environment, and never serialized.
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        raise ReviewError("OPENAI_API_KEY is required for live --llm runs; use --dry-run to export locally.")
    data = json.dumps(body, ensure_ascii=False, allow_nan=False).encode("utf-8")
    req = request.Request(ENDPOINT, data=data, method="POST",
                          headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with request.build_opener(NoRedirect()).open(req, timeout=timeout) as response:
            raw = response.read(8_000_001)
            if len(raw) > 8_000_000:
                raise ReviewError("Provider response exceeded the local response-size limit.")
        return json.loads(raw)
    except error.HTTPError as exc:
        # Provider error bodies may echo input. Never print them or authorization headers.
        raise ReviewError("OpenAI HTTP %d. Check account access, quota, model and supported settings. "
                          "No automatic retry was made." % exc.code) from None
    except (error.URLError, TimeoutError, OSError):
        raise ReviewError("OpenAI connection failed or timed out. No automatic retry was made.") from None
    except (ValueError, UnicodeError):
        raise ReviewError("OpenAI returned an invalid JSON response.") from None


class OpenAIReviewer:
    name = "openai"
    contract_version = 2

    def __init__(self, settings, dry_run=False, roles=None, transport=None):
        settings.validate()
        self.settings = settings
        self.dry_run = dry_run
        self.roles = tuple(roles or DEFAULT_ROLES)
        if not self.roles or len(set(self.roles)) != len(self.roles) or set(self.roles) - set(SUPPORTED_ROLES):
            raise ReviewError("LLM roles must be unique supported reviewer names.")
        self._transport = transport or _post
        self.requests = []
        self.receipts = []
        self.calls = []
        if not dry_run and transport is None and not os.environ.get("OPENAI_API_KEY", "").strip():
            raise ReviewError("OPENAI_API_KEY is required for live --llm runs; --dry-run needs no key.")

    def prepare(self, role, packet, schema=REVIEW_SCHEMA):
        # A static packet per role makes dry-run bytes identical to live request bytes.
        source_data = {k: v for k, v in packet.items() if k != "instructions"}
        body = {
            "model": self.settings.model,
            "instructions": packet["instructions"],
            "input": [{"role": "user", "content": json.dumps(source_data, ensure_ascii=False, sort_keys=True)}],
            "text": {"format": {"type": "json_schema", "name": "manuscript_" + role,
                                "strict": True, "schema": schema}},
            "max_output_tokens": self.settings.max_output_tokens,
            "store": False, "truncation": "disabled",
        }
        if self.settings.temperature is not None:
            body["temperature"] = self.settings.temperature
        if self.settings.reasoning_effort is not None:
            body["reasoning"] = {"effort": self.settings.reasoning_effort}
        encoded = json.dumps(body, ensure_ascii=False, allow_nan=False)
        if len(encoded) > self.settings.max_request_chars:
            raise ReviewError("Request exceeds --max-request-chars. No text was silently truncated; "
                              "supply a smaller document or explicitly raise the limit.")
        return body

    def _execute(self, role, packet, schema, empty):
        body = self.prepare(role, packet, schema)
        digest = sha256(json.dumps(body, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        self.requests.append({"role": role, "endpoint": ENDPOINT, "body": body,
                              "sha256": digest, "contains_manuscript_text": True})
        if self.dry_run:
            return empty
        call = {"role": role, "request_sha256": digest,
                "input_characters": len(body["input"][0]["content"]),
                "request_bytes": len(json.dumps(body, ensure_ascii=False).encode("utf-8")),
                "status": "transport_error", "raw_findings": None, "schema_error": None}
        self.calls.append(call)
        started = perf_counter()
        try:
            response = self._transport(body, self.settings.timeout_seconds)
        except ReviewError:
            raise
        except Exception:
            raise ReviewError("Provider transport failed; details suppressed to protect manuscript text and credentials.") from None
        finally:
            call["elapsed_seconds"] = round(perf_counter() - started, 4)
        if isinstance(response, dict):
            from ..diagnostics import safe_usage
            self.receipts.append({"role": role, "response_id": response.get("id"),
                                  "model": response.get("model", self.settings.model),
                                  "usage": safe_usage(response.get("usage")), "request_sha256": digest})
        call["status"] = "provider_incomplete"
        if not isinstance(response, dict) or response.get("status") != "completed":
            raise ReviewError("Provider response was not completed (possibly output limit or refusal); it was not accepted.")
        call["status"] = "invalid_response"
        texts = []
        output = response.get("output")
        if not isinstance(output, list):
            raise ReviewError("Provider response has no valid output list.")
        for item in output:
            if not isinstance(item, dict) or item.get("type") != "message":
                continue
            if not isinstance(item.get("content"), list):
                raise ReviewError("Provider response has malformed message content.")
            for content in item["content"]:
                if not isinstance(content, dict):
                    raise ReviewError("Provider response has malformed content.")
                if content.get("type") == "refusal":
                    call["status"] = "refused"
                    raise ReviewError("Provider declined the request; no generated findings were accepted.")
                if content.get("type") == "output_text":
                    texts.append(content.get("text", ""))
        try:
            payload = json.loads("".join(texts))
        except (ValueError, TypeError):
            raise ReviewError("Provider output was not valid JSON; no generated findings were accepted.") from None
        if isinstance(payload, dict) and isinstance(payload.get("findings"), list):
            call["raw_findings"] = len(payload["findings"])
        elif schema is COMPARISON_SCHEMA:
            call["raw_findings"] = 0
        call["status"] = "schema_rejected"
        local_schema = (REVIEW_ENVELOPE_SCHEMA if schema is REVIEW_SCHEMA
                        else COMPARISON_ENVELOPE_SCHEMA if schema is COMPARISON_SCHEMA else schema)
        try:
            validate_payload(payload, local_schema)
        except ReviewError as exc:
            path = getattr(exc, "schema_path", None)
            validator = getattr(exc, "schema_validator", None)
            if path is not None and validator is not None:
                call["schema_error"] = {"path": path, "validator": validator}
            raise
        call["status"] = "schema_accepted"
        return payload

    def review(self, role, packet):
        return self._execute(role, packet, REVIEW_SCHEMA,
                             {"findings": [], "claims": [], "strengths": [], "limitations": []})

    def compare(self, packet):
        return self._execute("comparison", packet, COMPARISON_SCHEMA,
                             {"assessments": [], "limitations": []})

    def metadata(self):
        from ..diagnostics import usage_totals
        return {"provider": self.name, "dry_run": self.dry_run, "settings": asdict(self.settings),
                "roles": list(self.roles), "request_count": len(self.requests),
                "attempted_calls": len(self.calls),
                "completed_calls": sum(c["status"] == "schema_accepted" for c in self.calls),
                "receipts": self.receipts, "calls": self.calls,
                "usage": usage_totals(self.receipts, len(self.calls)),
                "web_retrieval": False, "store": False,
                "note": "store=false is an API setting, not a promise of zero provider retention. No tools are enabled."}
