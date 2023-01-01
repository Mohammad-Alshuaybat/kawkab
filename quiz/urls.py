from django.urls import path
from .views import subject_set, skill_set, lesson_set, skills_quiz, lessons_quiz, add_question, add_question_image

urlpatterns = [
    path('subject_set/', subject_set),
    path('skill_set/', skill_set),
    path('lesson_set/', lesson_set),
    path('skills_quiz/', skills_quiz),
    path('lessons_quiz/', lessons_quiz),
    path('add_question/', add_question),
    path('add_question_image/', add_question_image),
]
