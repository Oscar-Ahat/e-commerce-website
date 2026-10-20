from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from django.contrib import admin
        admin.site.site_header = "Store Admin"
        admin.site.site_title = "Store Admin"
        admin.site.index_title = "Store Management"
