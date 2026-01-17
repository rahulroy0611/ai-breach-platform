import re
from app.models.scan_type import ScanType

IP_REGEX = r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$"
DOMAIN_REGEX = r"^(?!-)[A-Za-z0-9-]{1,63}(?<!-)\.(?:[A-Za-z]{2,})$"
URL_REGEX = r"^https?://"

def detect_scan_type(target: str) -> ScanType:
    target = target.strip().lower()

    if re.match(IP_REGEX, target):
        return ScanType.IP

    if re.match(URL_REGEX, target):
        return ScanType.API  # future-ready

    if re.match(DOMAIN_REGEX, target):
        return ScanType.DOMAIN

    raise ValueError(f"Unable to detect scan type for target: {target}")
