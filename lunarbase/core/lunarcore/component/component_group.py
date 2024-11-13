# SPDX-FileCopyrightText: Copyright © 2024 Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Danilo Gusicuma <danilo.gusicuma@idiap.ch>
#
# SPDX-License-Identifier: LicenseRef-lunarbase

from enum import Enum


class ComponentGroup(Enum):
    DATABASES = "Databases"
    GENAI = "GenAI"
    DATA_SCIENCE = "Data Science"
    CODERS = "Coders"
    DATA_EXTRACTION = "Data Extraction"
    DATA_VECTORIZERS = "Data Vectorizers"
    DATA_VISUALIZATION = "Data Visualization"
    DATA_TRANSFORMATION = "Data Transformation"
    IO = "IO"
    NLP = "NLP"
    API_TOOLS = "API Tools"
    CUSTOM = "Custom"
    CAUSAL_INFERENCE = "Causal Inference"
    BIOMEDICAL = "Bio-Medical"
    MUSICGEN = "MusicGen"
    UTILS = "Utilities"
    LUNAR = "Lunar"
    SERVICES = "Services"
    UNCLASSIFIED = "Unclassfied"

    def __repr__(self):
        return str(self.value)

    def __str__(self):
        return self.__repr__()
