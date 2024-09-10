from dependency_injector import containers, providers
from builder import new as new_audio_processing_service_builder

class AudioProcessingServiceContainer(containers.DeclarativeContainer):
    audio_processing_service_builder = providers.Resource(new_audio_processing_service_builder)
