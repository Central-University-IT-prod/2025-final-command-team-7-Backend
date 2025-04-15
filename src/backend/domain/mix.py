import dataclasses
from typing import Any

from backend.domain.mix_id import MixId


@dataclasses.dataclass
class Mix:
    id: MixId
    title: str
    color1: str
    color2: str
    color3: str