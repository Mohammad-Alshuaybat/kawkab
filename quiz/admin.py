from django.contrib import admin
from import_export.admin import ExportActionMixin
from .models import Subject, Skill, GeneralSkill, QuestionLevel, SkillInst, Module, Lesson, \
    AdminAnswer, UserAnswer, AdminFinalAnswer, UserFinalAnswer, AdminMultipleChoiceAnswer, \
    UserMultipleChoiceAnswer, FinalAnswerQuestion, MultipleChoiceQuestion, Solution, AdminQuiz, UserQuiz, Question


class ExportAllFields(ExportActionMixin, admin.ModelAdmin):
    pass


admin.site.register(Subject, ExportAllFields)
# admin.site.register(Tag, ExportAllFields)  abstract
admin.site.register(Skill, ExportAllFields)
admin.site.register(GeneralSkill, ExportAllFields)
admin.site.register(QuestionLevel, ExportAllFields)
admin.site.register(SkillInst, ExportAllFields)
admin.site.register(Module, ExportAllFields)
admin.site.register(Lesson, ExportAllFields)
# admin.site.register(Answer, ExportAllFields)  abstract
admin.site.register(AdminAnswer, ExportAllFields)
admin.site.register(UserAnswer, ExportAllFields)
admin.site.register(AdminFinalAnswer, ExportAllFields)
admin.site.register(UserFinalAnswer, ExportAllFields)
admin.site.register(AdminMultipleChoiceAnswer, ExportAllFields)
admin.site.register(UserMultipleChoiceAnswer, ExportAllFields)
admin.site.register(Question, ExportAllFields)  # abstract
admin.site.register(FinalAnswerQuestion, ExportAllFields)
admin.site.register(MultipleChoiceQuestion, ExportAllFields)
admin.site.register(Solution, ExportAllFields)
# admin.site.register(Quiz, ExportAllFields)  abstract
admin.site.register(AdminQuiz, ExportAllFields)
admin.site.register(UserQuiz, ExportAllFields)
