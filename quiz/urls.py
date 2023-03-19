from django.urls import path

from .views import subject_set, headline_set, module_set, build_quiz, marking, similar_questions, add_question_image, \
     add_question, report

urlpatterns = [
     path('subject_set/', subject_set),
     path('headline_set/', headline_set),
     path('module_set/', module_set),
     path('build_quiz/', build_quiz),
     path('marking/', marking),
     path('report/', report),

     path('add_question_image/', add_question_image),
     path('add_question/', add_question),
     path('similar_questions/', similar_questions),
     # path('read_modules_from_xlsx/', read_modules_from_xlsx),
     # path('read_skills_from_xlsx/', read_skills_from_xlsx),

]
