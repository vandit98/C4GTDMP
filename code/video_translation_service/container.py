from dependency_injector import containers, providers
from .builder import new as new_video_processing_builder

class VideoProcessingServiceContainer(containers.DeclarativeContainer):
    video_processing_service_builder = providers.Resource(new_video_processing_builder)
