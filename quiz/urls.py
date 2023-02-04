from django.urls import path
# from .views import subject_set, skill_set, module_set, build_quiz, marking, add_question, add_question_image, module_lesson_skill
from .views import read_skills_from_xlsx, read_modules_from_xlsx, read_lessons_from_xlsx, read_questions_from_xlsx, build_quiz, add_question_image, add_question
urlpatterns = [
     path('add_question_image/', add_question_image),
     path('add_question/', add_question),
     path('build_quiz/', build_quiz),
     path('read_questions_from_xlsx/', read_questions_from_xlsx),
     path('read_lessons_from_xlsx/', read_lessons_from_xlsx),
     path('read_modules_from_xlsx/', read_modules_from_xlsx),
     path('read_skills_from_xlsx/', read_skills_from_xlsx),
]
