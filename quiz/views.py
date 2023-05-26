import base64

from django.core.files.base import ContentFile
from django.core.mail import send_mail
from rest_framework.decorators import api_view
from rest_framework.response import Response

from school import settings
from user.utils import check_user, get_user
from .models import Subject, Module, Question, Lesson, FinalAnswerQuestion, AdminFinalAnswer, \
    MultipleChoiceQuestion, AdminMultipleChoiceAnswer, QuestionLevel, H1, HeadLine, HeadBase, UserFinalAnswer, \
    UserMultipleChoiceAnswer, UserQuiz, Author, LastImageName, Report, SavedQuestion, UserAnswer, MultiSectionQuestion, \
    UserMultiSectionAnswer
from .serializers import ModuleSerializer, QuestionSerializer, UserAnswerSerializer

from django.db.models import Count, Q, Sum

import random
import datetime

# import pandas as pd
from .utils import mark_final_answer_question, mark_multiple_choice_question, mark_multi_section_question, \
    review_final_answer_question, review_multi_choice_question, review_multi_section_question, questions_statistics_statement


@api_view(['POST'])
def subject_set(request):
    data = request.data

    if check_user(data):
        user = get_user(data)
        subjects = Subject.objects.filter(grade=user.grade).values('id', 'name')
        return Response(subjects)

    else:
        return Response(0)


@api_view(['POST'])
def headline_set(request):
    data = request.data
    subject_id = data.pop('subject_id', None)

    if check_user(data):
        subject = Subject.objects.get(id=subject_id)
        headlines = subject.get_main_headlines().values('id', 'name')

        modules = Module.objects.filter(subject=subject)
        module_serializer = ModuleSerializer(modules, many=True).data
        return Response({'modules': module_serializer, 'headlines': headlines})
    else:
        return Response(0)


@api_view(['POST'])
def build_quiz(request):
    def weight_module(h1s, question_number):
        modules = Module.objects.annotate(
            num_h1s=Count('lesson__h1', distinct=True),
            num_common_h1s=Count('lesson__h1', filter=Q(lesson__h1__in=h1s), distinct=True)
        ).filter(num_h1s__gt=0)

        module_weights = {}
        for module in modules:
            if module.num_common_h1s > 0:
                module_weights[module.id] = module.num_common_h1s / module.num_h1s

        sum_weights = sum(module_weights.values())
        module_weights = {module: round(weight / sum_weights * question_number) for module, weight in
                          module_weights.items()}

        return module_weights

    def weight_lessons(h1s):
        lessons = Lesson.objects.annotate(
            num_h1s=Count('h1', distinct=True),
            num_common_h1s=Count('h1', filter=Q(h1__in=h1s), distinct=True)
        ).filter(num_h1s__gt=0)

        lesson_weights = {}
        for lesson in lessons:
            if lesson.num_common_h1s > 0:
                lesson_weights[str(lesson.id)] = lesson.num_common_h1s / lesson.num_h1s

        return lesson_weights

    def lesson_module(module_ques, lesson_weights):
        modules_lessons = {}
        modules_lessons_weights = {}

        lessons = set(Lesson.objects.filter(id__in=lesson_weights.keys()))

        for module in module_ques.keys():
            modules_lessons[module] = lessons.intersection(Module.objects.get(id=module).lesson_set.all())

        for module, module_lessons in modules_lessons.items():
            modules_lessons_weights[module] = {
                'lessons': {str(lesson.id): lesson_weights[str(lesson.id)] for lesson in module_lessons if
                            str(lesson.id) in lesson_weights.keys()},
                'weight': module_ques[module]}

        return modules_lessons_weights

    def normalize_lessons_weight(modules_lessons_weights):
        for module, lessons_weight in modules_lessons_weights.items():
            total_lesson_weights = sum(lessons_weight['lessons'].values())
            lessons_weight['lessons'] = {lesson: round(weight / total_lesson_weights * lessons_weight['weight']) for
                                         lesson, weight in lessons_weight['lessons'].items()}
        return modules_lessons_weights

    def lesson_headlines(lesson_weight, h1s):
        lesson_headline = {}

        for lesson in lesson_weight.keys():
            lesson_headline[lesson] = h1s.intersection(
                Lesson.objects.get(id=lesson).get_main_headlines()).values_list('id', flat=True)

        for lesson, h1s in lesson_headline.items():
            h2s = HeadLine.objects.filter(parent_headline__in=h1s).values_list('id', flat=True)
            h3s = HeadLine.objects.filter(parent_headline__in=h2s).values_list('id', flat=True)
            h4s = HeadLine.objects.filter(parent_headline__in=h3s).values_list('id', flat=True)
            h5s = HeadLine.objects.filter(parent_headline__in=h4s).values_list('id', flat=True)
            headlines = list(set(h1s) | set(h2s) | set(h3s) | set(h4s) | set(h5s))
            random.shuffle(headlines)
            lesson_headline[lesson] = headlines

        return lesson_headline

    def quiz_level(level, number_of_question):  # 1-->easy, 2-->default, 3-->hard
        if level == 1:
            return [QuestionLevel.objects.get(name='easy')] * number_of_question
        elif level == 2:
            return random.shuffle(
                [QuestionLevel.objects.get(name='hard')] * number_of_question // 3 +
                [QuestionLevel.objects.get(name='inAverage')] * number_of_question // 3 +
                [QuestionLevel.objects.get(name='easy')] * (number_of_question - 2 * number_of_question // 3))
        elif level == 3:
            return [QuestionLevel.objects.get(name='hard')] * number_of_question
        else:
            return []

    def get_questions(lesson_headline, modules_lessons_normalized_weights, quiz_level=[]):
        """
        lesson_headline = {    # here headlines are from all levels 1-5
            'lesson1': {h1, h2, h3},
            'lesson2': {h1},
            'lesson3': {h1, h2, h3, h4},
            'lesson4': {h1, h2, h3, h4}
        }

        modules_lessons_normalized_weights = {    # all weights and question num here depend on quiz consist of 20 question
            'module1': {'lessons': {'lesson1': 10, 'lesson2': 5}, 'weight': 14.285714285714286},
            'module2': {'lessons': {'lesson1': 3, 'lesson2': 2}, 'weight': 5.714285714285715}
        }
        """

        question_set = set()

        for module, lessons_weight in modules_lessons_normalized_weights.items():
            for lesson, question_num in lessons_weight['lessons'].items():
                headline_counter = 0
                temp_question_set = set()
                while len(temp_question_set) < question_num:
                    headline = list(lesson_headline[lesson])[headline_counter % len(lesson_headline[lesson])]

                    _questions = Question.objects.filter(tags=headline, sub=False)  # .filter(tags=quiz_level[0])
                    # quiz_level.pop(quiz_level[0])
                    if _questions:
                        temp_question_set.add(random.choice(_questions))
                    headline_counter += 1
                    if headline_counter > question_num * 10:
                        break
                question_set |= temp_question_set
        serializer = QuestionSerializer(question_set, many=True)
        return serializer.data

    data = request.data
    h1_ids = data.pop('headlines', None)
    question_number = data.pop('question_num', None)
    quiz_level = data.pop('quiz_level', None)

    if check_user(data):
        h1s = H1.objects.filter(id__in=h1_ids)

        weighted_modules = weight_module(h1s, question_number)
        weighted_lessons = weight_lessons(h1s)
        lesson_headline = lesson_headlines(weighted_lessons, h1s)
        # print(lesson_headline)
        modules_lessons_weights = lesson_module(weighted_modules, weighted_lessons)
        modules_lessons_normalized_weights = normalize_lessons_weight(modules_lessons_weights)
        # print(modules_lessons_normalized_weights)
        # level = quiz_level(quiz_level, question_number)
        questions = get_questions(lesson_headline, modules_lessons_normalized_weights)

        return Response(questions)


    else:
        return Response(0)


@api_view(['POST'])
def mark_quiz(request):
    data = request.data

    answers = data.pop('answers', None)
    subject = data.pop('subject', None)
    quiz_duration = data.pop('quiz_duration', None)

    if check_user(data):
        user = get_user(data)

        attempt_duration = 0
        ideal_duration = 0
        question_num = 0
        correct_questions = 0
        modules = {}
        lessons = {}
        h1s = {}

        subject = Subject.objects.get(id=subject)
        quiz = UserQuiz.objects.create(subject=subject, user=user,
                                       duration=datetime.timedelta(seconds=int(quiz_duration)) if quiz_duration is not None else None)
        for ID, ans in answers.items():
            question = Question.objects.get(id=ID)
            if hasattr(question, 'finalanswerquestion'):
                _, correct_questions, ideal_duration, attempt_duration, modules, lessons, h1s = mark_final_answer_question(quiz, question, ans, correct_questions, ideal_duration, attempt_duration, modules, lessons, h1s, False)

            elif hasattr(question, 'multiplechoicequestion'):
                _, correct_questions, ideal_duration, attempt_duration, modules, lessons, h1s = mark_multiple_choice_question(quiz, question, ans, correct_questions, ideal_duration, attempt_duration, modules, lessons, h1s, False)

            elif hasattr(question, 'multisectionquestion'):
                correct_questions, ideal_duration, attempt_duration, modules, lessons, h1s = mark_multi_section_question(quiz, question, ans, correct_questions, ideal_duration, attempt_duration, modules, lessons, h1s, False)
                question_num += question.multisectionquestion.sub_questions.count() - 1
        skills = sorted(modules.items() if len(modules) > 5 else lessons.items() if len(lessons) > 5 else h1s.items(),
                        key=lambda x: (x[1]['correct'] + x[1]['all'], x[1]['correct']), reverse=True)
        best_worst_skills = dict(list(skills[:3]) + list(skills[-2:]))

        ideal_duration = "{}".format(str(datetime.timedelta(seconds=round(ideal_duration))))
        attempt_duration = "{}".format(str(datetime.timedelta(seconds=round(attempt_duration))))

        return Response({'total_question_num': len(answers) + question_num, 'correct_questions': correct_questions,
                         'ideal_duration': ideal_duration, 'attempt_duration': attempt_duration,
                         'quiz_id': quiz.id, 'best_worst_skills': best_worst_skills})
    else:
        return Response(0)
# {
#     "email": "abood@gmail.com",
#     "password": "123",
#     "subject": "8c932220-8ef1-4f9e-a730-377cedae1cc4",
#     "answers": {
#         "2399c20d-756f-41fc-839b-4d705040960b": {"duration": 11, "answer": {"849aafba-6264-4385-89d0-b81a45f2bfe8": "e8b4ff42-f106-41df-8284-1b80661a02ae", "86ee4141-2d52-4665-ade0-a057ed16140e": "002863fc-bee4-49ae-9171-a96e21957169"}},
#         "bf406450-33dd-41b6-9fd6-3513572c2d79": {"duration": 8, "answer": "38b7d47f-35fa-425d-9ec1-a249a3f1e358"},
#         "4f872a59-af7b-4880-9aaf-e3c70016bb7d": {"duration": 4, "answer": "a0ad3801-6f87-470b-be4d-fddb7805020d"}
#     },
#      "quiz_duration": 300
# }


@api_view(['POST'])
def mark_question(request):
    data = request.data
    answers = data.pop('answers', None)

    if check_user(data):  # TODO: user name
        question_status = False
        for ID, ans in answers.items():
            question = Question.objects.get(id=ID)
            if hasattr(question, 'finalanswerquestion'):
                answer = mark_final_answer_question(None, question, ans, None, None, None, None, None, None, True)
                question_status = answer == question.finalanswerquestion.correct_answer

            elif hasattr(question, 'multiplechoicequestion'):
                answer = mark_multiple_choice_question(None, question, ans, None, None, None, None, None, None, True)
                question_status = answer == question.multiplechoicequestion.correct_answer

            elif hasattr(question, 'multisectionquestion'):
                question_status = mark_multi_section_question(None, question, ans, None, None, None, None, None, None, True)

            # if ans.get('answer', None) is None:
            #     return Response(False)
        return Response(question_status)
    else:
        return Response(0)


@api_view(['POST'])
def retake_quiz(request):
    data = request.data
    quiz_id = data.pop('quiz_id', None)

    if check_user(data):
        quiz = UserQuiz.objects.get(id=quiz_id)
        question_set = Question.objects.filter(useranswer__quiz=quiz)
        serializer = QuestionSerializer(question_set, many=True)
        return Response(serializer.data)
    else:
        return Response(0)


@api_view(['POST'])
def similar_questions(request):
    def similar_by_headline(question, question_weight):
        levels_weight = [21, 15, 10, 6, 3, 1, 0]
        # get lesson
        tags = question.tags.exclude(headbase=None)
        for tag in tags:
            tag = tag.headbase
            main_headline = tag.h1 if hasattr(tag, 'h1') else tag.headline

            while hasattr(tag, 'headline'):
                tag = tag.headline.parent_headline
            lesson = tag.h1.lesson

            # add headlines questions
            headlines = lesson.get_all_headlines()
            questions = Question.objects.filter(tags__in=headlines, sub=False)
            for question in questions:
                question_weight[str(question.id)] = question_weight.get(str(question.id), 0)

            # weight the headlines
            weighted_headlines = {levels_weight[0]: {main_headline}}
            wastes_headlines = weighted_headlines[levels_weight[0]]

            weighted_headlines[levels_weight[1]] = set(main_headline.get_all_child_headlines())
            wastes_headlines |= weighted_headlines[levels_weight[1]]

            similarity_level = 2
            while hasattr(main_headline, 'parent_headline'):
                main_headline = main_headline.parent_headline
                main_headline = main_headline.h1 if hasattr(main_headline, 'h1') else main_headline.headline

                weighted_headlines[levels_weight[similarity_level]] = (set(main_headline.get_all_child_headlines()) | {main_headline}) - wastes_headlines
                wastes_headlines |= weighted_headlines[levels_weight[similarity_level]]

                similarity_level += 1

            weighted_headlines[levels_weight[similarity_level]] = lesson.get_all_headlines() - wastes_headlines
            wastes_headlines |= weighted_headlines[levels_weight[similarity_level]]

            weighted_headlines[levels_weight[similarity_level+1]] = lesson.module.get_all_headlines() - wastes_headlines

            # add question weight
            for weight, headlines in weighted_headlines.items():
                questions = Question.objects.filter(tags__in=headlines, sub=False)
                for question in questions:
                    question_weight[str(question.id)] = question_weight.get(str(question.id), 0) + weight

        return question_weight

    def similar_by_author(question, question_weight):
        author = question.tags.exclude(author=None).first().author
        questions = Question.objects.filter(tags=author, id__in=question_weight.keys(), sub=False)
        for question in questions:
            question_weight[str(question.id)] += 2
        return question_weight

    def similar_by_level(question, question_weight):
        level = question.tags.exclude(questionlevel=None).first().questionlevel.name
        questions = Question.objects.filter(tags__name=level, id__in=question_weight.keys(), sub=False)
        for question in questions:
            question_weight[str(question.id)] += 3
        return question_weight

    data = request.data
    quiz_id = data.pop('quiz_id', None)
    question_id = data.pop('question_id', None)
    is_single_question = data.pop('is_single_question', False)
    by_headlines = data.pop('by_headlines', False)
    by_author = data.pop('by_author', False)
    by_level = data.pop('by_level', False)

    question_weight = {}

    if not is_single_question:
        quiz = UserQuiz.objects.get(id=quiz_id)
        question_set = Question.objects.filter(useranswer__quiz=quiz)
    else:
        question_set = [Question.objects.get(id=question_id)]

    for question in question_set:
        if by_headlines:
            question_weight = similar_by_headline(question, question_weight)

        if by_author:
            question_weight = similar_by_author(question, question_weight)

        if by_level:
            question_weight = similar_by_level(question, question_weight)

    for question in question_set:
        question_weight.pop(str(question.id))

    sorted_question = sorted(question_weight.keys(), key=lambda x: question_weight[x], reverse=True)

    questions = []
    for question_id in sorted_question[:len(question_set)] if not is_single_question else sorted_question:
        questions.append(Question.objects.get(id=question_id))

    serializer = QuestionSerializer(questions, many=True)
    if is_single_question:
        tag = questions[0].tags.exclude(headbase=None).first().headbase
        while hasattr(tag, 'headline'):
            tag = tag.headline.parent_headline
        subject = str(tag.h1.lesson.module.subject.id)
        return Response({'questions': serializer.data, 'subject': subject})

    return Response(serializer.data)
# {
#         "questions_id": ["000c37e8-0635-49a7-9e94-2cfcc57602e8"],
#         "is_single_question": 1,
#         "by_headlines": 1,
#         "by_author": 1,
#         "by_level": 1
# }

############################


@api_view(['POST'])
def quiz_review(request):
    data = request.data

    quiz_id = data.pop('quiz_id', None)

    if check_user(data):
        quiz = UserQuiz.objects.get(id=quiz_id)
        answers = UserAnswer.objects.filter(quiz=quiz)

        correct_questions = 0
        question_num = 0
        solved_questions = 0
        ideal_duration = 0
        attempt_duration = 0
        modules = {}
        lessons = {}
        h1s = {}

        for answer in answers:
            if hasattr(answer, 'userfinalanswer'):
                solved_questions, correct_questions, ideal_duration, attempt_duration, modules, lessons, h1s = review_final_answer_question(answer, correct_questions, solved_questions, ideal_duration, attempt_duration, modules, lessons, h1s)
                question_num += 1
            elif hasattr(answer, 'usermultiplechoiceanswer'):
                solved_questions, correct_questions, ideal_duration, attempt_duration, modules, lessons, h1s = review_multi_choice_question(answer, correct_questions, solved_questions, ideal_duration, attempt_duration, modules, lessons, h1s)
                question_num += 1
            elif hasattr(answer, 'usermultisectionanswer'):
                solved_questions, correct_questions, ideal_duration, attempt_duration, modules, lessons, h1s = review_multi_section_question(answer, correct_questions, solved_questions, ideal_duration, attempt_duration, modules, lessons, h1s)
                question_num += answer.usermultisectionanswer.question.multisectionquestion.sub_questions.count()

        mark_based_h1s = sorted(h1s.items(),
                                key=lambda x: (x[1]['correct'] + x[1]['all'], x[1]['correct']), reverse=True)
        mark_based_lessons = sorted(lessons.items(),
                                    key=lambda x: (x[1]['correct'] + x[1]['all'], x[1]['correct']), reverse=True)
        mark_based_modules = sorted(modules.items(),
                                    key=lambda x: (x[1]['correct'] + x[1]['all'], x[1]['correct']), reverse=True)

        time_based_h1s = sorted(h1s.items(),
                                key=lambda x: x[1]['duration'], reverse=True)
        time_based_lessons = sorted(lessons.items(),
                                    key=lambda x: x[1]['duration'], reverse=True)
        time_based_modules = sorted(modules.items(),
                                    key=lambda x: x[1]['duration'], reverse=True)

        best_worst_skills = dict(mark_based_modules if len(mark_based_modules) > 5 else mark_based_lessons if len(mark_based_lessons) > 5 else mark_based_h1s)

        statements = questions_statistics_statement(attempt_duration, ideal_duration, solved_questions, answers, mark_based_modules, mark_based_lessons, mark_based_h1s, time_based_modules, time_based_lessons, time_based_h1s)

        answers_serializer = UserAnswerSerializer(answers, many=True).data

        return Response(
            {'answers': answers_serializer,
             'question_num': question_num, 'correct_questions_num': correct_questions,
             'ideal_duration': ideal_duration, 'attempt_duration': attempt_duration,
             'quiz_duration': quiz.duration.total_seconds() if quiz.duration is not None else None, 'quiz_subject': {'id': quiz.subject.id, 'name': quiz.subject.name},
             'best_worst_skills': best_worst_skills, 'statements': statements})
    else:
        return Response(0)


@api_view(['POST'])
def save_question(request):
    data = request.data
    question_id = data.pop('question_id', None)

    if check_user(data):
        user = get_user(data)
        question = Question.objects.get(id=question_id)
        SavedQuestion.objects.get_or_create(user=user, question=question)
        return Response(1)

    else:
        return Response(0)


@api_view(['POST'])
def unsave_question(request):
    data = request.data
    question_id = data.pop('question_id', None)

    if check_user(data):
        user = get_user(data)
        question = Question.objects.get(id=question_id)
        SavedQuestion.objects.get(user=user, question=question).delete()
        return Response(1)

    else:
        return Response(0)


@api_view(['POST'])
def report(request):
    data = request.data
    body = data.pop('body', None)
    question = data.pop('question_id', None)

    if check_user(data):
        user = get_user(data)
        question = Question.objects.get(id=question)
        Report.objects.create(user=user, body=body, question=question)

        subject = 'Report from user'
        message = f'{user.firstName} {user.lastName} said there is this issue {body} in this question {question.body}\nplease check it as soon as possible'
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            ['malek315@gmail.com'],
            fail_silently=False,
        )
        return Response(1)

    else:
        return Response(0)


@api_view(['POST'])
def quiz_history(request):
    data = request.data
    quiz_index = data.pop('quiz_index', 0)

    if check_user(data):
        user = get_user(data)

        days = {'Sunday': 'الأحد', 'Monday': 'الإثنين', 'Tuesday': 'الثلاثاء', 'Wednesday': 'الأربعاء', 'Thursday': 'الخميس', 'Friday': 'الجمعة', 'Saturday': 'السبت'}

        quizzes = UserQuiz.objects.filter(user=user).order_by('-creationDate')[quiz_index:quiz_index + 10]

        if not quizzes.exists():
            return Response([])

        quiz_list = []
        for quiz in quizzes:

            date = quiz.creationDate.strftime('%I:%M %p • %d/%m/%Y %A')
            date = date[:22] + days[date[22:]]

            attempt_duration = quiz.useranswer_set.aggregate(Sum('duration'))['duration__sum']
            attempt_duration = attempt_duration.total_seconds() if attempt_duration else 0
            ideal_duration = quiz.useranswer_set.aggregate(Sum('question__idealDuration'))['question__idealDuration__sum']
            ideal_duration = ideal_duration.total_seconds() if ideal_duration else 0

            user_answers = UserAnswer.objects.filter(quiz=quiz)

            question_num = 0
            correct_question_num = 0
            for answer in user_answers:

                if hasattr(answer, 'usermultiplechoiceanswer'):
                    answer = answer.usermultiplechoiceanswer
                    correct_question_num += 1 if answer.question.multiplechoicequestion.correct_answer == answer else 0
                    question_num += 1
                elif hasattr(answer, 'userfinalanswer'):
                    answer = answer.userfinalanswer
                    correct_question_num += 1 if answer.question.finalanswerquestion.correct_answer == answer else 0
                    question_num += 1
                elif hasattr(answer, 'usermultisectionanswer'):
                    answer = answer.usermultisectionanswer
                    for sub_answer in answer.sub_questions_answers.all():
                        if hasattr(sub_answer, 'usermultiplechoiceanswer'):
                            sub_answer = sub_answer.usermultiplechoiceanswer
                            correct_question_num += 1 if sub_answer.question.multiplechoicequestion.correct_answer == sub_answer else 0
                        elif hasattr(sub_answer, 'userfinalanswer'):
                            sub_answer = sub_answer.userfinalanswer
                            correct_question_num += 1 if sub_answer.question.finalanswerquestion.correct_answer == sub_answer else 0
                    question_num += answer.usermultisectionanswer.question.multisectionquestion.sub_questions.count()
            tags_ids = user_answers.values_list('question__tags__id', flat=True).distinct()
            headbases = HeadBase.objects.filter(id__in=tags_ids)
            h1s = set()
            lessons = set()
            modules = set()
            for tag in headbases:
                while hasattr(tag, 'headline'):
                    tag = tag.headline.parent_headline
                h1s.add(tag.h1.name)
                lessons.add(tag.h1.lesson.name)
                modules.add(tag.h1.lesson.module.name)
            quiz_list.append({
                'id': str(quiz.id),
                'subject': quiz.subject.name,
                'date': date,
                'quiz_duration': quiz.duration.total_seconds() if quiz.duration is not None else None,
                'attempt_duration': attempt_duration,
                'ideal_duration': ideal_duration,
                'question_num': question_num,
                'correct_question_num': correct_question_num,
                'skills': modules if len(modules) > 5 else lessons if len(lessons) > 5 else h1s,
            })

        return Response(quiz_list)

    else:
        return Response(0)


@api_view(['POST'])
def get_shared_question(request):
    data = request.data

    question_id = data.pop('ID', None)
    question_obj = Question.objects.filter(id=question_id)

    if question_obj.exists():
        tag = question_obj.first().tags.exclude(headbase=None).first().headbase
        while hasattr(tag, 'headline'):
            tag = tag.headline.parent_headline
        subject = str(tag.h1.lesson.module.subject.id)

        serializer = QuestionSerializer(question_obj.first(), many=False).data
        return Response({'question': serializer, 'subject': subject})

    else:
        return Response(0)


@api_view(['POST'])
def mark_shared_question(request):
    data = request.data
    answers = data.pop('answers', None)

    question_status = False
    for ID, ans in answers.items():
        question = Question.objects.get(id=ID)
        if hasattr(question, 'finalanswerquestion'):
            answer = mark_final_answer_question(None, question, ans, None, None, None, None, None, None, True)
            question_status = answer == question.finalanswerquestion.correct_answer

        elif hasattr(question, 'multiplechoicequestion'):
            answer = mark_multiple_choice_question(None, question, ans, None, None, None, None, None, None, True)
            question_status = answer == question.multiplechoicequestion.correct_answer

        elif hasattr(question, 'multisectionquestion'):
            question_status = mark_multi_section_question(None, question, ans, None, None, None, None, None, None, True)

    return Response(question_status)


@api_view(['POST'])
def get_admin_question(request):
    data = request.data

    question_id = data.pop('ID', None)

    question_obj = Question.objects.get(id=question_id)
    serializer = QuestionSerializer(question_obj, many=False).data

    return Response(serializer)


@api_view(['POST'])
def add_or_edit_multiple_choice_question(request):
    data = request.data

    edit = data.pop('edit', False)

    question_id = data.pop('ID', None)

    question_body = data.pop('question', None)
    image = data.pop('image', None)

    choices = data.pop('choices', None)
    notes = data.pop('notes', None)

    headlines = data.pop('headlines', None)
    headlines_level = data.pop('headlines_level', None)

    source = data.pop('source', None)

    level = data.pop('level', None)
    levels = {1: 'easy', 2: 'inAverage', 3: 'hard'}

    if not edit:
        question, _ = MultipleChoiceQuestion.objects.get_or_create(body=question_body)
    else:
        question = Question.objects.get(id=question_id).multiplechoicequestion
        question.choices.all().delete()
        question.tags.exclude(questionlevel=None).delete()
        question.tags.clear()
        question.save()

        question.body = question_body

    if image is not None and not edit:
        image = base64.b64decode(image)
        image_name = LastImageName.objects.first()
        question.image = ContentFile(image, str(image_name.name)+'.png')
        image_name.name += 1
        image_name.save()
    elif image is not None and edit:
        image = base64.b64decode(image)
        image_name = question.image.name
        question.image = ContentFile(image, str(image_name) + '.png')

    correct_answer = AdminMultipleChoiceAnswer.objects.create(body=choices[0])
    question.choices.add(correct_answer)
    question.correct_answer = correct_answer

    for i in range(1, len(choices)):
        choice = AdminMultipleChoiceAnswer.objects.create(body=choices[i], notes=notes[i])
        question.choices.add(choice)

    for i in range(len(headlines)):
        if headlines_level[i] == 1:
            headline, _ = H1.objects.get_or_create(name=headlines[i].strip())
            question.tags.add(headline)
        else:
            headline, _ = HeadLine.objects.get_or_create(name=headlines[i].strip(), level=headlines_level[i])
            question.tags.add(headline)

    author, _ = Author.objects.get_or_create(name=source)
    question.tags.add(author)

    level = QuestionLevel.objects.create(name=levels[level], level=level)
    question.tags.add(level)

    question.save()
    return Response(1)


@api_view(['POST'])
def add_or_edit_final_answer_question(request):
    data = request.data

    edit = data.pop('edit', False)

    question_id = data.pop('ID', None)

    question_body = data.pop('question', None)
    image = data.pop('image', None)

    answer = data.pop('answer', None)

    headlines = data.pop('headlines', None)
    headlines_level = data.pop('headlines_level', None)

    source = data.pop('source', None)

    level = data.pop('level', None)
    levels = {1: 'easy', 2: 'inAverage', 3: 'hard'}

    if not edit:
        question, _ = FinalAnswerQuestion.objects.get_or_create(body=question_body)
    else:
        question = Question.objects.get(id=question_id).finalanswerquestion

        question.correct_answer.delete()
        question.correct_answer = None
        question.tags.exclude(questionlevel=None).delete()
        question.tags.clear()
        question.save()

        question.body = question_body

    correct_answer = AdminFinalAnswer.objects.create(body=answer)
    question.correct_answer = correct_answer

    if image is not None and not edit:
        image = base64.b64decode(image)
        image_name = LastImageName.objects.first()
        question.image = ContentFile(image, str(image_name.name)+'.png')
        image_name.name += 1
        image_name.save()
    elif image is not None and edit:
        image = base64.b64decode(image)
        image_name = question.image.name
        question.image = ContentFile(image, str(image_name) + '.png')

    for i in range(len(headlines)):
        if headlines_level[i] == 1:
            headline, _ = H1.objects.get_or_create(name=headlines[i].strip())
            question.tags.add(headline)
        else:
            headline, _ = HeadLine.objects.get_or_create(name=headlines[i].strip(), level=headlines_level[i])
            question.tags.add(headline)

    author, _ = Author.objects.get_or_create(name=source)
    question.tags.add(author)

    level = QuestionLevel.objects.create(name=levels[level], level=level)
    question.tags.add(level)

    question.save()
    return Response(1)


@api_view(['POST'])
def add_or_edit_multi_section_question(request):
    data = request.data

    edit = data.pop('edit', False)

    question_id = data.pop('ID', None)

    question_body = data.pop('question', None)
    image = data.pop('image', None)

    sub_questions = data.pop('subQuestions', None)

    source = data.pop('source', None)

    level = 1
    levels = {1: 'easy', 2: 'inAverage', 3: 'hard'}

    if not edit:
        question, _ = MultiSectionQuestion.objects.get_or_create(body=question_body)
    else:
        question = Question.objects.get(id=question_id).multisectionquestion

        question.sub_questions.all().delete()
        question.tags.exclude(questionlevel=None).delete()
        question.tags.clear()
        question.save()

        question.body = question_body

    if image is not None and not edit:
        image = base64.b64decode(image)
        image_name = LastImageName.objects.first()
        question.image = ContentFile(image, str(image_name.name)+'.png')
        image_name.name += 1
        image_name.save()

    if image is not None and edit:
        image = base64.b64decode(image)
        image_name = question.image.name
        question.image = ContentFile(image, str(image_name) + '.png')

    author, _ = Author.objects.get_or_create(name=source)
    question.tags.add(author)

    for ques in sub_questions:
        if ques['type'] == 'finalAnswerQuestion':
            correct_answer = AdminFinalAnswer.objects.create(body=ques['answer'])
            sub_question = FinalAnswerQuestion.objects.create(body=ques['question'], correct_answer=correct_answer, sub=True)

        elif ques['type'] == 'multipleChoiceQuestion':
            correct_answer = AdminMultipleChoiceAnswer.objects.create(body=ques['choices'][0])
            sub_question = MultipleChoiceQuestion.objects.create(body=ques['question'], correct_answer=correct_answer, sub=True)
            sub_question.choices.add(correct_answer)

            for choiceIndex in range(1, len(ques['choices'])):
                choice = AdminMultipleChoiceAnswer.objects.create(body=ques['choices'][choiceIndex], notes=ques['choicesNotes'][choiceIndex])
                sub_question.choices.add(choice)

        for i in range(len(ques['headlines'])):
            if ques['headlinesLevel'][i] == 1:
                headline, _ = H1.objects.get_or_create(name=ques['headlines'][i].strip())

            else:
                headline, _ = HeadLine.objects.get_or_create(name=ques['headlines'][i].strip(), level=ques['headlinesLevel'][i])
            sub_question.tags.add(headline)
            question.tags.add(headline)

        sub_question.tags.add(author)

        sub_question_level = QuestionLevel.objects.create(name=levels[ques['questionLevel']], level=ques['questionLevel'])
        sub_question.tags.add(sub_question_level)
        level += ques['questionLevel']

        sub_question.save()

        question.sub_questions.add(sub_question)

    question_level = QuestionLevel.objects.create(name=levels[round(level/len(sub_questions))], level=level/len(sub_questions))

    question.tags.add(question_level)

    question.save()
    return Response(1)


@api_view(['GET'])
def reset_questions_level_and_ideal_duration(request):
    questions = Question.objects.all()
    for question in questions:
        question.idealDuration = datetime.timedelta(seconds=120)
        level = QuestionLevel.objects.create(name='inAverage', level=2)
        question.tags.add(level)
        question.save()
    return Response(0)


@api_view(['GET'])
def delete_users_answers(request):
    UserAnswer.objects.all().delete()
    return Response(0)


@api_view(['POST'])
def subject_question_num(request):
    data = request.data
    subject = data['subject']
    subject = Subject.objects.get(name=subject)
    modules = Module.objects.filter(subject=subject)
    lessons = Lesson.objects.filter(module__in=modules)
    h1s = H1.objects.filter(lesson__in=lessons)
    h2s = HeadLine.objects.filter(parent_headline__in=h1s)
    h3s = HeadLine.objects.filter(parent_headline__in=h2s)
    h4s = HeadLine.objects.filter(parent_headline__in=h3s)
    h5s = HeadLine.objects.filter(parent_headline__in=h4s)
    headlines = set(h1s) | set(h2s) | set(h3s) | set(h4s) | set(h5s)
    return Response(Question.objects.filter(tags__in=headlines, sub=False).distinct('id').count())


@api_view(['POST'])
def subject_question_ids(request):
    data = request.data
    subject = data['subject']
    subject = Subject.objects.get(name=subject)
    modules = Module.objects.filter(subject=subject)
    lessons = Lesson.objects.filter(module__in=modules)
    h1s = H1.objects.filter(lesson__in=lessons)
    h2s = HeadLine.objects.filter(parent_headline__in=h1s)
    h3s = HeadLine.objects.filter(parent_headline__in=h2s)
    h4s = HeadLine.objects.filter(parent_headline__in=h3s)
    h5s = HeadLine.objects.filter(parent_headline__in=h4s)
    headlines = set(h1s) | set(h2s) | set(h3s) | set(h4s) | set(h5s)
    return Response(Question.objects.filter(tags__in=headlines, sub=False).distinct('id').values_list('id', flat=True))
# {
#         "subject": "التاريخ"
# }


@api_view(['GET'])
def test(request):
    id = '539bd328-0fae-4c7c-854a-2ffed9a91587'
    q = Question.objects.get(id=id)
    return Response(QuestionSerializer(q, many=False).data)
