import sys
import os
import unittest
import base64
from unittest.mock import MagicMock

# Add repo root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.onvif_service import ONVIFService

class MockCamera:
    def __init__(self):
        self.id = 1
        self.uuid = "uuid-1234"
        self.name = "TestCamera"
        self.onvif_username = "admin"
        self.onvif_password = "password"
        self.assigned_ip = "127.0.0.1"
        self.onvif_port = 8000
        self.mac_address = "00:00:00:00:00:00"
        self.debug_mode = False
        self.ip_mode = "dhcp"
        self.main_width = 1920
        self.main_height = 1080
        self.sub_width = 640
        self.sub_height = 480
        self.main_framerate = 30
        self.sub_framerate = 15
        self.path_name = "cam1"
        self.rtsp_port = 8554

class TestAuthCache(unittest.TestCase):
    def setUp(self):
        self.camera = MockCamera()
        self.service = ONVIFService(self.camera)
        self.app = self.service.create_app()
        self.client = self.app.test_client()

    def test_auth_flow(self):
        # 1. Request without auth -> 401
        print("Testing: No Auth -> Expect 401")
        resp = self.client.post('/onvif/device_service', data='<soap>GetDeviceInformation</soap>')
        self.assertEqual(resp.status_code, 401)

        # 2. Request with valid Basic Auth -> 200
        print("Testing: Basic Auth -> Expect 200")
        creds = base64.b64encode(b"admin:password").decode('utf-8')
        headers = {'Authorization': f'Basic {creds}'}
        resp = self.client.post('/onvif/device_service',
                                data='<soap>GetDeviceInformation</soap>',
                                headers=headers)
        self.assertEqual(resp.status_code, 200)

        # 3. Request without auth again -> Should be 200 due to cache
        print("Testing: No Auth (Cached) -> Expect 200")
        resp = self.client.post('/onvif/device_service', data='<soap>GetDeviceInformation</soap>')
        self.assertEqual(resp.status_code, 200, "Should be 200 due to auth cache")
        print("SUCCESS: Auth cache worked")

if __name__ == '__main__':
    unittest.main()
