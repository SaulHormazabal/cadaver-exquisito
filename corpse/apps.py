from django.apps import AppConfig


class CorpseConfig(AppConfig):
    name = 'corpse'

    def ready(self):
        from . import signals  # noqa: F401  (conecta los receivers)
