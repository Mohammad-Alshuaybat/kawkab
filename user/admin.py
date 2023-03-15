from django.contrib import admin
from import_export.admin import ExportActionMixin
from .models import User, Report, DailyTask, Quote, Advertisement


class ExportAllFields(ExportActionMixin, admin.ModelAdmin):
    pass


admin.site.register(User, ExportAllFields)
admin.site.register(Report, ExportAllFields)
admin.site.register(DailyTask, ExportAllFields)
admin.site.register(Quote, ExportAllFields)
admin.site.register(Advertisement, ExportAllFields)
