# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Simon Ljungbeck <simon.ljungbeck@idiap.ch>
#
# SPDX-License-Identifier: GPL-3.0-or-later

#!/usr/bin/env python3

import argparse
import json
import os
import shutil
import warnings

from typing import Any, List

from config import (
    ARGS_TESTNAME_KEY,
    ARGS_DESCRIPTION_KEY,
    ARGS_OUTPUT_KEY,
    ARGS_EVALUATION_METHOD_KEY,
    ARGS_FILES_KEY,
    ARGS_FILE_DESCRIPTIONS_KEY,
    ARGS_LEVEL_NAMES_KEY,
    ARGS_LEVELS_KEY,
    ARGS_TESTLABELS_KEY,
    FILES_DIR,
    JSON_DESCRIPTION_KEY,
    JSON_EXPECTED_OUTPUTS_KEY,
    JSON_EVALUATION_METHOD_KEY,
    JSON_FILES_KEY,
    JSON_FILES_NAME_KEY,
    JSON_FILES_DESCRIPTION_KEY,
    JSON_TEST_LEVELS,
    JSON_TEST_LABELS,
    TEMPLATE_JSON_FILE,
    TESTS_DIR,
    DEFAULT_EVALUATION_METHOD,
    EVALUATION_METHODS,
)


def _test_path(name: str):
    test_path = os.path.join(os.path.normpath(os.path.dirname(__file__)), TESTS_DIR, name)
    return test_path


def _create_test_dir(name: str):
    test_path = _test_path(name)
    try:
        os.makedirs(test_path, exist_ok=False)
    except FileExistsError:
        ans = input(f"Test '{name}' already exists. Sure you want to overwrite it? (Y/n)\n").lower()
        while ans not in ('', 'y', 'yes', 'n', 'no'):
            ans = input(f"Please answer with 'Y/n'")
        if ans in ('n', 'no'):
            return False
        os.makedirs(test_path, exist_ok=True)
    return test_path


def _fill_file_descriptions(file_names: List[str] = None,
                            file_descriptions: List[str] = None):
    while len(file_names) > len(file_descriptions):
        file_descriptions.append('')


def _json_files_list(file_names: List[str] = None,
                     file_descriptions: List[str] = None):
    if len(file_names) != len(file_descriptions):
        warnings.warn('File names and file descriptions of different sizes! Filling with empty descriptions!')
        _fill_file_descriptions(file_names, file_descriptions)
    files_list = []
    for name, description in zip(file_names, file_descriptions):
        files_list.append({JSON_FILES_NAME_KEY: name,
                           JSON_FILES_DESCRIPTION_KEY: description})
    return files_list


def _fill_levels(level_names: List[str] = None, levels: List[int] = None):
    while len(level_names) > len(levels):
        levels.append(-1)


def _json_levels_dict(level_names: List[str] = None, levels: List[int] = None):
    if len(level_names) != len(levels):
        warnings.warn('Level names and levels of different sizes! Filling with -1 levels!')
        _fill_levels(level_names, levels)
    levels_dict = {}
    for level_name, level in zip(level_names, levels):
        levels_dict[level_name] = level
    return levels_dict


def _create_json_file(test_path: str, name: str, description: str = '',
                      outputs: Any = None, evaluation_method: str = None,
                      labels: str = None, file_names: List[str] = None,
                      file_descriptions: List[str] = None,
                      level_names: List[str] = None, levels: List[int] = None):
    dir_json = {
        JSON_DESCRIPTION_KEY: description,
        JSON_EXPECTED_OUTPUTS_KEY: outputs or [],
        JSON_EVALUATION_METHOD_KEY: evaluation_method or DEFAULT_EVALUATION_METHOD,
        JSON_FILES_KEY: _json_files_list(file_names, file_descriptions),
        JSON_TEST_LEVELS: _json_levels_dict(level_names, levels),
        JSON_TEST_LABELS: labels or [],
    }
    path = os.path.join(test_path, TEMPLATE_JSON_FILE.format(name=name))
    with open(path, 'w') as json_file:
        json.dump(dir_json, json_file, indent=4)


def _test_files_path(test_path: str):
    files_path = os.path.join(test_path, FILES_DIR)
    return files_path


def _dir_copy_file(source_path: str, destination_dir: str):
    file_name = os.path.basename(source_path)
    destination_path = os.path.join(destination_dir, file_name)
    if os.path.exists(destination_dir):
        print(f'File {file_name} already exists in {destination_dir}. Skipping copying {source_path}!')
    shutil.copyfile(source_path, destination_path)
    return file_name


def _create_empty_file(path: str):
    open(path, 'a').close()


def _create_files_dir(test_path: str, files: str):
    files_path = _test_files_path(test_path)
    file_names = []
    os.makedirs(files_path, exist_ok=True)
    for source_path in files:
        if os.path.exists(source_path):
            file_name = _dir_copy_file(source_path, files_path)
            file_names.append(file_name)
        else:
            file_name = os.path.basename(source_path)
            if file_name:
                file_path = os.path.join(files_path, file_name)
                _create_empty_file(file_path)
                file_names.append(file_name)
    return file_names


def create_test(name: str, description: str = '', outputs: Any = None,
                evaluation_method: str = None, files: List[str] = None,
                file_descriptions: List[str] = None,
                level_names: List[str] = None, levels: List[int] = None,
                labels: List[str] = None):
    if evaluation_method is not None and evaluation_method not in EVALUATION_METHODS:
        print(f"Evaluation method '{evaluation_method}' is not valid.")
        return
    test_path = _create_test_dir(name)
    if test_path:
        file_names = _create_files_dir(test_path, files)
        _create_json_file(test_path, name, description, outputs,
                          evaluation_method, labels, file_names,
                          file_descriptions, level_names, levels)
        print(f'Successfully created a test template with the location {test_path}')
    else:
        print('Test template creation cancelled, no test created!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This program creates a template for a test that can be executed by the AutoWorkflow tester')
    parser.add_argument('name', help='Name of the test on snake_case format')
    parser.add_argument('-d','--description', default='', required=False,
                        help='Description of the workflow to be passed to the AutoWorkflow decomposer')
    parser.add_argument('-o','--outputs', metavar='OUTPUT', nargs='+', required=False, default=[],
                        help='Expected outputs of the test')
    parser.add_argument('-e','--evaluation_method', metavar='EVALUATION_METHOD', required=False, default=DEFAULT_EVALUATION_METHOD,
                        help='Expected outputs of the test')
    parser.add_argument('-f','--files', metavar='FILES', nargs='+', required=False, default=[],
                        help='Paths of local files that are to be inputted to the test (these will be copied, or created if not existing)')
    parser.add_argument('-fd','--file_descriptions', metavar='FILE_DESCRIPTIONS', nargs='+', required=False, default=[],
                        help='Descriptions of the files in the same order')
    parser.add_argument('-lvn','--level_names', metavar='LEVEL_NAMES', nargs='+', required=False, default=[],
                        help="Level names (eg. 'components', 'complexity', 'specificity', 'custom_components', 'input_files', 'outputs', 'specialization')")
    parser.add_argument('-lv','--levels', metavar='LEVELS', nargs='+', type=int, required=False, default=[],
                        help="Levels in the same order as the level names")
    parser.add_argument('-lb','--labels', metavar='LABEL', nargs='+', required=False, default=[],
                        help="Test classification labels (eg. 'custom_component', 'input_file', '3components', etc.)")
    args = vars(parser.parse_args())

    create_test(
        name=args[ARGS_TESTNAME_KEY],
        description=args[ARGS_DESCRIPTION_KEY],
        outputs=args[ARGS_OUTPUT_KEY],
        evaluation_method=args[ARGS_EVALUATION_METHOD_KEY],
        files=args[ARGS_FILES_KEY],
        file_descriptions=args[ARGS_FILE_DESCRIPTIONS_KEY],
        level_names=args[ARGS_LEVEL_NAMES_KEY],
        levels=args[ARGS_LEVELS_KEY],
        labels=args[ARGS_TESTLABELS_KEY]
    )
