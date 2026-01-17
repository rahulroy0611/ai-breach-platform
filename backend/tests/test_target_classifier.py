from app.core.target_classifier import detect_scan_type
from app.models.scan_type import ScanType

def test_detect_domain():
    assert detect_scan_type("example.com") == ScanType.DOMAIN

def test_detect_ip():
    assert detect_scan_type("8.8.8.8") == ScanType.IP
