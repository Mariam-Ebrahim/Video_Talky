import json
import re

from langchain_classic.output_parsers import StructuredOutputParser
from langchain_core.exceptions import OutputParserException

from core.llm_client import LLMError, ask


class BadFormatError(LLMError):
    """The model answered, but not in the format we asked for."""


def _find_json(reply):
    """Return the JSON object inside a model reply as a dict, or None."""
    fenced = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", reply, re.DOTALL)
    if fenced:
        text = fenced[-1]
    elif "{" in reply:
        text = reply[reply.find("{"): reply.rfind("}") + 1]
    else:
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def ask_json(system, user, schemas, retries=1, **options):
    """Ask the model for JSON that follows `schemas` (a list of ResponseSchema). Returns a dict."""
    parser = StructuredOutputParser.from_response_schemas(schemas)
    system = (
        f"{system}\n\nReply with one JSON object and nothing else, formatted like this:\n"
        f"{parser.get_format_instructions()}"
    )
    options.setdefault("temperature", 0.0)
    for attempt in range(retries + 1):
        if attempt > 0:
            options["temperature"] = 0.3  # the same prompt at temperature 0 would fail the same way
        data = _find_json(ask(system, user, **options))
        if data is None:
            continue
        try:  # the parser checks that every field of the schema is there
            return parser.parse("```json\n" + json.dumps(data, ensure_ascii=False) + "\n```")
        except OutputParserException:
            continue
    raise BadFormatError("The model answered in the wrong format. Please try again.")