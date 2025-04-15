import dataclasses
import uuid


@dataclasses.dataclass
class GradientColor:
    id: uuid.UUID
    entity_id: uuid.UUID
    color1: str
    color2: str
