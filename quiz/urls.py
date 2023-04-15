from django.urls import path

from .views import subject_set, headline_set, build_quiz, mark_quiz, similar_questions, \
     add_multiple_choice_question, add_multi_section_question, add_final_answer_question, report, save_question, unsave_question, quiz_review, retake_quiz, quiz_history, subject_question_num,\
     test

urlpatterns = [
     path('subject_set/', subject_set),
     path('headline_set/', headline_set),
     path('build_quiz/', build_quiz),
     path('marking/', mark_quiz),
     path('quiz_review/', quiz_review),
     path('report/', report),
     path('retake_quiz/', retake_quiz),
     path('add_multiple_choice_question/', add_multiple_choice_question),
     path('add_final_answer_question/', add_final_answer_question),
     path('add_multi_section_question/', add_multi_section_question),
     path('test/', test),
     path('similar_questions/', similar_questions),
     path('save_question/', save_question),
     path('unsave_question/', unsave_question),
     path('quiz_history/', quiz_history),
     path('subject_question_num/', subject_question_num),
     # path('read_headlines_from_xlsx/', read_headlines_from_xlsx),
]
