from enum import Enum

class Intent(str, Enum):
    locked_out = "locked_out"
    maintenance = "maintenance"
    rent = "rent"
    general = "general"
