from dependency_injector import containers, providers
from .builder import new as new_pdf_processing_builder

class PdfProcessingServiceContainer(containers.DeclarativeContainer):
    pdf_processing_service_builder = providers.Resource(new_pdf_processing_builder)
