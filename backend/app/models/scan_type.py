from enum import Enum

class ScanType(str, Enum):
    DOMAIN = "domain"
    IP = "ip"
    API = "api"
