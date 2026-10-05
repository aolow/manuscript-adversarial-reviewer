"""Conservative heading recognition. Unknown subheadings retain their parent."""
import re

ALIASES = {
    "abstract": "Abstract", "summary": "Abstract",
    "introduction": "Introduction", "background": "Introduction",
    "methods": "Methods", "materials and methods": "Methods",
    "patients and methods": "Methods", "experimental procedures": "Methods",
    "results": "Results", "results and discussion": "Results and Discussion",
    "discussion": "Discussion", "conclusion": "Conclusion", "conclusions": "Conclusion",
    "limitations": "Limitations", "study limitations": "Limitations",
    "data availability": "Data Availability", "data availability statement": "Data Availability",
    "code availability": "Code Availability", "code and data availability": "Availability",
    "data and code availability": "Availability", "availability": "Availability",
    "references": "References", "bibliography": "References",
    "acknowledgments": "Acknowledgments", "acknowledgements": "Acknowledgments",
    "figure legends": "Figure Legends", "figure captions": "Figure Legends",
    "supplementary methods": "Methods", "supplementary results": "Results",
}


def heading(text, styled=False):
    raw = text.strip()
    cleaned = re.sub(r"^#{1,6}\s+", "", raw)
    cleaned = re.sub(r"^\d+(?:\.\d+)*[.)]?\s+", "", cleaned)
    cleaned = cleaned.strip(" *:\t")
    canonical = ALIASES.get(cleaned.lower())
    if canonical:
        return canonical, canonical
    if styled or raw.startswith("#"):
        return cleaned, None
    return None
