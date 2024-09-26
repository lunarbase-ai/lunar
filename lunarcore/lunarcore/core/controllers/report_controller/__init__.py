# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase


from typing import Union, Dict
from lunarcore.core.persistence_layer import PersistenceLayer
from lunarcore.config import LunarConfig
from lunarcore.core.typings.report import ReportSchema
from lunarcore.utils import get_config
import os

class ReportController:
    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self._config = config
        if isinstance(self._config, str):
            self._config = get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)

        self._persistence_layer = PersistenceLayer(config=self._config)

    async def save(self, user_id: str, report: ReportSchema):
        report_data = report.dict()
        path = self._persistence_layer.get_user_workflow_report_path(
            user_id=user_id, workflow_id=report.workflow
        )
        await self._persistence_layer.save_to_storage_as_json(
            path=f"{path}/{report.id}.json", data=report_data
        )
        return report

    async def list_all(self, user_id: str):
        path = self._persistence_layer.get_user_workflow_root(user_id=user_id)
        report_list = await self._persistence_layer.get_all_as_dict(
            path=f"{path}/*/{self._config.REPORT_PATH}/*.json"
        )
        return report_list

    async def get_by_id(self, user_id: str, workflow_id: str, id: str):
        path = self._persistence_layer.get_user_workflow_report_path(
            user_id=user_id, workflow_id=workflow_id
        )
        report = await self._persistence_layer.get_from_storage_as_dict(
            path=f"{path}/{id}.json",
        )
        return report