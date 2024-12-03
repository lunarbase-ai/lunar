# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Simon Ljungbeck <simon.ljungbeck@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

#!/usr/bin/env python3

import argparse
import json
import os
import warnings

from typing import Any, List, Dict

from lunarcore.benchmark.auto_workflow.dataset import get_subdirectories

from lunarcore.benchmark.auto_workflow.config import (
    JSON_DESCRIPTION_KEY,
    JSON_TEST_LEVELS,
    TEMPLATE_JSON_FILE,
    TESTS_DIR,
)


def get_json_path(test_name: str):
    path = os.path.join(
        os.path.dirname(__file__),
        TESTS_DIR,
        test_name,
        TEMPLATE_JSON_FILE.format(name=test_name)
    )
    return path


def load_test_data(test_name: str):
    json_path = get_json_path(test_name)
    if os.path.exists(json_path):
        with open(json_path, 'r') as json_file:
            test_data = json.load(json_file)
            return test_data
    return None


def save_test_data(test_name: str, test_data: Dict):
    json_path = get_json_path(test_name)
    if os.path.exists(json_path):
        with open(json_path, 'w') as json_file:
            json.dump(test_data, json_file, indent=4)
    else:
        warnings.warn(f'Could not save since {json_path} does not exist.')


def update_level(test_data: Dict, level_name: str):
    new_level = input(f"Set value of level '{level_name}' (current value: {test_data[JSON_TEST_LEVELS].get(level_name, None)}): ")
    if len(new_level) > 0:
        test_data[JSON_TEST_LEVELS][level_name] = int(new_level)


def update_levels(test_data: Dict, level_names: List[str]):
    for level_name in level_names:
        update_level(test_data, level_name)


def update_intent(test_data):
    new_intent = input('Input new intent (press enter to keep old one):\n')
    if len(new_intent) > 0:
        test_data[JSON_DESCRIPTION_KEY] = new_intent


def update_test_data(test_name: str, test_data: Dict, level_names: List[str], update_intents: bool):
    print(f'Test name: {test_name}')
    print(f'Intent: {test_data[JSON_DESCRIPTION_KEY]} ')
    if update_intents:
        update_intent(test_data)
    update_levels(test_data, level_names)
    test_data["evaluation_data"] = {
        "evaluation_method": "deterministic",
        "evaluation_method_data": {
            "expected_outputs": test_data['expected_outputs']
        }
    }


def update_tests(level_names: List[str], update_intents: bool):
    all_test_names = get_subdirectories(os.path.join(os.path.dirname(__file__), TESTS_DIR))
    for test_nr, test_name in enumerate(all_test_names):
        print(f'\nTEST {test_nr+1}/{len(all_test_names)}')
        test_data = load_test_data(test_name)
        if test_data:
            update_test_data(test_name, test_data, level_names, update_intents)
            save_test_data(test_name, test_data)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This program existing tests for the AutoWorkflow tester')
    parser.add_argument('-lvs','--levels', metavar='LEVELS', nargs='+', required=False, default=[],
                        help='Add/update levels')
    parser.add_argument('-i', '--intents', action='store_true', help='Update intents')
    args = vars(parser.parse_args())

    update_tests(
        level_names=args['levels'],
        update_intents=args['intents']
    )