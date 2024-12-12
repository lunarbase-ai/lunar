from uuid import uuid4

import pytest

from lunarbase.modeling.data_models import (
    ComponentModel,
    ComponentInput,
    ComponentOutput,
    WorkflowModel,
    ComponentDependency,
)
from lunarbase.tests.conftest import workflow_controller


@pytest.mark.asyncio
async def test_sparql_workflow(workflow_controller, sparql_datasource):
    wid = str(uuid4())
    components = [
        ComponentModel(
            workflow_id=wid,
            name="TextInput",
            class_name="TextInput",
            description="TextInput",
            group="IO",
            inputs=ComponentInput(
                key="input",
                data_type="TEMPLATE",
                value="PREFIX {prefix}\n {query}",
                template_variables={
                    "input.prefix": "rdfs: <http://www.w3.org/2000/01/rdf-schema#>",
                    "input.query": "SELECT ?label WHERE { <http://dbpedia.org/resource/Asturias> rdfs:label ?label }",
                },
            ),
            output=ComponentOutput(data_type="TEXT", value=None),
        ),
        ComponentModel(
            workflow_id=wid,
            name="Sparql Query",
            class_name="SPARQLQuery",
            description="SPARQL Query",
            group="DATABASES",
            inputs=[
                ComponentInput(
                    key="query",
                    data_type="TEXT",
                    value=None,
                ),
            ],
            output=ComponentOutput(data_type="JSON", value=None),
        ),
    ]
    workflow = WorkflowModel(
        id=wid,
        name="The SPARQL query",
        description="The SPARQL query",
        components=components,
        dependencies=[
            ComponentDependency(
                component_input_key="query",
                source_label=components[0].label,
                target_label=components[1].label,
                template_variable_key=None,
            ),
        ],
    )

    try:
        result = await workflow_controller.run(workflow, user_id=workflow_controller.config.DEFAULT_USER_PROFILE)
    finally:
        workflow_controller.delete(
            workflow.id, workflow_controller.config.DEFAULT_USER_PROFILE
        )
    result_value = (
        result.get(components[-1].label, dict()).get("output", dict()).get("value")
    )
    assert result_value is not None and result_value == "abcdr"
