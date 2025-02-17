from enum import Enum


class ConfigurationProfileType(Enum):
    LOCAL_FILE = "LocalFile"
    DATA_SOURCE = "DataSource"
    LLM = "LLM"