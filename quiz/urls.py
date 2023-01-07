from django.urls import path
from .views import subject_set, skill_set, lesson_set, build_quiz, marking, add_question, add_question_image

urlpatterns = [
    path('subject_set/', subject_set),
    path('skill_set/', skill_set),
    path('lesson_set/', lesson_set),
    path('build_quiz/', build_quiz),
    path('marking/', marking),
    path('add_question/', add_question),
    path('add_question_image/', add_question_image),
]
