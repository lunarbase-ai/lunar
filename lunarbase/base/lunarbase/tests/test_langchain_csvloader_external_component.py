import pytest


from lunarbase import LUNAR_CONTEXT


@pytest.mark.asyncio
async def test_langchain_csvloader(component_controller):
    """
    Assumes the existance of the LangChain's CSVLoader external component in registry
    """
    component = LUNAR_CONTEXT.lunar_registry.get_by_class_name(
        "CSVLoaderLunarIntegration"
    )
    for i, ci in enumerate(component.component_model.inputs):
        if ci.key == "file_path":
            component.component_model.inputs[i].value = "/tmp/hw200.csv"
        elif ci.key == "csv_args":
            component.component_model.inputs[i].value = {
                "delimiter": ",",
                "quotechar": '"',
                "fieldnames": ["Index", "Height", "Weight"],
            }

    result = await component_controller.run(component.component_model)
    result_value = result.get(component.component_model.label, dict()).get("output", dict()).get("value")
    assert result_value is not None and result_value == "abcdr"
