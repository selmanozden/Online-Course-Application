"""Django app configuration for models."""
from django.apps import AppConfig


class ModelsConfig(AppConfig):
    """Configuration for the models app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'models'
    verbose_name = 'Online Course Models'
    
    def ready(self):
        """Import models when app is ready."""
        # Import models to register them
        from . import user_model
        from . import course_model
        from . import content_model
        from . import exam_model
        from . import question_model
        from . import enrollment_model
        from . import progress_model

