from typing import Protocol, Any, Tuple
from service import _AudioProcessingServiceImpl, AudioProcessingService

class Builder(Protocol):
    def build(self) -> AudioProcessingService: ...

class _BuilderImpl:
    def build(self) -> AudioProcessingService:
        return _AudioProcessingServiceImpl()

def new() -> Builder:
    return _BuilderImpl()
