from typing import Protocol
from .service import PdfProcessingService, _PDFProcessingServiceImpl

class Builder(Protocol):
    def build(self) -> PdfProcessingService: ...

class _BuilderImpl:
    def build(self) -> PdfProcessingService:
        return _PDFProcessingServiceImpl()

def new() -> Builder:
    return _BuilderImpl()
