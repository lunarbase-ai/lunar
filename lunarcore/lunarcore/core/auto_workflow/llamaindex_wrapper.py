import json
import os

from llama_index.core import (
    Document,
    KeywordTableIndex,
    load_index_from_storage,
    ServiceContext,
    StorageContext,
    SummaryIndex,
    TreeIndex,
    VectorStoreIndex,
)
from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.retrievers.bm25 import BM25Retriever
from typing import Dict, List

from lunarcore.component_library import COMPONENT_REGISTRY
from lunarcore.core.auto_workflow import AutoWorkflow
from lunarcore.core.auto_workflow.config import (
    OPENAI_MODEL_NAME,
    OPENAI_API_VERSION,
    OPENAI_DEPLOYMENT_NAME,
    INDEX_TYPE,
    INDEX_ROOT_DIR,                       # TODO: add gitignore
    INDEX_PATH,
    INDEX_JSON_PATH,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_DEPLOYMENT_NAME,
)


class ComponentLlamaindexWrapper:
    def __init__(self):
        self.index = self.get_llamaindex()

    def get_llamaindex(self):
        index_data = self._index_data()
        if not os.path.exists(INDEX_JSON_PATH) or \
            json.dumps(index_data) != open(INDEX_JSON_PATH, 'r').read():
            self._build_llamaindex(index_data)

        api_key = os.environ.get('OPENAI_API_KEY', '')

        llm = AzureOpenAI(api_key=api_key, **index_data['llm_config'])
        embed_model = AzureOpenAIEmbedding(api_key=api_key, **index_data['embed_model_config'])

        service_context = ServiceContext.from_defaults(embed_model=embed_model, llm=llm)
        storage_context = StorageContext.from_defaults(persist_dir=INDEX_PATH)
        
        index = load_index_from_storage(
            storage_context, service_context=service_context
        )
        
        return index

    def _index_data(self):
        documents_data = self._components2documents_data()
        llm_config = self._llm_config()
        embed_model_config = self._embed_model_config()
        return {
            'documents_data': documents_data,
            'index_dir': INDEX_PATH,
            'index_type': INDEX_TYPE,
            'keys_list': ['components'],            # TODO: don't hardcode
            'llm_config': llm_config,
            'embed_model_config': embed_model_config
        }

    def _components2documents_data(self):
        documents_data = {}
        for component_model in COMPONENT_REGISTRY.components.values():
            component_name = component_model.class_name
            sb = []
            sb.append(f'Component name: {component_name}')
            sb.append(f'Component description: {component_model.description}')
            sb.append(f'Input labels: {AutoWorkflow._input_labels_str(component_model.inputs)}')
            component_str = '\n'.join(sb)
            documents_data[component_name] = {'component': component_str}
        return documents_data

    def _llm_config(self):
        llm_config = dict(
            model=OPENAI_MODEL_NAME,
            deployment_name=OPENAI_DEPLOYMENT_NAME,
            azure_endpoint=os.environ.get('AZURE_ENDPOINT'),
            api_version=OPENAI_API_VERSION
        )
        return llm_config
    
    def _embed_model_config(self):
        embed_model_config = dict(
            model=EMBEDDING_MODEL_NAME,
            deployment_name=EMBEDDING_DEPLOYMENT_NAME,
            azure_endpoint=os.environ.get('AZURE_ENDPOINT'),
            api_version=OPENAI_API_VERSION
        )
        return embed_model_config
    
    def _build_documents(self, documents_data):
        documents = []
        for document_dict in documents_data.values():
            documents.append(
                Document(
                    text=json.dumps(document_dict),
                )
            )
        return documents

    def _documents2index(self, index_type: str, documents: List[Document], service_context: ServiceContext):
        if index_type == 'summary':
            index = SummaryIndex.from_documents(documents, service_context=service_context)
        elif index_type == 'vector':
            index = VectorStoreIndex.from_documents(documents, service_context=service_context)
        elif index_type == 'keyword':
            index = KeywordTableIndex.from_documents(documents, service_context=service_context)
        else:
            index = TreeIndex.from_documents(documents, service_context=service_context)
        return index

    def _build_llamaindex(self, index_data: Dict, index_type: str = INDEX_TYPE):
        assert index_type in ['summary', 'vector', 'keyword', 'tree']
        
        keys_list = ['component']
        index_type = INDEX_TYPE
        os.makedirs(os.path.dirname(INDEX_ROOT_DIR), exist_ok=True)

        api_key=os.environ.get('OPENAI_API_KEY')

        llm = AzureOpenAI(api_key=api_key, **index_data['llm_config'])
        embed_model = AzureOpenAIEmbedding(api_key=api_key, **index_data['embed_model_config'])

        documents = self._build_documents(index_data['documents_data'])
        service_context = ServiceContext.from_defaults(
            embed_model=embed_model,
            llm=llm
        )
        index = self._documents2index(index_type, documents, service_context)
        index.storage_context.persist(persist_dir=INDEX_PATH)
        with open(INDEX_JSON_PATH, 'w') as index_json_file:
            json.dump(index_data, index_json_file)

    def query(self, query: str):
        query_engine = self.index.as_query_engine()
        response = query_engine.query(query)
        return response.response


if __name__ == '__main__':
    from dotenv import load_dotenv
    dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
    load_dotenv(dotenv_path)

    import asyncio
    asyncio.run(COMPONENT_REGISTRY.register(fetch=True))

    index_wrapper = ComponentLlamaindexWrapper()
    query = 'Select the most relevant components for a workflow reading a file and outputing its content reversed'
    response = index_wrapper.query(query)
    print(response)