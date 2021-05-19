from enum import Enum


class DiscState(Enum):
    Vulnerable = "vuln"
    Safe = "SAFE"
    Gone = "----"
