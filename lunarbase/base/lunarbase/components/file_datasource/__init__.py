from lunarcore.component.component_group import ComponentGroup
from lunarcore.component.data_types import DataType
from lunarbase.modeling.datasources import DataSourceType
from lunarbase.ioc.container import LunarContainer
from lunarbase.components.system_component import SystemComponent

class FileDatasource(
    SystemComponent,
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
    
    def resolve_deps(self, container: LunarContainer):
        return {
            "datasource_controller": container.datasource_controller
        }

    def __init__(self, deps: dict, **kwargs):
        super().__init__(deps=deps, **kwargs)
        self.datasource_controller = deps.get("datasource_controller", None)
    
    def run(self, datasource: str):
        if self.datasource_controller is None:
            raise Exception("Failed accessing datasource controller")
        
        ds = self.datasource_controller.show("pedroparajogos1@gmail.com", datasource)

        if ds.type != DataSourceType.LOCAL_FILE:
            raise Exception("Datasource is not a local file datasource")
        
        return [file.file_name for file in ds.connection_attributes.files]