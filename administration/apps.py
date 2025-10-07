"""Django app configuration for administration."""
from django.apps import AppConfig


class AdministrationConfig(AppConfig):
    """Configuration for the administration app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'administration'
    verbose_name = 'Administration'
