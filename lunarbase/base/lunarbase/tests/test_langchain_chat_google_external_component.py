import pytest


from lunarbase import LUNAR_CONTEXT


@pytest.mark.asyncio
async def test_langchain_google_chat(component_controller):
    """
    Assumes the existance of the LangChain's LangChainChatGoogleGenerativeAI external component in registry
    """
    component = LUNAR_CONTEXT.lunar_registry.get_by_class_name(
        "LangChainChatGoogleGenerativeAI"
    )

    component.component_model.configuration["model"] = "gemini-1.5-flash"
    component.component_model.configuration["google_api_key"] = "AIzaSyCpM1Ry3INlJIMR5DfXmV-MYWehmNQFElA"
    
    component.component_model.inputs[0].value = "Translate the following text to French: I am Lunar"

    result = await component_controller.run(component.component_model)
    result_value = result.get(component.component_model.label, dict()).get("output", dict()).get("value")

    assert result_value is not None and "Je suis Lunaire" in result_value
