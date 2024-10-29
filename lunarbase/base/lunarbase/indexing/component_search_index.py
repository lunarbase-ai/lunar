# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

from typing import List, Union, Dict

from whoosh import index, scoring
from whoosh.fields import Schema, TEXT, ID, BOOLEAN
from whoosh.index import EmptyIndexError
from whoosh.qparser import QueryParser

from lunarbase.lunarbase.auto_workflow import PersistenceLayer
from lunarbase.lunarbase.config import LunarConfig
from lunarbase import ComponentModel


class ComponentSearchIndex:
    def __init__(self, config: Union[str, Dict, LunarConfig]):
        self._config = config
        if isinstance(self._config, str):
            self._config = LunarConfig.get_config(settings_file_path=config)
        elif isinstance(self._config, dict):
            self._config = LunarConfig.parse_obj(config)
        self.schema = Schema(
            id=ID(stored=True),
            string=TEXT,
            type=TEXT(stored=True),
            is_custom=BOOLEAN(stored=True),
        )
        self._persistence_layer = PersistenceLayer(config=self._config)

    def get_or_create_index(self, index_path: str):
        try:
            return index.open_dir(index_path)
        except EmptyIndexError:
            return index.create_in(
                index_path,
                self.schema,
            )

    def index_global_components(self, components: List[ComponentModel]):
        ix = index.create_in(
            self._config.get_component_index(),
            self.schema,
        )
        writer = ix.writer()
        for component in components:
            writer.add_document(
                id=component.id,
                string=component.name
                + " "
                + component.description
                + " "
                + component.class_name,
                type=component.class_name,
                is_custom=component.is_custom,
            )
        writer.commit()

    def index(self, components: List[ComponentModel], user_id: str):
        path = self._persistence_layer.get_user_component_index(user_id)
        ix = self.get_or_create_index(path)
        writer = ix.writer()

        for component in components:
            if component.is_custom:
                writer.add_document(
                    id=component.id,
                    string=component.name
                    + " "
                    + component.description
                    + " "
                    + component.class_name,
                    type=component.class_name,
                    is_custom=component.is_custom,
                )
        writer.commit()

    def remove_component(self, component_id: str, user_id: str):
        path = self._persistence_layer.get_user_component_index(user_id)
        ix = self.get_or_create_index(path)
        writer = ix.writer()
        writer.delete_by_term("id", component_id)
        writer.commit()

    def get_component(self, component_id: str, user_id: str):
        results = self.search(component_id, user_id, field="id")
        return [r["id"] for r in results]

    def search(self, query: str, user_id: str, field: str = "string"):
        global_ix = self.get_or_create_index(self._config.get_component_index())
        custom_ix = self.get_or_create_index(
            self._persistence_layer.get_user_component_index(user_id)
        )
        results = []
        with global_ix.searcher(weighting=scoring.BM25F()) as searcher:
            parsed_query = QueryParser(field, global_ix.schema).parse(query)
            for result in searcher.search(parsed_query, limit=10):
                results.append(
                    {
                        "id": result.get("id"),
                        "type": result.get("type"),
                        "is_custom": result.get("is_custom"),
                        "string": result.get("string"),
                    }
                )
        with custom_ix.searcher(weighting=scoring.BM25F()) as searcher:
            parsed_query = QueryParser(field, custom_ix.schema).parse(query)
            for result in searcher.search(parsed_query, limit=10):
                results.append(
                    {
                        "id": result.get("id"),
                        "type": result.get("type"),
                        "is_custom": result.get("is_custom"),
                        "string": result.get("string"),
                    }
                )

        return results
