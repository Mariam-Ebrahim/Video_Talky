"""make_quiz(avoid=...) tells the model about earlier questions. Runs without a real LLM."""
import sys
from unittest.mock import MagicMock

# the libraries below are only needed to import core.quiz; the model call is replaced by a fake
for name in ["langchain_classic", "langchain_classic.output_parsers", "langchain_core", "langchain_core.exceptions",
             "langchain_core.language_models", "langchain_core.language_models.llms", "langchain_core.callbacks",
             "requests", "dotenv"]:
    try:
        __import__(name)
    except ImportError:
        sys.modules[name] = MagicMock()
if isinstance(sys.modules.get("langchain_core.exceptions"), MagicMock):
    sys.modules["langchain_core.exceptions"].OutputParserException = type("OutputParserException", (Exception,), {})

import core.quiz as quiz

prompts = []


def fake_ask_json_batch(system, users, schemas, max_new_tokens):
    results = []
    for user in users:
        prompts.append(user)
        results.append({"question": f"Q{len(prompts)}?", "option_a": "a", "option_b": "b", "option_c": "c",
                        "option_d": "d", "answer": "A", "explanation": "x"})
    return results


quiz.ask_json_batch = fake_ask_json_batch
SECTIONS = [{"start": 0, "end": 10, "title": "t"}, {"start": 10, "end": 20, "title": "t"}]
SNIPPETS = [{"start": 1, "text": "hello"}, {"start": 11, "text": "world"}]

result = quiz.make_quiz(SECTIONS, SNIPPETS, "en", count=4, avoid=["OLD1?", "OLD2?"])
assert len(result) == 4
assert all("OLD1?" in p and "OLD2?" in p for p in prompts), "earlier quizzes' questions must reach every prompt"
assert "Write question 1 " in prompts[0] and "Write question 2 " in prompts[1], "same-section questions get different focus hints"

prompts.clear()
quiz.make_quiz(SECTIONS, SNIPPETS, "en", count=2)
assert not any("OLD1?" in p for p in prompts), "without avoid, nothing extra is added"
print("quiz avoid OK")