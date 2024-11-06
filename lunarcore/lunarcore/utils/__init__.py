# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

import logging
import traceback
import re
import warnings
from functools import lru_cache
from itertools import islice
import inspect

from sphinx.ext.intersphinx import fetch_inventory
from typing import Any, Tuple

from lunarcore.logging import LunarLogFormatter


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


def get_python_std_modules(version: Tuple):
    """
    Thanks to https://github.com/PyCQA/isort/blob/7de182933fd50e04a7c47cc8be75a6547754b19c/scripts/mkstdlibs.py#L4
    """
    PYTHON_URL = "https://docs.python.org/{}/objects.inv"

    class FakeConfig:
        intersphinx_timeout = None
        tls_cacerts = None
        tls_verify = False
        user_agent = ""

    class FakeApp:
        srcdir = ""
        config = FakeConfig()

    version = ".".join([str(v) for v in version])
    url = PYTHON_URL.format(version)
    invdata = fetch_inventory(FakeApp(), "", url)

    # Any modules we want to enforce across Python versions stdlib can be included in set init
    modules = {
        "_ast",
        "posixpath",
        "ntpath",
        "sre_constants",
        "sre_parse",
        "sre_compile",
        "sre",
    }
    for module in invdata["py:module"]:
        root, *_ = module.split(".")
        if root not in ["__future__", "__main__"]:
            modules.add(root)
    return modules


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
