# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import contextlib
import json
from typing import Any, Dict, Iterable, Optional, Union, Mapping, List

from elasticsearch import ConnectionError, Elasticsearch, helpers, ApiError
from elasticsearch.helpers import BulkIndexError


class ElasticsearchConnector:
    def __init__(
        self,
        hostname_or_ip: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
        default_index: Optional[str] = None,
        **connection_kwargs: Any,
    ):
        self.tag = self.__class__.__name__

        self._hostname_or_ip = hostname_or_ip
        self._port = port

        self._username = username
        self._password = password

        self._connection_kwargs = (
            connection_kwargs if connection_kwargs is not None else dict()
        )

        self._default_index = default_index

    @property
    def default_index(self):
        return self._default_index

    @contextlib.contextmanager
    def connect(self):
        client = None
        try:
            if self._username is not None and self._password is not None:
                client = Elasticsearch(
                    f"http://{self._hostname_or_ip}:{self._port}",
                    http_auth=(self._username, self._password),
                )
            else:
                client = Elasticsearch(f"http://{self._hostname_or_ip}:{self._port}")

            print(
                f"{self.tag}: Connected to Elasticsearch at {self._hostname_or_ip}:{self._port}."
            )
            yield client
        except ConnectionError as e:
            print(
                f"{self.tag}: Failed to connect to Elasticsearch at {self._hostname_or_ip}:{self._port}."
            )
            raise e
        finally:
            if client is not None:
                client.transport.close()

    def update_script(self, script_id: str, script_body: Mapping):
        with self.connect() as client:
            print(f"{self.tag}: Storing script {script_id} ...")

            response = client.put_script(id=script_id, script=script_body)
            if response.meta.status != 200:
                raise ApiError(
                    f"Failed to store/update script {script_id}: {response.body}"
                )

            print(
                f"{self.tag}: script {script_id} stored successfully: {response.body}"
            )

    def update(
        self,
        data: Union[Dict, Iterable[Dict]],
        index: Optional[str] = None,
        index_mapping: Optional[Dict] = None,
    ):
        if index is None:
            index = self._default_index

        if index is None:
            raise ValueError(
                f"{self.tag}: No index name configured or passed at insert time!"
            )

        if isinstance(data, Dict):
            data = [data]

        if len(data) == 0:
            raise ValueError("Empty documents!")

        with self.connect() as client:
            if not client.indices.exists(index=index):
                if index_mapping is None:
                    raise ValueError(
                        f"{self.tag}: Index {index} not found, please create it first!"
                    )
                else:
                    self.create_index(index=index, mapping=index_mapping)

            data = [
                {
                    "_op_type": "update",
                    "_id": doc.pop("_id"),
                    "doc": doc,
                    "doc_as_upsert": True,
                }
                for doc in data
            ]

            try:
                response = helpers.bulk(
                    client=client, actions=data, index=index, request_timeout=180
                )  # 3 minutes
                return f"{self.tag}: Index {index} - indexed {len(data)} documents with status: {response}."

            except BulkIndexError as e:
                print(e.errors[0])
                raise e

    def delete(
        self,
        ids: Union[str, List[str]],
        index: Optional[str] = None,
    ):
        if index is None:
            index = self._default_index

        if index is None:
            raise ValueError(
                f"{self.tag}: No index name configured or passed at insert time!"
            )

        if isinstance(ids, str):
            ids = [ids]

        data = [
            {
                "_op_type": "delete",
                "_id": _i,
            }
            for _i in ids
        ]

        with self.connect() as client:
            try:
                print(f"{self.tag}: Updating {len(data)} documents ...")
                response = helpers.bulk(
                    client=client, actions=data, index=index, request_timeout=60
                )  # 3 minutes
                print(
                    f"{self.tag}: Index {index} - deleted {len(data)} documents ({ids}) with status: {response}."
                )
            except BulkIndexError as e:
                print(e.errors[0])
                raise e

    def insert(
        self,
        data: Union[Dict, Iterable[Dict]],
        index: Optional[str] = None,
        index_mapping: Optional[Dict] = None,
    ):
        """
        Each document should have a type
        :param data:
        :param index:
        :param index_mapping:
        :return:

        Parameters
        ----------
        nested_upsert
        """
        if index is None:
            index = self._default_index

        if index is None:
            raise ValueError(
                f"{self.tag}: No index name configured or passed at insert time!"
            )

        if isinstance(data, Dict):
            data = [data]

        return self.update(data=data, index=index, index_mapping=index_mapping)

    def ping(self):
        with self.connect() as client:
            ping = client.ping()
            if ping:
                print(
                    f"{self.tag}: Connection to ES {self._hostname_or_ip}:{self._port} successful!"
                )
            else:
                print(
                    f"{self.tag}: Connection to ES {self._hostname_or_ip}:{self._port} failed!"
                )
            return ping

    def delete_index(self, index: str):
        with self.connect() as client:
            if not client.indices.exists(index=index):
                print(f"{self.tag}: Index {index} not found, skipping deletion.")
                return None

            response = client.indices.delete(index=index, ignore=[400, 404])

            if response.get("acknowledged", False):
                print(f"{self.tag}: Index {index} deleted successfully.")
            elif "error" in response:
                print(
                    f"{self.tag}: Failed to delete index {index}: {response['error']['root_cause']}"
                )

    def create_index(self, index: str, mapping: Optional[Dict] = None):
        """
        # ToDo: Add settings
        """

        with self.connect() as client:
            if client.indices.exists(index=index):
                print(f"{self.tag}: Index {index} already exists, skipping creation.")
                return None

            response = client.indices.create(index=index, body=mapping, ignore=400)

            if response.get("acknowledged", False):
                print(f"{self.tag}: Index mapping success for index {index}.")
            elif "error" in response:
                raise ValueError(f"{self.tag}: Failed to map index {index}: {response}")

    def query(
        self,
        query: Union[Dict, str],
        size: int = 10,
        post_filter: Optional[Dict] = None,
        sort: Optional[Dict] = None,
        index: Optional[str] = None,
        min_score: Optional[float] = None,
        request_timeout: int = 60,
        **query_kwargs: Any,
    ):
        if index is None:
            index = self._default_index

        if index is None:
            raise ValueError(
                f"{self.tag}: No index name configured or passed at search time!"
            )

        if isinstance(query, str):
            query = json.loads(query)

        with self.connect() as client:
            page = client.search(
                index=index,
                size=size,
                query=query,
                post_filter=post_filter,
                sort=sort,
                min_score=min_score,
                request_timeout=request_timeout,
                track_total_hits=False,
                **query_kwargs,
            )

            for doc in page["hits"]["hits"]:
                yield doc

    def aggregate(
        self,
        query: Union[Dict, str],
        index: Optional[str] = None,
        min_score: Optional[float] = None,
        **query_kwargs: Any,
    ):
        if index is None:
            index = self._default_index

        if index is None:
            raise ValueError(
                f"{self.tag}: No index name configured or passed at search time!"
            )

        if isinstance(query, str):
            query = json.loads(query)

        with self.connect() as client:
            page = client.search(
                index=index, size=0, query=query, min_score=min_score, **query_kwargs
            )

            for doc in page["aggregations"]["values"]["buckets"]:
                yield doc

    def search(
        self,
        query: Union[Dict, str],
        page_size: int = 10,
        scroll_timeout: str = "5m",
        index: Optional[str] = None,
        min_score: Optional[float] = None,
        request_timeout: int = 60,
        **query_kwargs: Any,
    ):
        if index is None:
            index = self._default_index

        if index is None:
            raise ValueError(
                f"{self.tag}: No index name configured or passed at search time!"
            )

        if isinstance(query, str):
            query = json.loads(query)

        with self.connect() as client:
            page = client.search(
                index=index,
                scroll=scroll_timeout,
                size=page_size,
                query=query,
                min_score=min_score,
                request_timeout=request_timeout,
                **query_kwargs,
            )
            sid = page["_scroll_id"]
            scroll_size = page["hits"]["total"]["value"]
            page_counter = 0

            # Start scrolling
            while scroll_size > 0:
                # Get the number of results that we returned in the last scroll
                scroll_size = len(page["hits"]["hits"])
                if scroll_size > 0:
                    for doc in page["hits"]["hits"]:
                        yield doc

                # get next page
                page = client.scroll(scroll_id=sid, scroll="2m")
                page_counter += 1
                # Update the scroll ID
                sid = page["_scroll_id"]
