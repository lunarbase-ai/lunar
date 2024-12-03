# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Simon Ljungbeck <simon.ljungbeck@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import json
import numpy as np
import os
import random
import warnings

from typing import Dict, List

from lunarcore.benchmark.auto_workflow.config import (
    TESTS_DIR,
    FILES_DIR,
    JSON_DESCRIPTION_KEY,
    JSON_EXPECTED_OUTPUTS_KEY,
    JSON_FILES_KEY,
    JSON_FILES_NAME_KEY,
    JSON_FILES_DESCRIPTION_KEY,
    JSON_TEST_LEVELS,
    JSON_TEST_LEVEL_COMPONENTS,
    JSON_TEST_LEVEL_CUSTOM_COMPONENTS,
    JSON_TEST_LEVEL_KB_COMPONENTS,
    JSON_TEST_LEVEL_FILES,
    JSON_TEST_LEVEL_INTENT_LENGTH,
    JSON_TEST_LEVEL_INTENT_LENGTH_DIV,
    JSON_TEST_LABELS,
    TEMPLATE_JSON_FILE,
    MAX_LEN_EXPECTED_OUTPUT,
    DATASET_STATS_DIR,
    HISTOGRAM_WORKFLOW_LENGTHS_FILE,
    HISTOGRAM_INTENT_CHARS_FILE,
    HISTOGRAM_INTENT_WORDS_FILE,
    HISTOGRAM_KB_COMPONENTS_FILE,
    HISTOGRAM_CUSTOM_COMPONENTS_FILE,
    LEVEL2LABEL_TEMPLATE,
)
from lunarcore.core.typings.datatypes import File
from lunarcore.benchmark.auto_workflow.utils import (
    histogram,
)


def get_subdirectories(directory_path: str):
    entries = os.listdir(directory_path)
    subdirectories = [entry for entry in entries if os.path.isdir(os.path.join(directory_path, entry))]
    return subdirectories


class Dataset():
    class DatasetStatistics():
        def __init__(self, test_jsons: Dict[str, Dict], dataset_stats_dir: str = DATASET_STATS_DIR):
            self.test_jsons = test_jsons
            self.dataset_stats_dir = dataset_stats_dir

        def workflow_length_stats(self):
            lengths = np.array([test_data[JSON_TEST_LEVELS][JSON_TEST_LEVEL_COMPONENTS] for test_data in self.test_jsons.values()])
            print(f'Mean workflow length (#components): {np.mean(lengths):.2f}')
            print(f'Std workflow length (#components): {np.std(lengths, ddof=1):.2f}')
            file_path = os.path.join(self.dataset_stats_dir, HISTOGRAM_WORKFLOW_LENGTHS_FILE)
            print(f'Histogram of workflow lengths (#components): {histogram(lengths, "Workflow lengths", "#Components", "Frequency", file_path, integer_partition=True)}')

        def intent_chars_stats(self):
            lengths = np.array([len(test_data[JSON_DESCRIPTION_KEY]) for test_data in self.test_jsons.values()])
            print(f'Mean intent length (#characters): {np.mean(lengths):.2f}')
            print(f'Std intent length (#characters): {np.std(lengths, ddof=1):.2f}')
            file_path = os.path.join(self.dataset_stats_dir, HISTOGRAM_INTENT_CHARS_FILE)
            print(f'Histogram of intent lengths (#characters): {histogram(lengths, "Intent lengths", "#Characters", "Frequency", file_path)}')

        def intent_words_stats(self):
            lengths = np.array([len(test_data[JSON_DESCRIPTION_KEY].split()) for test_data in self.test_jsons.values()])
            print(f'Mean intent length (#words): {np.mean(lengths):.2f}')
            print(f'Std intent length (#words): {np.std(lengths, ddof=1):.2f}')
            file_path = os.path.join(self.dataset_stats_dir, HISTOGRAM_INTENT_WORDS_FILE)
            print(f'Histogram of intent lengths (#words): {histogram(lengths, "Intent lengths", "#Words", "Frequency", file_path)}')

        def knowledge_base_components_stats(self):
            lengths = np.array([test_data[JSON_TEST_LEVELS][JSON_TEST_LEVEL_COMPONENTS]-test_data[JSON_TEST_LEVELS][JSON_TEST_LEVEL_CUSTOM_COMPONENTS] for test_data in self.test_jsons.values()])
            print(f'Mean number KB components: {np.mean(lengths):.2f}')
            print(f'Std nuber KB components: {np.std(lengths, ddof=1):.2f}')
            file_path = os.path.join(self.dataset_stats_dir, HISTOGRAM_KB_COMPONENTS_FILE)
            print(f'Histogram of number KB components: {histogram(lengths, "KB components", "#Components", "Frequency", file_path, integer_partition=True)}')

        def custom_components_stats(self):
            lengths = np.array([test_data[JSON_TEST_LEVELS][JSON_TEST_LEVEL_CUSTOM_COMPONENTS] for test_data in self.test_jsons.values()])
            print(f'Mean number custom components: {np.mean(lengths):.2f}')
            print(f'Std nuber custom components: {np.std(lengths, ddof=1):.2f}')
            file_path = os.path.join(self.dataset_stats_dir, HISTOGRAM_CUSTOM_COMPONENTS_FILE)
            print(f'Histogram of number custom components: {histogram(lengths, "Custom components", "#Components", "Frequency", file_path, integer_partition=True, xaxis_integers=True)}')

    def __init__(self, tests_dir: str = TESTS_DIR, include_tests: List[str] = None):
        self.tests_dir = tests_dir or TESTS_DIR
        self.test_jsons = self._load_test_jsons(include_tests)
        self.dataset_stat = self.DatasetStatistics(self.test_jsons, DATASET_STATS_DIR)

    def __str__(self):
        tests_sb = []
        for test_nr, (test_name, test_data) in enumerate(self.test_jsons.items()):
            # tests_sb.append(f'TEST {test_nr+1}')
            # tests_sb.append(f'Test name: {test_name}')
            # tests_sb.append(f'Intent: {test_data[JSON_DESCRIPTION_KEY]}')
            tests_sb.append(f'\\item {test_data[JSON_DESCRIPTION_KEY]}')
            # tests_sb.append(f'Expected outputs: {self.expected_outputs_chop(test_data[JSON_EXPECTED_OUTPUTS_KEY])}')
            # tests_sb.append(f'Expected number components: {test_data[JSON_TEST_LEVELS][JSON_TEST_LEVEL_COMPONENTS]}\n')
        return '\n'.join(tests_sb)

    def _load_test_jsons(self, include_tests: List[str]):
        all_test_names = get_subdirectories(os.path.join(os.path.dirname(__file__), self.tests_dir))
        test_jsons = {}
        for test_name in include_tests or all_test_names:
            if test_name in all_test_names:
                test_data = self._load_test_json(test_name)
                if test_data:
                    test_jsons[test_name] = test_data
                else:
                    warnings.warn(f"Could not load the JSON file of test '{test_name}'. Skipping it!")
            else:
                warnings.warn(f"Could not find test '{test_name}'. Skipping it!")
        return test_jsons
    
    def expected_outputs_chop(self, expected_outputs: List[str]):
        choped_expected_outputs = []
        for expected_output in expected_outputs:
            if len(expected_output) <= MAX_LEN_EXPECTED_OUTPUT:
                choped_expected_outputs.append(expected_output)
            else:
                choped_expected_outputs.append(f'{expected_output[:MAX_LEN_EXPECTED_OUTPUT]}...')
        return choped_expected_outputs

    def _levels2labels(self, test_data: Dict):
        for level_name, level in test_data[JSON_TEST_LEVELS].items():
            test_data[JSON_TEST_LABELS].append(
                LEVEL2LABEL_TEMPLATE.format(
                    level_name=level_name,
                    level=level
                )
            )

    def _intent_len_round(self, intent: str, div: int = JSON_TEST_LEVEL_INTENT_LENGTH_DIV):
        nr_words = len(intent.split())
        return int((nr_words + (div>>1))//div)

    def _fill_extra_json_data(self, test_data: Dict):
        test_data[JSON_TEST_LEVELS][JSON_TEST_LEVEL_KB_COMPONENTS] = test_data[JSON_TEST_LEVELS][JSON_TEST_LEVEL_COMPONENTS] - test_data[JSON_TEST_LEVELS][JSON_TEST_LEVEL_CUSTOM_COMPONENTS]
        test_data[JSON_TEST_LEVELS][JSON_TEST_LEVEL_FILES] = len(test_data[JSON_FILES_KEY])
        test_data[JSON_TEST_LEVELS][JSON_TEST_LEVEL_INTENT_LENGTH] = self._intent_len_round(test_data[JSON_DESCRIPTION_KEY])
        return test_data

    def _load_test_json(self, test_name: str, json_name: str = None):
        json_name = json_name or test_name    # Assumes json file has same name as directory
        json_path = os.path.join(os.path.dirname(__file__), self.tests_dir, test_name, TEMPLATE_JSON_FILE.format(name=json_name))
        if os.path.exists(json_path):
            with open(json_path, 'r') as json_file:
                test_data = json.load(json_file)
                test_data = self._fill_extra_json_data(test_data)
                self._levels2labels(test_data)
                return test_data
        return None

    def _test_file_path(self, test_name: str, file_name: str):
        path = os.path.join(os.path.dirname(__file__), self.tests_dir, test_name, FILES_DIR, file_name)
        return path

    def _files_list(self, test_name: str, files_json: List[Dict]):
        file_objects = []
        for file_json in files_json:
            path = self._test_file_path(test_name, file_json[JSON_FILES_NAME_KEY])
            if os.path.exists(path):
                file_object = File(
                    path=path,
                    description=file_json[JSON_FILES_DESCRIPTION_KEY]
                )
                file_objects.append(file_object)
            else:
                warnings.warn(f"Could not find input file '{path}'. Skipping it!")
        return file_objects

    def _pre_test_stats(self):
        self.dataset_stat.workflow_length_stats()
        self.dataset_stat.intent_chars_stats()
        self.dataset_stat.intent_words_stats()
        self.dataset_stat.knowledge_base_components_stats()
        self.dataset_stat.custom_components_stats()

    def random_sample(self, frac_samples: float):
        test_names = list(self.test_jsons)
        nr_samples = int(frac_samples * len(test_names))
        sample_test_names = random.sample(test_names, nr_samples)
        return sample_test_names
    
    def excluded_tests(self):
        all_test_names = get_subdirectories(self.tests_dir)
        excluded_tests = [test for test in all_test_names if test not in self.test_jsons]
        return excluded_tests
