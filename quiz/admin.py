from django.contrib import admin
from import_export.admin import ExportActionMixin

from .models import Subject, QuestionLevel, Module, Lesson, \
    AdminAnswer, UserAnswer, AdminFinalAnswer, UserFinalAnswer, AdminMultipleChoiceAnswer, \
    UserMultipleChoiceAnswer, FinalAnswerQuestion, MultipleChoiceQuestion, Solution, AdminQuiz, UserQuiz, Question, \
    HeadLine, H1, LastImageName, Author, HeadLineInst, SavedQuestion, Report


class ExportAllFields(ExportActionMixin, admin.ModelAdmin):
    pass


admin.site.register(Subject, ExportAllFields)
admin.site.register(Module, ExportAllFields)
admin.site.register(Lesson, ExportAllFields)

admin.site.register(Author, ExportAllFields)

admin.site.register(QuestionLevel, ExportAllFields)
admin.site.register(H1, ExportAllFields)
admin.site.register(HeadLine, ExportAllFields)

admin.site.register(HeadLineInst, ExportAllFields)
admin.site.register(AdminFinalAnswer, ExportAllFields)


# admin.site.register(SkillInst, ExportAllFields)
# admin.site.register(Answer, ExportAllFields)  abstract
admin.site.register(UserFinalAnswer, ExportAllFields)
admin.site.register(AdminMultipleChoiceAnswer, ExportAllFields)
admin.site.register(UserMultipleChoiceAnswer, ExportAllFields)

admin.site.register(FinalAnswerQuestion, ExportAllFields)
admin.site.register(MultipleChoiceQuestion, ExportAllFields)

admin.site.register(Solution, ExportAllFields)
admin.site.register(Report, ExportAllFields)

admin.site.register(AdminQuiz, ExportAllFields)  # abstract

admin.site.register(UserQuiz, ExportAllFields)
admin.site.register(SavedQuestion, ExportAllFields)
