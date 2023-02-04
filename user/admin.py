from django.contrib import admin
from import_export.admin import ExportActionMixin
from .models import User


class ExportAllFields(ExportActionMixin, admin.ModelAdmin):
    pass


admin.site.register(User, ExportAllFields)
