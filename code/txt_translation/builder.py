from typing import Protocol
from .service import TextProcessingService, _TextProcessingServiceImpl

class Builder(Protocol):
    def build(self) -> TextProcessingService: ...

class _BuilderImpl:
    def build(self) -> TextProcessingService:
        return _TextProcessingServiceImpl()

def new() -> Builder:
    return _BuilderImpl()
