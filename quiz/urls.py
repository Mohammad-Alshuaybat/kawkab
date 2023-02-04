from django.urls import path
# from .views import subject_set, skill_set, module_set, build_quiz, marking, add_question, add_question_image, module_lesson_skill
from .views import build_quiz, add_question_image, add_question
urlpatterns = [
     path('add_question_image/', add_question_image),
     path('add_question/', add_question),
     path('build_quiz/', build_quiz)
]
