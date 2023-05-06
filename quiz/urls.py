from django.urls import path

from .views import subject_set, headline_set, build_quiz, mark_quiz, similar_questions, \
     add_multiple_choice_question, add_multi_section_question, add_final_answer_question, report, save_question, \
     unsave_question, quiz_review, retake_quiz, quiz_history, subject_question_num, \
     test, test1, edit_multi_section_question, edit_final_answer_question, edit_multiple_choice_question,\
     get_admin_question, subject_question_ids

urlpatterns = [
     path('subject_set/', subject_set),
     path('headline_set/', headline_set),
     path('build_quiz/', build_quiz),
     path('marking/', mark_quiz),
     path('quiz_review/', quiz_review),
     path('report/', report),
     path('retake_quiz/', retake_quiz),
     path('subject_question_ids/', subject_question_ids),
     path('add_multiple_choice_question/', add_multiple_choice_question),
     path('add_final_answer_question/', add_final_answer_question),
     path('add_multi_section_question/', add_multi_section_question),
     path('get_admin_question/', get_admin_question),
     # path('add_final_answer_question/', add_final_answer_question),
     # path('add_multi_section_question/', add_multi_section_question),
     path('edit_multi_section_question/', edit_multi_section_question),
     path('edit_final_answer_question/', edit_final_answer_question),
     path('edit_multiple_choice_question/', edit_multiple_choice_question),
     path('test/', test),
     path('test1/', test1),
     path('similar_questions/', similar_questions),
     path('save_question/', save_question),
     path('unsave_question/', unsave_question),
     path('quiz_history/', quiz_history),
     path('subject_question_num/', subject_question_num),
     # path('read_headlines_from_xlsx/', read_headlines_from_xlsx),
]
