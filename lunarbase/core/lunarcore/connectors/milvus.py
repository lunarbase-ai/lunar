# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

import logging
from typing import Optional, Iterable, List, Any, Union, Dict
import uuid

from pymilvus import DataType

from lunarbase import Embedding
from pymilvus.orm.mutation import MutationResult

logger = logging.getLogger(__name__)

DEFAULT_MILVUS_CONNECTION = {
    "host": "127.0.0.1",
    "port": "19530",
    "user": "",
    "password": "",
    "secure": False,
}


def _create_connection_alias(connection_args: dict) -> str:
    """Create the connection to the Milvus server."""
    from pymilvus import MilvusException, connections

    # Grab the connection arguments that are used for checking existing connection
    host: Optional[str] = connection_args.get("host", None)
    port: Optional[Union[str, int]] = connection_args.get("port", None)
    address: Optional[str] = connection_args.get("address", None)
    uri: Optional[str] = connection_args.get("uri", None)
    user: Optional[str] = connection_args.get("user", None)

    # Order of use is host/port, uri, address
    if host is not None and port is not None:
        given_address = str(host) + ":" + str(port)
    elif uri is not None:
        given_address = uri.split("https://")[1]
    elif address is not None:
        given_address = address
    else:
        given_address = None
        logger.debug("Missing standard address type for reuse attempt")

    # User defaults to empty string when getting connection info
    if user is not None:
        tmp_user = user
    else:
        tmp_user = ""

    # If a valid address was given, then check if a connection exists
    if given_address is not None:
        for con in connections.list_connections():
            addr = connections.get_connection_addr(con[0])
            if (
                con[1]
                and ("address" in addr)
                and (addr["address"] == given_address)
                and ("user" in addr)
                and (addr["user"] == tmp_user)
            ):
                logger.debug("Using previous connection: %s", con[0])
                return con[0]

    # Generate a new connection if one doesn't exist
    alias = uuid.uuid4().hex
    try:
        connections.connect(alias=alias, **connection_args)
        logger.debug("Created new connection using: %s", alias)
        return alias
    except MilvusException as e:
        logger.error("Failed to create new connection using: %s", alias)
        raise e


class MilvusConnector:
    def __init__(
        self,
        collection_name: str,
        connection_args: Optional[dict[str, Any]] = None,
        index_params: Optional[dict] = None,
        consistency_level: str = "Session",
        search_params: Optional[dict] = None,
        drop_old: Optional[bool] = False,
        batch_size: int = 1000,
        insertion_timeout: Optional[int] = None,
    ):
        """Initialize the Milvus vector store."""
        try:
            from pymilvus import Collection, utility
        except ImportError:
            raise ValueError(
                "Could not import pymilvus python package. "
                "Please install it with `pip install pymilvus`."
            )

        self.default_search_params = {
            "IVF_FLAT": {"metric_type": "L2", "params": {"nprobe": 10}},
            "IVF_SQ8": {"metric_type": "L2", "params": {"nprobe": 10}},
            "IVF_PQ": {"metric_type": "L2", "params": {"nprobe": 10}},
            "HNSW": {"metric_type": "L2", "params": {"ef": 10}},
            "RHNSW_FLAT": {"metric_type": "L2", "params": {"ef": 10}},
            "RHNSW_SQ": {"metric_type": "L2", "params": {"ef": 10}},
            "RHNSW_PQ": {"metric_type": "L2", "params": {"ef": 10}},
            "IVF_HNSW": {"metric_type": "L2", "params": {"nprobe": 10, "ef": 10}},
            "ANNOY": {"metric_type": "L2", "params": {"search_k": 10}},
            "AUTOINDEX": {"metric_type": "L2", "params": {}},
        }

        self.collection_name = collection_name
        self.index_params = index_params
        self.search_params = search_params
        self.consistency_level = consistency_level

        self._primary_field = "pk"
        # In order for compatibility, the vector field needs to be called "vector"
        self._text_field = "text"
        self._vector_field = "vector"
        self.fields: list[str] = []
        # Create the connection to the server
        if connection_args is None:
            connection_args = DEFAULT_MILVUS_CONNECTION
        self.alias = _create_connection_alias(connection_args)
        self.col: Optional[Collection] = None

        self._batch_size = batch_size
        self._insertion_timeout = insertion_timeout

        # Grab the existing collection if it exists
        if utility.has_collection(self.collection_name, using=self.alias):
            self.col = Collection(
                self.collection_name,
                using=self.alias,
            )
        # If drop old is needed, drop it
        if drop_old and isinstance(self.col, Collection):
            self.col.drop()
            self.col = None

        # Initialize the vector store
        self._init()

    def _init(self, embeddings: Optional[list] = None) -> None:
        # if embeddings is not None:
        #     self._create_collection(embeddings)
        self._extract_fields()
        # self._create_index()
        self._create_search_params()
        # self._load()

    def _create_collection(self, embeddings: list) -> None:
        from pymilvus import (
            Collection,
            CollectionSchema,
            DataType,
            FieldSchema,
            MilvusException,
        )
        from pymilvus.orm.types import infer_dtype_bydata

        # Determine embedding dim
        dim = len(embeddings[0])
        fields = [
            FieldSchema(
                self._primary_field, DataType.INT64, is_primary=True, auto_id=True
            ),
            FieldSchema(self._text_field, DataType.VARCHAR, max_length=1500),
            FieldSchema(self._vector_field, infer_dtype_bydata(embeddings[0]), dim=dim),
        ]

        # Create the schema for the collection
        schema = CollectionSchema(fields)

        # Create the collection
        try:
            self.col = Collection(
                name=self.collection_name,
                schema=schema,
                consistency_level=self.consistency_level,
                using=self.alias,
            )
        except MilvusException as e:
            logger.error(
                "Failed to create collection: %s error: %s", self.collection_name, e
            )
            raise e

    def _extract_fields(self) -> None:
        """Grab the existing fields from the Collection"""
        from pymilvus import Collection

        if isinstance(self.col, Collection):
            schema = self.col.schema
            for x in schema.fields:
                if x.is_primary:
                    self._primary_field = x.name
                if x.dtype == DataType.FLOAT_VECTOR:
                    self._vector_field = x.name
                self.fields.append(x.name)

    def _get_index(self) -> Optional[dict[str, Any]]:
        """Return the vector index information if it exists"""
        from pymilvus import Collection

        if isinstance(self.col, Collection):
            for x in self.col.indexes:
                if x.field_name == self._vector_field:
                    return x.to_dict()
        return None

    def _create_index(self) -> None:
        """Create an index on the collection"""
        from pymilvus import Collection, MilvusException

        if isinstance(self.col, Collection) and self._get_index() is None:
            try:
                # If no index params, use a default HNSW based one
                if self.index_params is None:
                    self.index_params = {
                        "metric_type": "L2",
                        "index_type": "HNSW",
                        "params": {"M": 8, "efConstruction": 64},
                    }

                try:
                    self.col.create_index(
                        self._vector_field,
                        index_params=self.index_params,
                        using=self.alias,
                    )

                # If default did not work, most likely on Zilliz Cloud
                except MilvusException:
                    # Use AUTOINDEX based index
                    self.index_params = {
                        "metric_type": "L2",
                        "index_type": "AUTOINDEX",
                        "params": {},
                    }
                    self.col.create_index(
                        self._vector_field,
                        index_params=self.index_params,
                        using=self.alias,
                    )
                logger.debug(
                    "Successfully created an index on collection: %s",
                    self.collection_name,
                )

            except MilvusException as e:
                logger.error(
                    "Failed to create an index on collection: %s", self.collection_name
                )
                raise e

    def _create_search_params(self) -> None:
        """Generate search params based on the current index type"""
        from pymilvus import Collection

        if isinstance(self.col, Collection) and self.search_params is None:
            index = self._get_index()
            if index is not None:
                index_type: str = index["index_param"]["index_type"]
                metric_type: str = index["index_param"]["metric_type"]
                self.search_params = self.default_search_params[index_type]
                self.search_params["metric_type"] = metric_type

    def _load(self) -> None:
        """Load the collection if available."""
        from pymilvus import Collection

        if isinstance(self.col, Collection) and self._get_index() is not None:
            self.col.load()

    def get_num_entities(self):
        return self.col.num_entities

    def add_texts(
        self,
        texts: Iterable[str],
        embeddings: List[Embedding],
        metadatas: Optional[List[dict]] = None,
        **kwargs: Any,
    ) -> List[str]:
        from pymilvus import Collection, MilvusException

        texts = list(texts)

        if len(embeddings) == 0:
            logger.debug("Nothing to insert, skipping.")
            return []

        # If the collection hasn't been initialized yet, perform all steps to do so
        if not isinstance(self.col, Collection):
            self._init(embeddings)

        # Dict to hold all insert columns
        insert_dict: dict[str, list] = {
            self._text_field: texts,
            self._vector_field: embeddings,
        }

        # Collect the metadata into the insert dict.
        if metadatas is not None:
            for d in metadatas:
                for key, value in d.items():
                    if key in self.fields:
                        insert_dict.setdefault(key, []).append(value)

        # Total insert count
        vectors: list = insert_dict[self._vector_field]
        total_count = len(vectors)

        pks: list[str] = []

        assert isinstance(self.col, Collection)
        for i in range(0, total_count, self._batch_size):
            # Grab end index
            end = min(i + self._batch_size, total_count)
            # Convert dict to list of lists batch for insertion
            insert_list = [insert_dict[x][i:end] for x in self.fields if x != "Auto_id"]
            # Insert into the collection.
            try:
                res: MutationResult
                res = self.col.insert(
                    insert_list, timeout=self._insertion_timeout, **kwargs
                )
                pks.extend(res.primary_keys)
            except MilvusException as e:
                logger.error(
                    "Failed to insert batch starting at entity: %s/%s", i, total_count
                )
                raise e
        return pks

    def similarity_search_by_vector(
        self,
        embedding: List[float],
        k: int = 4,
        param: Optional[dict] = None,
        expr: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> List[str]:
        if self.col is None:
            logger.debug("No existing collection to search.")
            return []
        res = self.similarity_search_with_score_by_vector(
            embedding=embedding, k=k, param=param, expr=expr, timeout=timeout, **kwargs
        )
        return [doc for doc, _ in res]

    def similarity_search_with_score_by_vector(
        self,
        embedding: List[float],
        k: int = 4,
        param: Optional[dict] = None,
        expr: Optional[str] = None,
        timeout: Optional[int] = None,
        **kwargs: Any,
    ) -> List[Dict]:
        if self.col is None:
            logger.debug("No existing collection to search.")
            return []

        if param is None:
            param = self.search_params

        # Determine result metadata fields.
        output_fields = self.fields[:]
        output_fields.remove(self._vector_field)

        # Perform the search.
        res = self.col.search(
            data=[embedding],
            anns_field=self._vector_field,
            param=param,
            limit=k,
            expr=expr,
            output_fields=output_fields,
            timeout=timeout,
            **kwargs,
        )
        # Organize results.
        ret = []
        for result in res[0]:
            meta = {x: result.entity.get(x) for x in output_fields}
            meta.pop(self._primary_field)
            meta["result_score"] = result.score
            ret.append(meta)
        return ret
