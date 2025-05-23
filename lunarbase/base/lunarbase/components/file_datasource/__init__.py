from lunarcore.component.component_group import ComponentGroup
from lunarcore.component.lunar_component import LunarComponent
from lunarcore.component.data_types import DataType
from lunarbase.modeling.datasources import DataSourceType

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
    datasource_controller=None,
):

    def __init__(self, **kwargs):
        super().__init__(configuration=kwargs)

        self.datasource_controller = self.configuration.get("datasource_controller", None)

    def run(self, datasource: str):
        if self.datasource_controller is None:
            raise Exception("Failed accessing datasource controller")
        
        ds = self.datasource_controller.show("pedroparajogos1@gmail.com", datasource)

        if ds.type != DataSourceType.LOCAL_FILE:
            raise Exception("Datasource is not a local file datasource")
        
        # Convert the files to a serializable format
        return [file.model_dump() for file in ds.connection_attributes.files]