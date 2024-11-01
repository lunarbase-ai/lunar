# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase
from typing import Any, Optional
from sqlalchemy import create_engine, URL, text
from urllib.parse import quote, urlparse

class SQLConnector:
    def __init__(
        self,
        url: Optional[str] = None,
        driver_name: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[str] = None,
        database: Optional[str] = None,
        **connection_kwargs: Any,
    ):
        if url is not None:
            _url = urlparse(url)
            if _url.scheme != 'sqlite':
                left_url, _, right_url = url.rpartition('@')
                driver_name, credentials = left_url.split("://", 1)
                username, password = credentials.split(":", 1)
                host, database = right_url.split("/", 1)
                host, _, port = host.rpartition(":")
            else:
                driver_name = _url.scheme
                database = _url.path

        url = URL.create(
            driver_name,
            username=username,
            password=quote(password) if password else None,
            host=host,
            port=port,
            database=database,
        )
        self.engine = create_engine(url, **connection_kwargs)

    def query(self, query_string):
        with self.engine.connect() as connection:
            result = connection.execute(text(query_string))
            data = [r._asdict() for r in result.fetchall()]
            return data
