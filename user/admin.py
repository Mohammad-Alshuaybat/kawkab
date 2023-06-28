from django.contrib import admin
from import_export.admin import ExportActionMixin

from quiz.models import UserQuiz
from .models import User, DailyTask, Quote, Advertisement


class ExportAllFields(ExportActionMixin, admin.ModelAdmin):
    pass


class UserExportAllFields(ExportActionMixin, admin.ModelAdmin):
    list_display = ('user_name', 'auth_method', 'account', 'quizzes_num', 'last_quiz', 'creationDate')
    ordering = ('-creationDate',)

    @staticmethod
    def user_name(obj):
        return obj

    @staticmethod
    def last_quiz(obj):
        if UserQuiz.objects.filter(user=obj).exists():
            return UserQuiz.objects.filter(user=obj).order_by('creationDate').last().creationDate
        else:
            return None

    @staticmethod
    def account(obj):
        if obj.email is not None:
            return obj.email
        elif obj.phone is not None:
            return obj.phone
        else:
            return None

    @staticmethod
    def quizzes_num(obj):
        return UserQuiz.objects.filter(user=obj).count()

# class UserWritingAnswerExportAllFields(ExportActionMixin, admin.ModelAdmin):
#     list_display = ('creation_date', 'user', 'contact_info', 'status')
#     ordering = ('status',)
#
#     def creation_date(self, obj):
#         if obj.quiz:
#             return obj.quiz.creationDate
#         return None


admin.site.register(User, UserExportAllFields)
admin.site.register(DailyTask, ExportAllFields)
admin.site.register(Quote, ExportAllFields)
admin.site.register(Advertisement, ExportAllFields)
