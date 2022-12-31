from django.contrib import admin
from .models import Subject, Skill, SkillInst, Module, Lesson, Quiz, Question, Choice, QuizAnswer, QuestionAnswer

admin.site.register(Subject)
admin.site.register(Skill)
admin.site.register(SkillInst)
admin.site.register(Module)
admin.site.register(Lesson)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Choice)
admin.site.register(QuizAnswer)
admin.site.register(QuestionAnswer)
