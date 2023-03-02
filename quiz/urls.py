from django.urls import path

from .views import similar_questions, build_quiz, add_question_image, add_question

urlpatterns = [
     path('add_question_image/', add_question_image),
     path('add_question/', add_question),
     path('build_quiz/', build_quiz),
     path('similar_questions/', similar_questions),
     # path('read_lessons_from_xlsx/', read_lessons_from_xlsx),
     # path('read_modules_from_xlsx/', read_modules_from_xlsx),
     # path('read_skills_from_xlsx/', read_skills_from_xlsx),

]
