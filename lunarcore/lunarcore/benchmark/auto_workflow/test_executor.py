# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Simon Ljungbeck <simon.ljungbeck@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import logging
import warnings

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from typing import Dict, List

from lunarcore.benchmark.auto_workflow.config import (
    DOTENV_PATH,
    JSON_DESCRIPTION_KEY,
    JSON_EXPECTED_OUTPUTS_KEY,
    DETERMINISTIC_EVALUATION_METHOD,
    LLM_EVALUATION_METHOD,
    JSON_FILES_KEY,
    JSON_EVALUATION_DATA_KEY,
    JSON_EVALUATION_METHOD_KEY,
    JSON_EVALUATION_METHOD_DATA_KEY,
    JSON_TEST_LEVELS,
    JSON_TEST_LEVEL_COMPONENTS,
    JSON_TEST_LEVEL_CUSTOM_COMPONENTS,
    JSON_TEST_LEVEL_KB_COMPONENTS,
    JSON_TEST_LEVEL_INTENT_LENGTH,
    JSON_TEST_LEVEL_INTENT_LENGTH_DIV,
    JSON_TEST_LEVEL_SPECIALIZATION,
    JSON_TEST_LEVEL_SPECIFICITY,
    JSON_TEST_LABELS,
    LOGGER_FILE_TEST_EXECUTOR_TEMPLATE,
    PLOTS_DIRECTORY_TEMPLATE,
    OPENAI_MODEL_NAME,
    OPENAI_TEMPERATURE,
    OPENAI_API_TYPE,
    OPENAI_TOP_P,
    OPENAI_SEED,
    OPENAI_MODEL_KWARGS,
    OPENAI_API_VERSION,
    OPENAI_DEPLOYMENT_NAME,
    OPENAI_API_KEY,
    AZURE_ENDPOINT,
)
from lunarcore.benchmark.auto_workflow.autoworkflow_tester.auto_workflow_tester import AutoworkflowTester
from lunarcore.benchmark.auto_workflow.baseline_testers.gpt4o_tester import GPT4oTester
from lunarcore.benchmark.auto_workflow.baseline_testers.llama3_8b_tester import Llama3_8B
from lunarcore.benchmark.auto_workflow.baseline_testers.mixtral_8x7b_tester import Mixtral_8x7B
from lunarcore.benchmark.auto_workflow.baseline_testers.gemma2_9b_tester import Gemma2_9B
from lunarcore.benchmark.auto_workflow.dataset import Dataset
from lunarcore.benchmark.auto_workflow.evaluation_record import EvaluationRecord
from lunarcore.benchmark.auto_workflow.tester import Tester
from lunarcore.benchmark.auto_workflow.utils import (
    empty_file,
)


class TestExecutor():
    def __init__(self, tester: Tester, dataset: Dataset, logger: logging.Logger = None):
        self.tester = tester
        self.dataset = dataset
        self.logger = logger or self._init_logger()

    def _init_logger(self):
        tester_name = self.tester.tester_name
        if not tester_name:
            warnings.warn('Cannot find Tester name. Creating logfile in results directory!')
        logger = logging.getLogger(f'{__name__}@{tester_name}')
        logger.setLevel(logging.DEBUG)
        logger_file_path = LOGGER_FILE_TEST_EXECUTOR_TEMPLATE.format(
            tester_name = tester_name
        )
        empty_file(logger_file_path)
        file_handler = logging.FileHandler(logger_file_path)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        # stream_handler = logging.StreamHandler(sys.stdout)
        # logger.addHandler(stream_handler)
        return logger

    def _outputs_same(self, outputs1: List, outputs2: List):
        if len(outputs1) != len(outputs2):
            return False
        for output in outputs1:
            if output not in outputs2:
                return False
        return True

    def _create_client(self):
        client = AzureChatOpenAI(
            model_name=OPENAI_MODEL_NAME,
            temperature=OPENAI_TEMPERATURE,
            openai_api_type=OPENAI_API_TYPE,
            openai_api_version=OPENAI_API_VERSION,
            deployment_name=OPENAI_DEPLOYMENT_NAME,
            openai_api_key=OPENAI_API_KEY,
            azure_endpoint=AZURE_ENDPOINT,
            model_kwargs=OPENAI_MODEL_KWARGS,
        )
        return client

    def _output_llm_evaluation(self, prompt_template_str: str, output):
        prompt_template = PromptTemplate.from_template(
            prompt_template_str,
            template_format='f-string'
        )
        client = self._create_client()
        chain = prompt_template | client
        chain_results = chain.invoke({'output': output})
        result_text = chain_results.content
        return result_text

    def _evaluate_outputs(self, test_name: str, evaluation_record: EvaluationRecord, test_data: Dict, workflow_outputs: List):
        evaluation_data = test_data[JSON_EVALUATION_DATA_KEY]
        evaluation_method = evaluation_data[JSON_EVALUATION_METHOD_KEY]
        evaluation_method_data = evaluation_data[JSON_EVALUATION_METHOD_DATA_KEY]
        
        if evaluation_method == DETERMINISTIC_EVALUATION_METHOD:
            is_correct = self._outputs_same(
                evaluation_method_data['expected_outputs'],
                workflow_outputs,
            )
        elif evaluation_method == LLM_EVALUATION_METHOD:
            is_correct = 'yes' in self._output_llm_evaluation(
                evaluation_method_data['prompt_template'],
                workflow_outputs
            ).lower()
        else:
            raise ValueError(f"Evaluation method '{evaluation_method}' for test '{test_name}' is not valid.")

        evaluation_record.register_result(
            test_name,
            test_data[JSON_TEST_LABELS],
            workflow_outputs,
            is_correct,
        )

    def run_tests(self):
        evaluation_record = EvaluationRecord()
        for test_nr, (test_name, test_data) in enumerate(self.dataset.test_jsons.items()):
            self.logger.info(f"New test: '{test_name}' (test nr {test_nr+1}/{len(self.dataset.test_jsons)})")
            evaluation_record.register_test(test_name, test_data[JSON_TEST_LEVELS], test_data[JSON_TEST_LABELS], test_data[JSON_EVALUATION_DATA_KEY])
            try:
                intent = test_data[JSON_DESCRIPTION_KEY]
                files_json = test_data[JSON_FILES_KEY]
                files = self.dataset._files_list(test_name, files_json)
                test_outputs = self.tester.run_test(test_name, intent, files)
                self.logger.info(f'Got outputs:\nTest outputs: {test_outputs}\nEvaluation data: {test_data[JSON_EVALUATION_DATA_KEY]}')
                self._evaluate_outputs(test_name, evaluation_record, test_data, test_outputs)
            except Exception as e:
                self.logger.info(f"Test {test_name} crashed. Error: {e}")
            self.logger.info(f'Evaluation stats now:\n{evaluation_record}')
        return evaluation_record


def print_plot_result(evaluation_record: EvaluationRecord, plot_dir: str):
    print(evaluation_record)

    filename = evaluation_record.level_result_line_chart(JSON_TEST_LEVEL_COMPONENTS, 'Performance vs. #components',
                                                         '#Components', xaxis_integers=True, plot_dir=plot_dir)
    print(f'Plotted: {filename}')

    filename = evaluation_record.level_result_line_chart(JSON_TEST_LEVEL_CUSTOM_COMPONENTS, 'Performance vs. #custom components',
                                                         '#Custom components', xaxis_integers=True, plot_dir=plot_dir)
    print(f'Plotted: {filename}')

    filename = evaluation_record.level_result_line_chart(JSON_TEST_LEVEL_KB_COMPONENTS, 'Performance vs. #KB components',
                                                         '#KB components', xaxis_integers=True, plot_dir=plot_dir)
    print(f'Plotted: {filename}')

    filename = evaluation_record.level_result_line_chart(JSON_TEST_LEVEL_INTENT_LENGTH, 'Performance vs. intent length',
                                                         '#Words', xaxis_integers=True, plot_dir=plot_dir,
                                                         xaxis_factor=JSON_TEST_LEVEL_INTENT_LENGTH_DIV)
    print(f'Plotted: {filename}')

    filename = evaluation_record.level_result_line_chart(JSON_TEST_LEVEL_SPECIALIZATION, 'Performance vs. specialization',
                                                         'Specialization level', xaxis_integers=True, plot_dir=plot_dir)
    print(f'Plotted: {filename}')

    filename = evaluation_record.level_result_line_chart(JSON_TEST_LEVEL_SPECIFICITY, 'Performance vs. intent specificity',
                                                         'Specificity level', xaxis_integers=True, plot_dir=plot_dir)
    print(f'Plotted: {filename}')

    filename = evaluation_record.two_levels_3d_scatter(
        JSON_TEST_LEVEL_CUSTOM_COMPONENTS,
        JSON_TEST_LEVEL_KB_COMPONENTS,
        # 'Avg. Component Run (Custom components vs. KB components)',
        'Run Acc. (Custom components vs. KB components)',
        '#Custom components',
        '#KB components',
        True,
        plot_dir
    )
    print(f'Plotted: {filename}')
        
    filename = evaluation_record.two_levels_3d_scatter(
        JSON_TEST_LEVEL_CUSTOM_COMPONENTS,
        JSON_TEST_LEVEL_KB_COMPONENTS,
        # 'Avg. Exec() (Custom components vs. KB components)',
        'Answer Acc. (Custom components vs. KB components)',
        '#Custom components',
        '#KB components',
        False,
        plot_dir
    )
    print(f'Plotted: {filename}')


def tests_str(tests_dir: str = None, include_tests: List[str] = None):
    dataset = Dataset(tests_dir, include_tests)
    return str(dataset)


def pre_test_stats(tests_dir: str = None, include_tests: List[str] = None):
    dataset = Dataset(tests_dir, include_tests)
    print(dataset)
    dataset._pre_test_stats()


def create_training_set(tests_dir: str = None, include_tests: List[str] = None, frac_samples: float = 1/3):
    dataset = Dataset(tests_dir, include_tests)
    training_dataset_names = dataset.random_sample(frac_samples)
    return training_dataset_names


def create_test_set(tests_dir: str = None, training_set: List[str] = None):
    dataset = Dataset(tests_dir, training_set)
    evaluation_dataset_names = dataset.excluded_tests()
    return evaluation_dataset_names
    

def test_autoworkflow(env_path: str = DOTENV_PATH, tests_dir: str = None, include_tests: List[str] = None, save_workflows: bool = True):
    tester = AutoworkflowTester(env_path, save_workflows)
    dataset = Dataset(tests_dir, include_tests)
    test_executor = TestExecutor(tester, dataset)
    evaluation_record = test_executor.run_tests()
    print_plot_result(evaluation_record, PLOTS_DIRECTORY_TEMPLATE.format(tester_name=tester.tester_name))


def test_gpt4o(env_path: str = DOTENV_PATH, tests_dir: str = None, include_tests: List[str] = None):
    tester = GPT4oTester()
    dataset = Dataset(tests_dir, include_tests)
    test_executor = TestExecutor(tester, dataset)
    evaluation_record = test_executor.run_tests()
    print_plot_result(evaluation_record, PLOTS_DIRECTORY_TEMPLATE.format(tester_name=tester.tester_name))


def test_llama3_8b(env_path: str = DOTENV_PATH, tests_dir: str = None, include_tests: List[str] = None):
    tester = Llama3_8B()
    dataset = Dataset(tests_dir, include_tests)
    test_executor = TestExecutor(tester, dataset)
    evaluation_record = test_executor.run_tests()
    print_plot_result(evaluation_record, PLOTS_DIRECTORY_TEMPLATE.format(tester_name=tester.tester_name))


def test_mixtral_8x7b(env_path: str = DOTENV_PATH, tests_dir: str = None, include_tests: List[str] = None):
    tester = Mixtral_8x7B()
    dataset = Dataset(tests_dir, include_tests)
    test_executor = TestExecutor(tester, dataset)
    evaluation_record = test_executor.run_tests()
    print_plot_result(evaluation_record, PLOTS_DIRECTORY_TEMPLATE.format(tester_name=tester.tester_name))

def test_gemma2_9b(env_path: str = DOTENV_PATH, tests_dir: str = None, include_tests: List[str] = None):
    tester = Gemma2_9B()
    dataset = Dataset(tests_dir, include_tests)
    test_executor = TestExecutor(tester, dataset)
    evaluation_record = test_executor.run_tests()
    print_plot_result(evaluation_record, PLOTS_DIRECTORY_TEMPLATE.format(tester_name=tester.tester_name))


if __name__ == "__main__":
    load_dotenv(DOTENV_PATH)

    developer_tests = [  # TRAINING DATASET: 0 = doesn't run;  1 = runs but incorrect;  2 = correct
        'python_execute',                       # 1: just forwards code to pythoncoder, doesn't set result variable
        'reversed_constant_string',             # 2
        'ner_file_persons_hard',                # 2
        'integer_sort_python',                  # 2
        'translate_eng_french',                 # 1: uses LLM for translation, but it outputs more than just the translation
        'integer_sort_r',                       # 0: seems to be something wrong with R coder, but generated R code also wrong (i.e. result label should probably be 1)
        'file_float_rounder',                   # 2
        'matrix_multiplication_determinant',    # 0: crashes because LLM generate python code using pd.compat.StringIO which has been removed from new pandas versions
        'word_count_pdf',                       # 2
        'word_count_zip',                       # 2
        'wikipedia_word1',                      # 2
        'dates_iso_format',                     # 1: 2000-01-13T00:00:00 instead of just date 
        'image_dominant_color',                 # 1: outputs the list [0, 0, 0] instead of a tuple (0, 0, 0)
        'python_syntax_error_correcter',        # 1: uses autopep8 but it fails correcting the syntax error
        'math_expression_image',                # 1: uses pic2text for extracting but then pythoncoder with regex and eval that fails extracting eval str from latex expression string (probably because of \cdot inside)
        'html_scrape_json_urls_status',         # 1: outputs dict {url: "200 OK"} instead of just list [200]
        'csv_genes_wikipedia_sentence1',        # 1: correct, except missing the dot 
        'country_largest_file',                 # 2  (quite impressive -- it uses python coder to request to https://restcountries.com/v3.1/name/)
        'text_sentences2newline',               # 2
        'html_scrape_json_urls',                # 0: pythoncode fails -- json.dumps({input_str}) should be json.dumps("{input_str}")
        'longest_pdf2',                         # 1: outputs "['This is a pdf containing some interesting content. ']" instead of just sentence inside
        'integral_file',                        # 0: computes correct result but returns integral_result.evalf() which is of type <class 'sympy.core.numbers.Float'> so program crashes
        'constant_string',                      # 2
        'ner_file',                             # 2
        'find_urls_file_scrape',                # 1: outputs the output from URL scraper, instead of using property getter to extract only the content. Proposed solution: add example of URL scraper (potentially use the 3 step approach where LLM first chooses potential components and then examples are retrieved of each of those)
        'file_content_searcher',                # 2
        'text_misspelling_file',                # 0: uses a pythoncoder with `from spellchecker import SpellChecker` which works good outside lunar, but fails to import `from indexer import DictionaryIndex` in that package
        'cpp_content',                          # 2
        'stock_earnings_1str',                  # 2
    ]

    evaluation_tests = [
        'csv_genes_list',
        'csv_genes_wikidata',
        'current_year',
        'file_integers_adder',
        'find_urls_file',
        'html_tag1',
        'math_image',
        'ner_file_persons',
        'online_spreadsheet_read',
        'online_spreadsheet_stocks',
        'pdf_titles2',
        'stock_earnings_2str',
        'stock_earnings_file',
        'textfile_reverser',
        'url_file_html',
        'urls_exists_file',
        'urls_successfull_scrapes_file',
        'word_count_pdf_section',
        'zip_file1_read',
        'zip_file_list',
        'zip_file_list_find_pdfs',
        'zipped_pdf_titles2',
        'cpp_correcter',
        'cpp_semicolon_correcter',
        'csv_genes_wikipedia_word1',
        'csv_grades_count',
        'csv_stock_price_dict',
        'email_pdf_title',
        'excel_sheet2',
        'fact_extract',
        'file_float_rounder_str',
        'html_paragraph_extractor_file',
        'html_tags_file',
        'image_rescale_size',
        'image_rescale_size_saved',
        'image_zip_rescale_size_saved',
        'json2dict',
        'json_average',
        'json_country2capital',
        'json_dict_add',
        'json_dict_average',
        'json_key_sort',
        'json_movies_2000',
        'language_detect',
        'language_detect_translate',
        'markdown2html',
        'math_expression_textfile',
        'matrix_correlation',
        'pdf2html',
        'python_comments',
        'python_correct_execute',
        'python_syntax_error_finder',
        'r_execute',
        'survey_average_rating',
        'survey_opinion_sentiment',
        'text_file_counter',
        'text_lower_reverse_split',
        'translate_2output',
        'translate_eng_french_pdf',
        'txt2pdf2txt',
        'url2domainname_file',
        'urls2domainnames_file',
        'urls_reachable',
        'wikidata_description_file',
        'wikipedia_content_file',
        'wikipedia_info_extract',
        'word_frequency',
        'word_lengths_file',
        'xml2json',
        'xml2list',
        'zip_zip_content',
        'zipped_pdf_tables_count',
    ]

    # Print dataset
    # print(tests_str(include_tests=include_tests))
    # print(tests_str())
    # input()

    # Compute and print dataset stats
    # pre_test_stats(include_tests=include_tests)
    # pre_test_stats()
    # input()

    # Create training dataset
    # print(create_training_set(include_tests=include_tests))
    # create_training_set()
    # input()

    # evaluation_tests = create_test_set(training_set=developer_tests)
    # pre_test_stats(include_tests=evaluation_tests)
    # input()

    # include_tests = developer_tests
    # include_tests = evaluation_tests
    include_tests = [
        # 'python_execute',                       # 1: just forwards code to pythoncoder, doesn't set result variable
        # 'reversed_constant_string',             # 2
        # 'ner_file_persons_hard',                # 2
        # 'integer_sort_python',                  # 2
        # 'translate_eng_french',                 # 1: uses LLM for translation, but it outputs more than just the translation
        # 'integer_sort_r',                       # 0: seems to be something wrong with R coder, but generated R code also wrong (i.e. result label should probably be 1)
        # 'file_float_rounder',                   # 2
        # 'matrix_multiplication_determinant',    # 0: crashes because LLM generate python code using pd.compat.StringIO which has been removed from new pandas versions
        # 'word_count_pdf',                       # 2
        # 'word_count_zip',                       # 2
        # 'wikipedia_word1',                      # 2
        # 'dates_iso_format',                     # 1: 2000-01-13T00:00:00 instead of just date 
        # 'image_dominant_color',                 # 1: outputs the list [0, 0, 0] instead of a tuple (0, 0, 0)
        # 'python_syntax_error_correcter',        # 1: uses autopep8 but it fails correcting the syntax error
        # 'math_expression_image',                # 1: uses pic2text for extracting but then pythoncoder with regex and eval that fails extracting eval str from latex expression string (probably because of \cdot inside)
        # 'html_scrape_json_urls_status',         # 1: outputs dict {url: "200 OK"} instead of just list [200]
        # 'csv_genes_wikipedia_sentence1',        # 1: correct, except missing the dot 
        # 'country_largest_file',                 # 2  (quite impressive -- it uses python coder to request to https://restcountries.com/v3.1/name/)
        # 'text_sentences2newline',               # 2
        # 'html_scrape_json_urls',                # 0: pythoncode fails -- json.dumps({input_str}) should be json.dumps("{input_str}")
        # 'longest_pdf2',                         # 1: outputs "['This is a pdf containing some interesting content. ']" instead of just sentence inside
        # 'integral_file',                        # 0: computes correct result but returns integral_result.evalf() which is of type <class 'sympy.core.numbers.Float'> so program crashes
        'constant_string',                      # 2
        # 'ner_file',                             # 2
        # 'find_urls_file_scrape',                # 1: outputs the output from URL scraper, instead of using property getter to extract only the content. Proposed solution: add example of URL scraper (potentially use the 3 step approach where LLM first chooses potential components and then examples are retrieved of each of those)
        # 'file_content_searcher',                # 2
        # 'text_misspelling_file',                # 0: uses a pythoncoder with `from spellchecker import SpellChecker` which works good outside lunar, but fails to import `from indexer import DictionaryIndex` in that package
        # 'cpp_content',                          # 2
        # 'stock_earnings_1str',                  # 2
        # 'csv_genes_list',
        # 'csv_genes_wikidata',
        # 'current_year',
        # 'file_integers_adder',
        # 'find_urls_file',
        # 'html_tag1',
        # 'math_image',
        # 'ner_file_persons',
        # 'online_spreadsheet_read',
        # 'online_spreadsheet_stocks',
        # 'pdf_titles2',
        # 'stock_earnings_2str',
        # 'stock_earnings_file',
        # 'textfile_reverser',
        # 'url_file_html',
        # 'urls_exists_file',
        # 'urls_successfull_scrapes_file',
        # 'word_count_pdf_section',
        # 'zip_file1_read',
        # 'zip_file_list',
        # 'zip_file_list_find_pdfs',
        # 'zipped_pdf_titles2',
        # 'cpp_correcter',
        # 'cpp_semicolon_correcter',
        # 'csv_genes_wikipedia_word1',
        # 'csv_grades_count',
        # 'csv_stock_price_dict',
        # 'email_pdf_title',
        # 'excel_sheet2',
        # 'fact_extract',
        # 'file_float_rounder_str',
        # 'html_paragraph_extractor_file',
        # 'html_tags_file',
        # 'image_rescale_size',
        # 'image_rescale_size_saved',
        # 'image_zip_rescale_size_saved',
        # 'json2dict',
        # 'json_average',
        # 'json_country2capital',
        # 'json_dict_add',
        # 'json_dict_average',
        # 'json_key_sort',
        # 'json_movies_2000',
        # 'language_detect',
        # 'language_detect_translate',
        # 'markdown2html',
        # 'math_expression_textfile',
        # 'matrix_correlation',
        # 'pdf2html',
        # 'python_comments',
        # 'python_correct_execute',
        # 'python_syntax_error_finder',
        # 'r_execute',
        # 'survey_average_rating',
        # 'survey_opinion_sentiment',
        # 'text_file_counter',
        # 'text_lower_reverse_split',
        # 'translate_2output',
        # 'translate_eng_french_pdf',
        # 'txt2pdf2txt',
        # 'url2domainname_file',
        # 'urls2domainnames_file',
        # 'urls_reachable',
        # 'wikidata_description_file',
        # 'wikipedia_content_file',
        # 'wikipedia_info_extract',
        # 'word_frequency',
        # 'word_lengths_file',
        # 'xml2json',
        # 'xml2list',
        # 'zip_zip_content',
        # 'zipped_pdf_tables_count',
    ]
    # print(include_tests)
    # input()

    # Run tests
    # test_gpt4o(include_tests=include_tests)
    # input()
    # test_llama3_8b(include_tests=include_tests)
    # input()
    # test_mixtral_8x7b(include_tests=include_tests)
    # input()
    # test_gemma2_9b(include_tests=include_tests)
    # input()
    test_autoworkflow(include_tests=include_tests, save_workflows=False)
    # input()
