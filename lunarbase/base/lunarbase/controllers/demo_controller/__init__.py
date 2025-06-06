#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

import json
from pathlib import Path
from typing import Union, Dict

from lunarbase.config import LunarConfig
from lunarbase.modeling.data_models import WorkflowModel


class DemoController:
    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self._config = config
        if isinstance(self._config, str):
            self._config = LunarConfig.get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)
        self._demos_path = self._config.DEMO_STORAGE_PATH

    @property
    def config(self):
        return self._config

    @property
    def demos_path(self):
        return self._demos_path

    def get_by_id(self, workflow_id: str):
        wf_path = str(Path(self._demos_path, workflow_id, f"{workflow_id}.json"))
        with open(wf_path, "r") as file:
            workflow = json.load(file)
        return WorkflowModel.model_validate(workflow)

    def list_short(self):
        flow_list = []
        try:
            base_path = Path(self._demos_path)
            element_paths = [str(_path) for _path in base_path.glob("*/*")]
        except FileNotFoundError:
            element_paths = []
        for element_path in element_paths:
            if not str(element_path).lower().endswith(".json"):
                continue
            with open(element_path, "r") as file:
                element = json.load(file)
            flow_list.append(element)
        flow_list = map(
            lambda chain: WorkflowModel.model_validate(chain).short_model(), flow_list
        )
        return list(flow_list)
