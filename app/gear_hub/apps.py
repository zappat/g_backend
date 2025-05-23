from django.apps import AppConfig


class GearHubConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gear_hub'
    
    def ready(self):
        import gear_hub.signals
