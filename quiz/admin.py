from django.contrib import admin
from import_export.admin import ExportActionMixin

from .models import Subject, QuestionLevel, Module, Lesson, \
    AdminAnswer, UserAnswer, AdminFinalAnswer, UserFinalAnswer, AdminMultipleChoiceAnswer, \
    UserMultipleChoiceAnswer, FinalAnswerQuestion, MultipleChoiceQuestion, Solution, AdminQuiz, UserQuiz, Question, \
    HeadLine, H1, LastImageName, Author, HeadLineInst, SavedQuestion, Report, MultiSectionQuestion, \
    UserMultiSectionAnswer, WritingQuestion, UserWritingAnswer, Tag


class ExportAllFields(ExportActionMixin, admin.ModelAdmin):
    pass


class QuizExportAllFields(ExportActionMixin, admin.ModelAdmin):
    list_display = ('creationDate', 'user', 'subject', 'questions_num', 'duration')
    ordering = ('-creationDate',)

    def questions_num(self, obj):
        return UserAnswer.objects.filter(quiz=obj).count()


class UserWritingAnswerExportAllFields(ExportActionMixin, admin.ModelAdmin):
    list_display = ('creation_date', 'user', 'contact_info', 'status')
    ordering = ('status', '-quiz__creationDate',)

    def creation_date(self, obj):
        if obj.quiz:
            return obj.quiz.creationDate
        return None

    def user(self, obj):
        if obj.quiz:
            return obj.quiz.user
        return None

    def contact_info(self, obj):
        if obj.quiz:
            return obj.quiz.user.contact_method
        return None


class QuestionAdmin(ExportActionMixin, admin.ModelAdmin):
    search_fields = ['id', 'body', 'image']


admin.site.register(Question, QuestionAdmin)

admin.site.register(Subject, ExportAllFields)
admin.site.register(Module, ExportAllFields)
admin.site.register(Lesson, ExportAllFields)

admin.site.register(Author, ExportAllFields)

admin.site.register(QuestionLevel, ExportAllFields)
admin.site.register(H1, ExportAllFields)
admin.site.register(HeadLine, ExportAllFields)

admin.site.register(HeadLineInst, ExportAllFields)
admin.site.register(AdminFinalAnswer, ExportAllFields)


admin.site.register(LastImageName, ExportAllFields)
admin.site.register(Tag, ExportAllFields)
admin.site.register(MultiSectionQuestion, ExportAllFields)
admin.site.register(UserMultiSectionAnswer, ExportAllFields)
admin.site.register(WritingQuestion, ExportAllFields)
admin.site.register(UserWritingAnswer, UserWritingAnswerExportAllFields)
admin.site.register(UserFinalAnswer, ExportAllFields)
admin.site.register(AdminMultipleChoiceAnswer, ExportAllFields)
admin.site.register(UserMultipleChoiceAnswer, ExportAllFields)

admin.site.register(FinalAnswerQuestion, ExportAllFields)
admin.site.register(MultipleChoiceQuestion, ExportAllFields)

admin.site.register(Solution, ExportAllFields)
admin.site.register(Report, ExportAllFields)

admin.site.register(AdminQuiz, ExportAllFields)  # abstract

admin.site.register(UserQuiz, QuizExportAllFields)
admin.site.register(SavedQuestion, ExportAllFields)
