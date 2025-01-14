from enum import Enum

from lunarcore.data_sources.attributes import LocalFileConnectionAttributes, PostgresqlConnectionAttributes, \
    SparqlConnectionAttributes


class DataSourceType(Enum):
    # Keep the values consistent with the DataSource class types
    LOCAL_FILE = "LocalFile"
    POSTGRESQL = "Postgresql"
    SPARQL = "Sparql"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    def expected_connection_attributes(self):
        if self == DataSourceType.LOCAL_FILE:
            return LocalFileConnectionAttributes, [
                field_name
                for field_name, filed_info in LocalFileConnectionAttributes.model_fields.items()
                if filed_info.is_required()
            ]
        elif self == DataSourceType.POSTGRESQL:
            return PostgresqlConnectionAttributes, [
                field_name
                for field_name, filed_info in PostgresqlConnectionAttributes.model_fields.items()
                if filed_info.is_required()
            ]
        elif self == DataSourceType.SPARQL:
            return SparqlConnectionAttributes, [
                field_name
                for field_name, filed_info in SparqlConnectionAttributes.model_fields.items()
                if filed_info.is_required()
            ]
        else:
            return None, []
