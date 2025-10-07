"""Django app configuration for controllers."""
from django.apps import AppConfig


class ControllersConfig(AppConfig):
    """Configuration for the controllers app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'controllers'
    verbose_name = 'Online Course Controllers'
