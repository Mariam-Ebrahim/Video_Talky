from core.llm_client import ask, is_online

print("online:", is_online())
print(ask("Answer only in Arabic, in one short sentence.", "What is the capital of France?"))