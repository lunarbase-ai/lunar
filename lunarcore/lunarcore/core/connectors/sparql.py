# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from typing import Any

from SPARQLWrapper import SPARQLWrapper, JSON


class SPARQLConnector:
    def __init__(self, endpoint: str, **kwargs: Any):
        self.sparql = SPARQLWrapper(endpoint=endpoint, returnFormat=JSON, **kwargs)
        self.__reset_query()

    def __reset_query(self):
        self.sparql.setQuery(query="")

    def query(self, query_string: str):
        self.sparql.setQuery(query=query_string)
        try:
            result = self.sparql.queryAndConvert()
            return result
        except Exception as e:
            raise ConnectionError(str(e))
