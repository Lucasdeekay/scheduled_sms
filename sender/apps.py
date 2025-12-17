from django.apps import AppConfig
class SenderConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sender'

    def ready(self):
        # make sure we run only once (manage.py runserver spawns 2 processes)
        import os
        if os.environ.get('RUN_MAIN', None) != 'true':
            return
        
        from .views import start_scheduler
        start_scheduler()