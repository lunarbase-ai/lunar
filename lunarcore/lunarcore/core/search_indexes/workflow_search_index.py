# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

from typing import List, Union, Dict

from whoosh.index import EmptyIndexError

from lunarcore import PersistenceLayer
from lunarcore.config import LunarConfig
from lunarcore.core.data_models import WorkflowModel
from whoosh import index, scoring
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser

from lunarcore.utils import get_config


class WorkflowSearchIndex:
    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self._config = config
        if isinstance(self._config, str):
            self._config = get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)

        self.schema = Schema(
            name=TEXT(stored=True),
            id=ID(stored=True),
            description=TEXT,
            variable_keys=TEXT,
            variable_values=TEXT,
            string=TEXT,
        )

        self._persistence_layer = PersistenceLayer(config=self._config)

    @property
    def config(self):
        return self._config

    def get_or_create_index(self, user_id: str):
        index_path = self._persistence_layer.get_user_workflow_index(user_id)
        try:
            return index.open_dir(index_path)
        except EmptyIndexError:
            return index.create_in(
                index_path,
                self.schema,
            )

    def index(self, workflows: List[WorkflowModel], user_id: str):
        ix = self.get_or_create_index(user_id)
        writer = ix.writer()
        for flow in workflows:
            variable_keys = []
            variable_values = []
            for comp in flow.components:
                variable_keys.extend([inp.key for inp in comp.inputs])
                variable_values.extend([inp.value for inp in comp.inputs])

            writer.add_document(
                name=flow.name,
                id=flow.id,
                description=flow.description,
                variable_keys=str(variable_keys),
                variable_values=str(variable_values),
                string=f"{flow.name} {flow.description}",
            )
        writer.commit()

    def remove_document(self, workflow_id: str, user_id: str):
        ix = self.get_or_create_index(user_id)
        writer = ix.writer()
        writer.delete_by_term("id", workflow_id)
        writer.commit()

    def search(self, query: str, user_id: str, field: str = "string"):
        ix = self.get_or_create_index(user_id)
        results = []
        with ix.searcher(weighting=scoring.BM25F()) as searcher:
            parsed_query = QueryParser(field, ix.schema).parse(query)
            for result in searcher.search(parsed_query, limit=10):
                results.append({"id": result.get("id"), "name": result.get("name")})

        return results
