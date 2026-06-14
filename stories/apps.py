from django.apps import AppConfig


class StoriesConfig(AppConfig):
    name = 'stories'

    def ready(self):
        from . import signals  # noqa: F401  (conecta los receivers)
