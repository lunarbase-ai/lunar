import pytest


from lunarbase import LUNAR_CONTEXT


@pytest.mark.asyncio
async def test_langchain_csvloader(component_controller):
    """
    Assumes the existance of the LangChain's CSVLoader external component in registry
    """
    component = LUNAR_CONTEXT.lunar_registry.get_by_class_name(
        "LangChainCSVLoader"
    )

    component.component_model.configuration["file_path"] = "/tmp/hw200.csv"
    component.component_model.configuration["csv_args"] = {
                "delimiter": ",",
                "quotechar": '"',
                "fieldnames": ["Index", "Height", "Weight"],
            }

    result = await component_controller.run(component.component_model)
    result_value = result.get(component.component_model.label, dict()).get("output", dict()).get("value")

    assert result_value is not None and result_value[0]["kwargs"] == "abcdr"
