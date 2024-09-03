from typing import Protocol
from .service import VideoProcessingService, _VideoProcessingServiceImpl

class Builder(Protocol):
    def build(self) -> VideoProcessingService: ...

class _BuilderImpl:
    def build(self) -> VideoProcessingService:
        return _VideoProcessingServiceImpl()

def new() -> Builder:
    return _BuilderImpl()
