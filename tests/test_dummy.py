# tests/test_dummy.py
from django.test import TestCase


class DummyTestCase(TestCase):
    def test_dummy(self):
        """Dummy test - always passes"""
        self.assertTrue(True)
