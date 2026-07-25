import os

# Garante que a app e os settings possam ser importados nos testes sem depender
# de um arquivo .env local, fornecendo credenciais de LLM fictícias.
os.environ.setdefault("LLM_API_KEY", "test-key")
os.environ.setdefault("LLM_MODEL", "test-model")
