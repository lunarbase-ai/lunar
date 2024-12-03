import os

# .env
DOTENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), ".env")

# General
MAX_ANS_TOKENS = 3*10**4

# Tester names
GPT4O_LABEL = 'gpt4o'
LLAMA3_8B_LABEL = 'llama3_8b'
MIXTRAL_8X7B_LABEL = 'mixtral_8x7b'
GEMMA2_9B_LABEL = 'gemma2_9b'

# GPT-4o
GPT4O_OPENAI_API_KEY_ENV = 'OPENAI_API_KEY'
GPT4O_AZURE_ENDPOINT_ENV = 'AZURE_ENDPOINT'
GPT4O_MODEL_NAME = "gpt-4o"
GPT4O_TEMPERATURE = 1e-16
GPT4O_API_TYPE = "azure"
GPT4O_API_VERSION = "2024-02-01"
GPT4O_DEPLOYMENT_NAME = "lunar-chatgpt-4o"
GPT4O_TOP_P = 1e-16
GPT4O_SEED = 1234
GPT4O_MODEL_KWARGS = {'top_p': GPT4O_TOP_P, 'seed': GPT4O_SEED}
GPT4O_PYTHON_PATTERN = pattern = r'```python\n(.*)```'

# Llama3 8B
LLAMA3_8B_DOTENV = os.path.join(os.path.dirname(__file__), '.env')
LLAMA3_8B_HF_ID = 'meta-llama/Meta-Llama-3-8B-Instruct'
LLAMA3_8B_TEMPERATURE = 1e-16
LLAMA3_8B_TOP_P = 1e-16
LLAMA3_8B_PYTHON_PATTERN = r'```\n(.*)```'

# Mixtral 8x7B
MIXTRAL_8X7B_DOTENV = os.path.join(os.path.dirname(__file__), '.env')
MIXTRAL_8X7B_HF_ID = 'mistralai/Mixtral-8x7B-Instruct-v0.1'
MIXTRAL_8X7B_TEMPERATURE = 1e-16
MIXTRAL_8X7B_TOP_P = 1e-16
MIXTRAL_8X7B_PYTHON_PATTERN = r'```\n(.*)```'

# Llama3 8B
GEMMA2_9B_DOTENV = os.path.join(os.path.dirname(__file__), '.env')
GEMMA2_9B_HF_ID = 'google/gemma-2-9b-it'
GEMMA2_9B_TEMPERATURE = 1e-16
GEMMA2_9B_TOP_P = 1e-16
GEMMA2_9B_PYTHON_PATTERN = r'```\n(.*)```'

# prompts
BASELINE_PROMPT_TEMPLATE = """You are a Python programmer.
Generate a Python program that solves the task below.
Use print(output) for output in the program.
The list of files provided below may be used by the program.
Answer with only the code.

TASK: {{task}}

AVAILABLE FILES:
{{files}}
"""
BASELINE_PROMPT_TEMPLATE_FORMAT = 'jinja2'
FILE_PROMPT_TEMPLATE = '{description}: {path}'