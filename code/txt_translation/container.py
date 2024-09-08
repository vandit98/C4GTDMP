from dependency_injector import containers, providers
from .builder import new as new_txt_processing_builder

class TxtProcessingServiceContainer(containers.DeclarativeContainer):
    txt_processing_service_builder = providers.Resource(new_txt_processing_builder)
