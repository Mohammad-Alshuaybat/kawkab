from django.urls import path

from .views import subject_set, headline_set, build_quiz, marking, similar_questions, add_question_image, \
     add_question, report, save_question, unsave_question, quiz_review, retake_quiz

urlpatterns = [
     path('subject_set/', subject_set),
     path('headline_set/', headline_set),
     path('build_quiz/', build_quiz),
     path('marking/', marking),
     path('quiz_review/', quiz_review),
     path('report/', report),
     path('retake_quiz/', retake_quiz),
     path('add_question_image/', add_question_image),
     path('add_question/', add_question),
     path('similar_questions/', similar_questions),
     path('save_question/', save_question),
     path('unsave_question/', unsave_question),
]
