#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
from uuid import uuid4

import pytest

from lunarbase.modeling.data_models import (
    ComponentModel,
    ComponentInput,
    ComponentOutput,
)


@pytest.mark.skip(reason="Should be reviewed")
@pytest.mark.asyncio
async def test_text_file_reader(component_controller, local_file_datasource):
    wid = str(uuid4())
    component = ComponentModel(
        workflow_id=wid,
        name="Text File Reader",
        class_name="TextFileReader",
        description="Text File Reader",
        group="IO",
        inputs=ComponentInput(
            key="input_file",
            data_type="File",
            value=local_file_datasource.id
        ),
        output=ComponentOutput(data_type="TEXT", value=None),
    )

    result = await component_controller.run(component)
    result_value = (
        result.get(component.label, dict()).get("output", dict()).get("value")
    )
    assert result_value is not None and result_value == "LUNAR"
