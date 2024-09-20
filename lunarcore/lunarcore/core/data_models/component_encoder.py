# SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import json
from typing import Any

import numpy as np
from pydantic import BaseModel

from lunarcore.core.typings.components import ComponentGroup
from lunarcore.core.typings.datatypes import DataType
from lunarcore.errors import ComponentError


class ComponentEncoder(json.JSONEncoder):
    """Custom encoder for special data types"""

    def default(self, obj):
        if isinstance(obj, DataType):
            return str(obj.name)

        elif isinstance(obj, ComponentGroup):
            return str(obj.name)

        elif isinstance(obj, BaseModel):
            return obj.model_dump()

        elif isinstance(obj, datetime.date):
            return str(obj)

        elif type(obj).__name__ == "Timestamp":
            return str(obj)

        elif isinstance(obj, ComponentError):
            return str(obj)

        elif isinstance(
            obj,
            (
                np.int_,
                np.intc,
                np.intp,
                np.int8,
                np.int16,
                np.int32,
                np.int64,
                np.uint8,
                np.uint16,
                np.uint32,
                np.uint64,
            ),
        ):
            return int(obj)

        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)

        elif isinstance(obj, (np.complex_, np.complex64, np.complex128)):
            return {"real": obj.real, "imag": obj.imag}

        elif isinstance(obj, np.ndarray):
            return obj.tolist()

        elif isinstance(obj, np.bool_):
            return bool(obj)

        elif isinstance(obj, np.void):
            return None

        return json.JSONEncoder.default(self, obj)


def component_json_dumps(obj: object, **dumps_kwargs: Any):
    _kwargs = {**dumps_kwargs, "cls": ComponentEncoder}
    return json.dumps(obj, **_kwargs)
