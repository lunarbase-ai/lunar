# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase
import ast
import inspect
import logging
import re
import traceback
import warnings
import zipfile
from collections import defaultdict
from functools import lru_cache
from itertools import islice
from pathlib import Path
from typing import Any, List

from lunarbase.logging import LunarLogFormatter


class InheritanceTracker(object):
    class __metaclass__(type):
        __inheritors__ = defaultdict(list)

        def __new__(meta, name, bases, dct):
            klass = type.__new__(meta, name, bases, dct)
            for base in klass.mro()[1:-1]:
                meta.__inheritors__[base].append(klass)
            return klass


def exception_to_string(excp):
    # from https://stackoverflow.com/questions/4564559/get-exception-description-and-stack-trace-which-caused-an-exception-all-as-a-st/58764987#58764987
    stack = traceback.extract_stack()[:-3] + traceback.extract_tb(
        excp.__traceback__
    )  # add limit=??
    pretty = traceback.format_list(stack)
    return "".join(pretty) + "\n  {} {}".format(excp.__class__, excp)


def split_into_batches(embeddings, batch_size):
    num_embeddings = len(embeddings)
    num_batches = (num_embeddings + batch_size - 1) // batch_size  # Ceiling division

    batches = []
    for i in range(num_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, num_embeddings)
        batch = embeddings[start_idx:end_idx]
        batches.append(batch)

    return batches


def clean_text(text: str) -> str:
    text = re.sub(r"\[\d+\]", "", text)
    text = text.strip()
    text = re.sub("r\n{2,}", "\n", text)
    return text


def create_dict_chunks(data, size):
    it = iter(data)
    for i in range(0, len(data), size):
        yield {k: data[k] for k in islice(it, size)}


def create_list_chunks(data, size):
    size = max(1, size)
    return (data[i : i + size] for i in range(0, len(data), size))


def to_camel(snake_case):
    words = snake_case.split("_")
    camel_case = words[0] + "".join(word.capitalize() for word in words[1:])
    return camel_case


def get_template_variables(template):
    pattern = r"\{([^{}:]+)\}"
    matches = re.findall(pattern, template)
    return matches


def to_jinja_template(template, variables):
    for variable in variables:
        pattern = r"\{" + re.escape(variable) + r"\}"
        template = re.sub(pattern, r"{\g<0>}", template)

    remove_space_pattern = r"{{\s*(.*?)\s*}}"
    return re.sub(remove_space_pattern, r"{{\1}}", template)


def truncate_list(li, max_length, max_depth, current_depth=1):
    if not isinstance(li, list):
        raise ValueError("The first parameter should be a list!")

    truncated_list = []

    if current_depth > max_depth:
        return truncated_list

    for value in li:
        if isinstance(value, list):
            truncated_value = truncate_list(
                value, max_length, max_depth, current_depth + 1
            )
        elif isinstance(value, dict):
            truncated_value = truncate_dictionary(
                value, max_length, max_depth, current_depth + 1
            )
        else:
            truncated_value = value

        if len(truncated_list) < max_length:
            truncated_list.append(truncated_value)

    return truncated_list


def truncate_dictionary(d, max_length, max_depth, current_depth=1):
    if not isinstance(d, dict):
        raise ValueError("The first parameter should be a dictionary!")

    truncated_dict = {}

    if current_depth > max_depth:
        return truncated_dict

    for key, value in d.items():
        if isinstance(value, dict):
            truncated_value = truncate_dictionary(
                value, max_length, max_depth, current_depth + 1
            )
        elif isinstance(value, list):
            truncated_value = truncate_list(
                value, max_length, max_depth, current_depth + 1
            )
        else:
            truncated_value = value

        if len(truncated_dict) < max_length:
            truncated_dict[key] = truncated_value

    return truncated_dict


def select_property_from_dict(dictionary: dict, key_path: str):
    parts = key_path.split(".")

    if len(parts) > 1:
        value = dictionary[parts[0]]
        try:
            for p in parts[1:]:
                value = value[p]
        except KeyError:
            raise ValueError(f"The selected property path is invalid: {key_path}!")
        return value

    else:
        try:
            value = dictionary[key_path]
            return value
        except KeyError:
            raise ValueError(
                f"The selected property <{key_path}> doesn't exist in the input object! Accepted properties: {list(dictionary.keys())}"
            )


def fix_pip_package_version(version: str):
    if any(
        [
            str(version).startswith("="),
            str(version).startswith("~"),
            str(version).startswith(">"),
            str(version).startswith("<"),
        ]
    ):
        return version
    return "==" + version


def get_source_code(resource: Any):
    try:
        source_code = inspect.getsource(resource)
        return source_code
    except OSError as e:
        warnings.warn(
            f"Cannot retrieve source code for resource {resource}! This is probably a dynamic resource. Details: {str(e)}"
        )
    return None


@lru_cache()
def setup_logger(id: str):
    logger = logging.getLogger(id)
    logger.setLevel(logging.INFO)
    if logger.hasHandlers():
        logger.handlers.clear()

    console = logging.StreamHandler()
    console.setFormatter(LunarLogFormatter())
    logger.addHandler(console)
    logger.propagate = False
    return logger


def get_file_content(path: str):
    try:
        with open(path, "r") as file:
            content = file.read()
            return content
    except FileNotFoundError:
        warnings.warn(f"Could not find a file with the path {path}.")


def isiterable(obj: object):
    try:
        iter(obj)
        return True
    except TypeError:
        return False


def anyinzip(zip_path: str, paths: List[str]):
    with zipfile.ZipFile(zip_path) as z:
        for path in paths:
            if path in z.namelist():
                return path
    return None


def anyindir(root_path: str, paths: List[str]):
    for path in paths:
        if Path(path).is_relative_to(root_path):
            return path
    return None


def get_imports(source_code: str):
    raw_imports = set()

    tree = ast.parse(source_code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for subnode in node.names:
                raw_imports.add(subnode.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0:  # This is to ignore relative imports
                raw_imports.add(node.module)
    # Clean up imports
    imports = set()
    for name in [n for n in raw_imports if n]:
        # Sanity check: Name could have been None if the import
        # statement was as ``from . import X``
        # Cleanup: We only want to first part of the import.
        # Ex: from django.conf --> django.conf. But we only want django
        # as an import.
        cleaned_name, _, _ = name.partition(".")
        if len(cleaned_name) > 0:
            imports.add(cleaned_name)
    return list(imports)
