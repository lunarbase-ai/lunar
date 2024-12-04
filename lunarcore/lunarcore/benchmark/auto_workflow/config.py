# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Simon Ljungbeck <simon.ljungbeck@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from dotenv import load_dotenv
import os


# .env path
DOTENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), ".env")
load_dotenv(DOTENV_PATH)

# Directory and file names Paths to directories and files for tests
TESTS_DIR = 'tests'
TEMPLATE_JSON_FILE = '{name}.json'
FILES_DIR = 'files'

# Keys of the test JSON file in each test directory
JSON_DESCRIPTION_KEY = 'description'
JSON_EXPECTED_OUTPUTS_KEY = 'expected_outputs'
JSON_EVALUATION_METHOD_KEY = 'evaluation_method'
JSON_EVALUATION_METHOD_DATA_KEY = 'evaluation_method_data'
JSON_EVALUATION_DATA_KEY = 'evaluation_data'
JSON_FILES_KEY = 'files'
JSON_FILES_NAME_KEY = 'name'
JSON_FILES_DESCRIPTION_KEY = 'description'
JSON_TEST_LEVELS = 'evaluation_levels'
JSON_TEST_LEVEL_COMPONENTS = 'components'
JSON_TEST_LEVEL_CUSTOM_COMPONENTS = 'custom_components'
JSON_TEST_LEVEL_FILES = 'input_files'
JSON_TEST_LEVEL_SPECIALIZATION = 'specialization'
JSON_TEST_LEVEL_SPECIFICITY = 'specificity'
JSON_TEST_LEVEL_KB_COMPONENTS = 'kb_components'
JSON_TEST_LEVEL_INTENT_LENGTH = 'intent_word_length'
JSON_TEST_LEVEL_INTENT_LENGTH_DIV = 5
JSON_TEST_LABELS = 'evaluation_labels'

# Evaluation methods
DETERMINISTIC_EVALUATION_METHOD = 'deterministic'
CODE_EVALUATION_METHOD = 'code'
LLM_EVALUATION_METHOD = 'llm'
EVALUATION_METHODS = [
   DETERMINISTIC_EVALUATION_METHOD,
   CODE_EVALUATION_METHOD,
   LLM_EVALUATION_METHOD,
]
DEFAULT_EVALUATION_METHOD = DETERMINISTIC_EVALUATION_METHOD

# Keys of the EvaluationRecord stats data structure
EVALUATION_EXECUTION_FINISHES_KEY = 'execution_finishes'
EVALUATION_CORRECTS_KEY = 'corrects'
EVALUATION_TOTAL_KEY = 'total'

# Intended for test template creator script
ARGS_TESTNAME_KEY = 'name'
ARGS_DESCRIPTION_KEY = 'description'
ARGS_OUTPUT_KEY = 'outputs'
ARGS_EVALUATION_METHOD_KEY = 'evaluation_method'
ARGS_FILES_KEY = 'files'
ARGS_FILE_DESCRIPTIONS_KEY = 'file_descriptions'
ARGS_LEVEL_NAMES_KEY = 'level_names'
ARGS_LEVELS_KEY = 'levels'
ARGS_TESTLABELS_KEY = 'labels'

# Evaluation string templates
EVALUATION_RECORD_STR_TEMPLATE = """{tests_outputs}
========
Total ratio correct: {nr_correct}/{total} ({frac_correct:.2f})
Total ratio execution finishes: {nr_execution_finishes}/{total} ({frac_execution_finishes:.2f})
Ratio correct per group:
{group_stats_str}
========"""
EVALUATION_RECORD_GROUP_STATS_STR = """-{group_name}:
   Ratio correct: {nr_correct}/{total} ({frac_correct:.2f})
   Ratio execution finishes: {nr_execution_finishes}/{total} ({frac_execution_finishes:.2f})"""
OUTPUTS_RECORD_STR = """Test name: {test_name}
-Workflow output: {workflow_outputs}
-Evaluation data: {evaluation_data}
-Result correct: {is_correct}
-Execution finished: {execution_finished}"""

# AutoworkflowTester __str__
MAX_LEN_EXPECTED_OUTPUT = 100

# plot library
RESULTS_DIRECTORY = os.path.join(os.path.dirname(__file__), 'results')
DATASET_STATS_DIR = os.path.join(RESULTS_DIRECTORY, 'dataset_stats')
PLOTS_DIRECTORY_TEMPLATE = os.path.join(RESULTS_DIRECTORY, '{tester_name}', 'plots')
HISTOGRAM_WORKFLOW_LENGTHS_FILE = 'workflow_lenghts_histogram.png'
HISTOGRAM_INTENT_CHARS_FILE = 'intent_chars_histogram.png'
HISTOGRAM_INTENT_WORDS_FILE = 'intent_words_histogram.png'
HISTOGRAM_KB_COMPONENTS_FILE = 'knowledge_base_components_histogram.png'
HISTOGRAM_CUSTOM_COMPONENTS_FILE = 'custom_components_histogram.png'
LINE_CHART_LEVELS_FILE_TEMPLATE = '{level_name}_line_chart.png'
SCATTER_3D_LEVELS_FILE_TEMPLATE = '{frac_type}_{level_name1}_{level_name2}_scatter.png'

# label representation of level
LEVEL2LABEL_TEMPLATE = '{level_name}_{level}'

# Logger files
LOGGER_FILE_TEST_EXECUTOR_TEMPLATE = os.path.join(RESULTS_DIRECTORY, '{tester_name}', 'test_executor.log')
LOGGER_FILE_TESTER_TEMPLATE = os.path.join(os.path.dirname(__file__), RESULTS_DIRECTORY, '{tester_name}', 'tester.log')

# Azure OpenAI API parameters
OPENAI_MODEL_NAME = "gpt-4o"
OPENAI_TEMPERATURE = 1e-16
OPENAI_API_TYPE = "azure"
OPENAI_TOP_P = 1e-16
OPENAI_SEED = 1234
OPENAI_MODEL_KWARGS = {"top_p": OPENAI_TOP_P, "seed": OPENAI_SEED}
OPENAI_API_VERSION = os.getenv('PYTHON_CODER_OPENAI_API_VERSION')
OPENAI_DEPLOYMENT_NAME = os.getenv('AZURE_DEPLOYMENT')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')
