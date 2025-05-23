from lunarcore.component.component_group import ComponentGroup
from lunarcore.component.lunar_component import LunarComponent
from lunarcore.component.data_types import DataType

class FileDatasource(
    LunarComponent,
    component_name="FileDataSource",
    component_description="""Component for reading files from a file datasource

        Inputs:
            - datasourceId: the id of the datasource to read from

        Outputs (List[File]): the files in the datasource
        """,
    input_types={"datasource": DataType.DATASOURCE},
    output_type=DataType.LIST,
    component_group=ComponentGroup.LUNAR,
):

    def __init__(self, **kwargs):
        super().__init__(configuration=kwargs)

    def run(self, datasource: str):
        return [datasource]