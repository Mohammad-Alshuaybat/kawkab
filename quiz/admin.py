from django.contrib import admin
from .models import Subject, Skill, SkillInst, Module, Lesson, Quiz, Question, Choice, QuizAnswer, QuestionAnswer
from import_export.admin import ExportActionMixin


class SkillAdmin(ExportActionMixin, admin.ModelAdmin):
    pass


class ChoiceAdmin(ExportActionMixin, admin.ModelAdmin):
    pass


class QuestionAdmin(ExportActionMixin, admin.ModelAdmin):
    pass


admin.site.register(Skill, SkillAdmin)

admin.site.register(Subject)
admin.site.register(SkillInst)
admin.site.register(Module)
admin.site.register(Lesson)
admin.site.register(Quiz)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)
admin.site.register(QuizAnswer)
admin.site.register(QuestionAnswer)

