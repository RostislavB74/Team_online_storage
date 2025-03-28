from django.conf import settings
from django.core.files.storage import Storage
from django.utils.module_loading import import_string


def get_storage():
    """Dynamically loads the storage backend from settings."""
    storage_class = import_string(settings.DEFAULT_FILE_STORAGE)
    return storage_class()


class CustomStorage(Storage):
    def __init__(self, *args, **kwargs):
        self.backend = get_storage()
        super().__init__(*args, **kwargs)

    def _save(self, name, content):
        return self.backend._save(name, content)

    def url(self, name):
        return self.backend.url(name)
