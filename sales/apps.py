"""
Sales Management App Configuration

This module defines the configuration for the sales management app.
"""

from django.apps import AppConfig


class SalesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sales'
    verbose_name = 'Sales Management'

    def ready(self):
        """
        Perform any initialization when the app is ready.
        This is where you can import and register signals.
        """
        try:
            import sales.signals  # noqa
        except ImportError:
            pass
