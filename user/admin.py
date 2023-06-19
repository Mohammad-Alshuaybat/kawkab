from django.contrib import admin
from import_export.admin import ExportActionMixin
from .models import User, DailyTask, Quote, Advertisement


class ExportAllFields(ExportActionMixin, admin.ModelAdmin):
    pass


class UserExportAllFields(ExportActionMixin, admin.ModelAdmin):
    list_display = ('firstName', 'lastName', 'creationDate', 'auth_method', 'email', 'phone', 'password', 'grade', 'section')
    ordering = ('-creationDate',)


admin.site.register(User, UserExportAllFields)
admin.site.register(DailyTask, ExportAllFields)
admin.site.register(Quote, ExportAllFields)
admin.site.register(Advertisement, ExportAllFields)
