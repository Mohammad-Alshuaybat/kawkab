import time
from math import ceil

from django.core.mail import send_mail
from rest_framework.decorators import api_view
from rest_framework.response import Response

from school import settings
from user.models import User
from user.utils import check_user, get_user
from .models import Subject, Module, Question, Lesson, FinalAnswerQuestion, AdminFinalAnswer, \
    MultipleChoiceQuestion, AdminMultipleChoiceAnswer, QuestionLevel, H1, HeadLine, HeadBase, UserFinalAnswer, \
    UserMultipleChoiceAnswer, UserQuiz, Author, LastImageName, Report, SavedQuestion, UserAnswer
from .serializers import SubjectSerializer, TagSerializer, ModuleSerializer, \
    QuestionSerializer, FinalAnswerQuestionSerializer, MultipleChoiceQuestionSerializer, UserAnswerSerializer, \
    UserQuizSerializer

from django.db.models import Count, Q, Sum

import random
import datetime


# import pandas as pd


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
        module_weights = {module: round(weight / sum_weights * question_number) for module, weight in module_weights.items()}

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

    def quiz_level(level, number_of_question):
        if level == 1:
            return [QuestionLevel.objects.get(name=1)] * number_of_question
        elif level == 2:
            return random.shuffle(
                [QuestionLevel.objects.get(name=2)] * number_of_question // 2 + [QuestionLevel.objects.get(name=1)] * (
                            number_of_question - number_of_question // 2))
        else:
            return [QuestionLevel.objects.get(name=2)] * number_of_question

    def get_questions(lesson_headline, modules_lessons_normalized_weights, quiz_level=[]):
        """ lesson_headline = {    # here headlines are from all levels 1-5
        'lesson1': {h1, h2, h3},
        'lesson2': {h1},
        'lesson3': {h1, h2, h3, h4},
        'lesson4': {h1, h2, h3, h4}
        } """

        """ modules_lessons_normalized_weights = {    # all weights and question num here depend on quiz consist of 20 question
        'module1': {'lessons': {'lesson1': 10, 'lesson2': 5}, 'weight': 14.285714285714286}, 
        'module2': {'lessons': {'lesson1': 3, 'lesson2': 2}, 'weight': 5.714285714285715}
        } """

        question_set = set()

        for module, lessons_weight in modules_lessons_normalized_weights.items():
            for lesson, question_num in lessons_weight['lessons'].items():
                headline_counter = 0
                temp_question_set = set()
                while len(temp_question_set) < question_num:
                    headline = list(lesson_headline[lesson])[headline_counter % len(lesson_headline[lesson])]

                    _questions = Question.objects.filter(tags=headline)  # .filter(tags=quiz_level[0])
                    # quiz_level.pop(quiz_level[0])
                    if _questions:
                        temp_question_set.add(random.choice(_questions))
                    headline_counter += 1
                    if headline_counter > question_num * 8:
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
        correct_questions = 0
        lessons = {}
        h1s = {}

        subject = Subject.objects.get(id=subject)
        quiz = UserQuiz.objects.create(subject=subject, user=user,
                                       duration=datetime.timedelta(seconds=int(quiz_duration)))
        for ID, ans in answers.items():
            question = Question.objects.get(id=ID)
            if hasattr(question, 'finalanswerquestion'):
                answer = UserFinalAnswer.objects.create(body=ans.get('answer', None),
                                                        duration=datetime.timedelta(seconds=ans['duration']),
                                                        question=question, quiz=quiz)
                question = question.finalanswerquestion
            elif hasattr(question, 'multiplechoicequestion'):
                choice = AdminMultipleChoiceAnswer.objects.filter(id=ans.get('answer', None)).first()

                answer = UserMultipleChoiceAnswer.objects.create(choice=choice,
                                                                 duration=datetime.timedelta(seconds=ans['duration']),
                                                                 question=question, quiz=quiz)
                question = question.multiplechoicequestion

            correct_questions += 1 if answer == question.correct_answer else 0

            tag = question.tags.exclude(headbase=None).first().headbase
            if hasattr(tag, 'headline'):
                while hasattr(tag, 'headline'):
                    tag = tag.headline.parent_headline
            tag = tag.h1

            h1 = h1s.get(tag.name, {})
            lesson = lessons.get(tag.lesson.id, {})

            if answer == question.correct_answer:
                h1['correct'] = h1.get('correct', 0) + 1
                lesson['correct'] = lesson.get('correct', 0) + 1
            else:
                h1['correct'] = h1.get('correct', 0)
                lesson['correct'] = lesson.get('correct', 0)

            h1['all'] = h1.get('all', 0) + 1
            lesson['all'] = lesson.get('all', 0) + 1

            h1s[tag.name] = h1
            lessons[tag.lesson.name] = lesson

            ideal_duration += question.idealDuration.total_seconds()
            attempt_duration += answer.duration.total_seconds()

        skills = sorted(lessons.items() if len(lessons) > 5 else h1s.items(), key=lambda x: (x[1]['correct'] + x[1]['all'], x[1]['correct']), reverse=True)
        best_worst_skills = dict(list(skills[:3]) + list(skills[-2:]))

        ideal_duration = "{}".format(str(datetime.timedelta(seconds=ideal_duration)))
        attempt_duration = "{}".format(str(datetime.timedelta(seconds=attempt_duration)))
        return Response({'correct_questions': correct_questions, 'total_question_num': len(answers),
                         'attempt_duration': attempt_duration, 'ideal_duration': ideal_duration,
                         'quiz_id': quiz.id, 'best_worst_skills': best_worst_skills})
    else:
        return Response(0)


@api_view(['POST'])
def mark_question(request):
    data = request.data
    answers = data.pop('answers', None)

    if check_user(data):
        for ID, ans in answers.items():
            question = Question.objects.get(id=ID)
            if hasattr(question, 'finalanswerquestion'):
                UserFinalAnswer.objects.create(body=ans.get('answer', None),
                                                        duration=datetime.timedelta(seconds=ans['duration']),
                                                        question=question)

            elif hasattr(question, 'multiplechoicequestion'):
                choice = AdminMultipleChoiceAnswer.objects.filter(id=ans.get('answer', None)).first()

                UserMultipleChoiceAnswer.objects.create(choice=choice,
                                                                 duration=datetime.timedelta(seconds=ans['duration']),
                                                                 question=question)

        return Response(1)
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
        tag = question.tags.exclude(headbase=None).first().headbase

        if hasattr(tag, 'h1'):
            main_headline = tag.h1

        elif hasattr(tag, 'headline'):
            main_headline = tag.headline
            while hasattr(tag, 'headline'):
                tag = tag.headline.parent_headline

        lesson = tag.h1.lesson

        # add headlines questions
        headlines = lesson.get_all_headlines()
        questions = Question.objects.filter(tags__in=headlines)
        for question in questions:
            question_weight[str(question.id)] = question_weight.get(str(question.id), 0)

        # weight the headlines
        wastes_headlines = {main_headline}
        weighted_headlines = {levels_weight[0]: {main_headline}}
        wastes_headlines |= set(main_headline.get_all_child_headlines())
        weighted_headlines[levels_weight[1]] = set(main_headline.get_all_child_headlines())
        similarity_level = 2
        while hasattr(main_headline, 'parent_headline'):
            main_headline = main_headline.parent_headline
            if hasattr(main_headline, 'headline'):
                main_headline = main_headline.headline
                weighted_headlines[levels_weight[similarity_level]] = (
                                                                                      set(main_headline.get_all_child_headlines()) | {
                                                                                  main_headline}) - wastes_headlines
                wastes_headlines |= weighted_headlines[levels_weight[similarity_level]]
            elif hasattr(main_headline, 'h1'):
                main_headline = main_headline.h1
                weighted_headlines[levels_weight[similarity_level]] = (
                                                                                      set(main_headline.get_all_child_headlines()) | {
                                                                                  main_headline}) - wastes_headlines
                wastes_headlines |= weighted_headlines[levels_weight[similarity_level]]
            similarity_level += 1
        weighted_headlines[levels_weight[similarity_level]] = lesson.get_all_headlines() - wastes_headlines
        wastes_headlines |= weighted_headlines[levels_weight[similarity_level]]
        similarity_level += 1
        weighted_headlines[levels_weight[similarity_level]] = lesson.module.get_all_headlines() - wastes_headlines

        # add question weight
        for weight, headlines in weighted_headlines.items():
            questions = Question.objects.filter(tags__in=headlines)
            for question in questions:
                question_weight[str(question.id)] = question_weight.get(str(question.id), 0) + weight

        return question_weight

    def similar_by_author(question, question_weight):
        author = question.tags.exclude(author=None).first().author
        questions = Question.objects.filter(tags=author, id__in=question_weight.keys())
        for question in questions:
            question_weight[str(question.id)] += 2
        return question_weight

    def similar_by_level(question, question_weight):
        level = question.tags.exclude(questionlevel=None).first().questionlevel
        questions = Question.objects.filter(tags=level, id__in=question_weight.keys())
        for question in questions:
            question_weight[str(question.id)] += 3
        return question_weight

    data = request.data
    questions_id = data.pop('questions_id', None)
    is_single_question = data.pop('is_single_question', False)
    by_headlines = data.pop('by_headlines', False)
    by_author = data.pop('by_author', False)
    by_level = data.pop('by_level', False)

    question_weight = {}
    for question in questions_id:
        question = Question.objects.get(id=question)
        if by_headlines:
            question_weight = similar_by_headline(question, question_weight)

        if by_author:
            question_weight = similar_by_author(question, question_weight)

        if by_level:
            question_weight = similar_by_level(question, question_weight)

    for ID in questions_id:
        question_weight.pop(ID)

    sorted_question = sorted(question_weight.keys(), key=lambda x: question_weight[x], reverse=True)

    questions = []
    for question_id in (sorted_question[:len(questions_id)]if not is_single_question else sorted_question):
        questions.append(Question.objects.get(id=question_id))

    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)
# {
#         "questions_id": ["000c37e8-0635-49a7-9e94-2cfcc57602e8"],
#         "is_single_question": 1,
#         "by_headlines": 1,
#         "by_author": 1,
#         "by_level": 1
# }


@api_view(['POST'])
def quiz_review(request):
    data = request.data
    print(data)
    quiz_id = data.pop('quiz_id', None)

    if check_user(data):
        quiz = UserQuiz.objects.get(id=quiz_id)
        answers = UserAnswer.objects.filter(quiz=quiz)

        correct_questions = 0
        modules = {}
        lessons = {}
        h1s = {}

        for answer in answers:
            if hasattr(answer, 'userfinalanswer'):
                answer = answer.userfinalanswer
                question = answer.question.finalanswerquestion
            elif hasattr(answer, 'usermultiplechoiceanswer'):
                answer = answer.usermultiplechoiceanswer
                question = answer.question.multiplechoicequestion

            tag = question.tags.exclude(headbase=None).first().headbase
            if hasattr(tag, 'headline'):
                while hasattr(tag, 'headline'):
                    tag = tag.headline.parent_headline
            tag = tag.h1

            h1 = h1s.get(tag.name, {})
            lesson = lessons.get(tag.lesson.name, {})
            module = modules.get(tag.lesson.module.name, {})

            if answer == question.correct_answer:
                correct_questions += 1
                h1['correct'] = h1.get('correct', 0) + 1
                lesson['correct'] = lesson.get('correct', 0) + 1
                module['correct'] = module.get('correct', 0) + 1
            else:
                h1['correct'] = h1.get('correct', 0)
                lesson['correct'] = lesson.get('correct', 0)
                module['correct'] = module.get('correct', 0)

            h1['all'] = h1.get('all', 0) + 1
            lesson['all'] = lesson.get('all', 0) + 1
            module['all'] = module.get('all', 0) + 1

            if answer.duration > answer.question.idealDuration:
                h1['duration'] = h1.get('duration', 0) + 1
                lesson['duration'] = lesson.get('duration', 0) + 1
                module['duration'] = module.get('duration', 0) + 1
            else:
                h1['duration'] = h1.get('duration', 0)
                lesson['duration'] = lesson.get('duration', 0)
                module['duration'] = module.get('duration', 0)

            h1s[tag.name] = h1
            lessons[tag.lesson.name] = lesson
            modules[tag.lesson.module.name] = module

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

        statements = [
                    f'تقييم بشكل عام : أظهرت بطأ في تقديمك للامتحان حيث كان معدل حلك لكل سؤال 4 دقائق مما مكنك من حل 6 اسئلة من أصل {len(answers)} في الوقت المحدد',
                      ]
        if mark_based_modules[-1][1]['correct'] < mark_based_modules[-1][1]['all']:
            statements.append(f'اكثر اخطاءك كانت في وحدة {mark_based_modules[-1][0]}')
        if mark_based_lessons[-1][1]['correct'] < mark_based_lessons[-1][1]['all']:
            statements.append(f'اكثر اخطاءك كانت في درس {mark_based_lessons[-1][0]}')
        if mark_based_h1s[-1][1]['correct'] < mark_based_h1s[-1][1]['all']:
            statements.append(f'ركز أكثر في دراسة موضوع {mark_based_h1s[-1][0]}')

        if mark_based_modules[-1][1]['correct'] == mark_based_modules[-1][1]['all']:
            statements.append(f'أجبت على جميع أسئلة وحدة {mark_based_modules[0][0]} بنجاح')
        if mark_based_lessons[-1][1]['correct'] == mark_based_lessons[-1][1]['all']:
            statements.append(f'أجبت على جميع أسئلة درس {mark_based_lessons[0][0]} بنجاح')

        if time_based_modules[0][1]['duration'] > 0:
            statements.append(f'لاحظنا قضاءك الوقت الأكبر على اسئلة وحدة {time_based_modules[0][0]}')
        if time_based_lessons[0][1]['duration'] > 0:
            statements.append(f'لاحظنا قضاءك الوقت الأكبر على اسئلة درس {time_based_lessons[0][0]}')
        if time_based_h1s[0][1]['duration'] > 0:
            statements.append(f'لاحظنا قضاءك الوقت الأكبر على اسئلة {time_based_h1s[0][0]}')
        print(mark_based_modules)
        print(time_based_modules)
        print(mark_based_lessons)
        print(time_based_lessons)
        print(mark_based_h1s)
        print(time_based_h1s)
        print(statements)

        best_worst_skills = dict(mark_based_lessons if len(mark_based_lessons) > 5 else mark_based_h1s)

        # best_worst_skills = sorted(lessons.items() if len(lessons) > 5 else h1s.items(),
        #                 key=lambda x: (x[1]['correct'] + x[1]['all'], x[1]['correct']), reverse=True)
        # best_worst_skills = dict(best_worst_skills)

        answers_serializer = UserAnswerSerializer(answers, many=True).data
        return Response(
            {'answers': answers_serializer, 'correct_questions_num': correct_questions, 'quiz_duration': quiz.duration, 'quiz_subject': quiz.subject.name, 'best_worst_skills': best_worst_skills})
    else:
        return Response(0)
# {
#     "quiz_id": "e5fdfd58-56b4-48e2-a18c-c9b90c11c3ee",
#     "email": "abood@gmail.com",
#     "password": "123"
# }


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
        quizzes = UserQuiz.objects.filter(user=user).order_by('-creationDate')[quiz_index:quiz_index+10]
        if not quizzes.exists():
            return Response(1)
        quiz_list = []
        for quiz in quizzes:

            date = quiz.creationDate.strftime('%I:%M %p • %d/%m/%Y %A')
            date = date[:22] + days[date[22:]]
            attempt_duration = quiz.useranswer_set.aggregate(Sum('duration'))['duration__sum']
            attempt_duration = attempt_duration.total_seconds() if attempt_duration else 0

            user_answers = UserAnswer.objects.filter(quiz=quiz)

            question_num = 0
            correct_question_num = 0
            for answer in user_answers:
                question_num += 1
                if (answer.usermultiplechoiceanswer if hasattr(answer, 'usermultiplechoiceanswer') else answer.userfinalanswer) == (answer.question.multiplechoicequestion.correct_answer if hasattr(answer.question, 'multiplechoicequestion') else answer.question.finalanswerquestion.correct_answer):
                    correct_question_num += 1

            tags_ids = user_answers.values_list('question__tags__id', flat=True).distinct()
            headbases = HeadBase.objects.filter(id__in=tags_ids)
            h1s = set()
            lessons = set()
            for tag in headbases:
                if hasattr(tag, 'headline'):
                    while hasattr(tag, 'headline'):
                        tag = tag.headline.parent_headline
                h1s.add(tag.h1.name)
                lessons.add(tag.h1.lesson.name)

            quiz_list.append({
                    'id': str(quiz.id),
                    'subject': quiz.subject.name,
                    'date': date,
                    'quiz_duration': quiz.duration.total_seconds(),
                    'attempt_duration': attempt_duration,
                    'question_num': question_num,
                    'correct_question_num': correct_question_num,
                    'skills': lessons if len(lessons) > 5 else h1s,
                })

        return Response(quiz_list)

    else:
        return Response(0)


@api_view(['POST'])
def add_question(request):
    data = request.data
    body = data.pop('body', None)
    correct_answer = data.pop('correct_answer', None)
    headline = data.pop('headline', None)
    headline_level = data.pop('headline_level', None)
    choices = data.pop('choices', None)
    author = data.pop('author', None)
    level = data.pop('level', None)
    levels = {'0': 'easy', '1': 'inAverage', '2': 'hard'}

    if len(choices) == 0:
        question, _ = FinalAnswerQuestion.objects.get_or_create(body=body)
        answer, _ = AdminFinalAnswer.objects.get_or_create(body=correct_answer)
        question.correct_answer = answer
    else:
        question, _ = MultipleChoiceQuestion.objects.get_or_create(body=body)

        for choice in choices:
            cho, _ = AdminMultipleChoiceAnswer.objects.get_or_create(body=list(choice.keys())[0],
                                                                     notes=list(choice.values())[0])
            question.choices.add(cho)

        answer, _ = AdminMultipleChoiceAnswer.objects.get_or_create(body=correct_answer)
        question.correct_answer = answer

    if str(headline_level) == '1':
        headline, _ = H1.objects.get_or_create(name=headline.strip())
        question.tags.add(headline)
    else:
        headline, _ = HeadLine.objects.get_or_create(name=headline.strip(), level=headline_level)
        question.tags.add(headline)

    aut, _ = Author.objects.get_or_create(name=author)
    question.tags.add(aut)

    lvl, _ = QuestionLevel.objects.get_or_create(name=levels[str(level)])
    question.tags.add(lvl)

    question.save()
    return Response({'questionId': question.id})


@api_view(['POST'])
def add_question_image(request):
    data = request.data
    questionId = data.pop('questionId', None)[0]

    question = Question.objects.get(id=questionId)
    question.image = data['image']

    last_name = LastImageName.objects.all().first()
    question.image.name = str(last_name.name)
    last_name.name += 1
    last_name.save()
    question.save()
    return Response(1)


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
    return Response(Question.objects.filter(tags__in=headlines).count())
# {
#         "subject": "التاريخ"
# }


# @api_view(['GET'])
# def read_skills_from_xlsx(request):
#     df = pd.read_excel(r'G:\school\data\skills.xlsx')

#     sub, _ = Subject.objects.get_or_create(name='الرياضيات')
#     for index, row in df.iterrows():
#         row = row.to_dict()
#         if row['type'] == 2:
#             GeneralSkill.objects.get_or_create(id=row['id'], name=row['name'], subject=sub)
#         else:
#             Skill.objects.get_or_create(id=row['id'], name=row['name'], subject=sub)

#     for index, row in df.iterrows():
#         row = row.to_dict()
#         dependencies = str(row['dependencies']).split(',')
#         for i in dependencies:
#             if i != 'nan':
#                 dep_skill = Skill.objects.get(id=i)
#                 Skill.objects.get(id=row['id']).dependencies.add(dep_skill)
#     return Response()
#

# @api_view(['GET'])
# def read_headlines_from_xlsx(request):
#     df = pd.read_excel(r'G:\school\data\che.xlsx')
#     sub, _ = Subject.objects.get_or_create(name='الكيمياء', grade=12)
#     semester = 1
#     for index, row in df.iterrows():
#         if index == 39:
#             semester = 2
#             continue
#         mod, _ = Module.objects.get_or_create(name=row['module'].strip(), subject=sub, semester=semester)
#         les, _ = Lesson.objects.get_or_create(name=row['lesson'].strip(), module=mod)
#         h1, _ = H1.objects.get_or_create(name=row['h1'].strip())
#         h1.lesson = les
#         h1.save()
#         if (str(row['h2'])) != 'nan':
#             h2, _ = HeadLine.objects.get_or_create(name=row['h2'].strip())
#             h2.parent_headline = h1
#             h2.level = 2
#             h2.save()
#
#         if (str(row['h3'])) != 'nan':
#             h3, _ = HeadLine.objects.get_or_create(name=row['h3'].strip())
#             h3.parent_headline = h2
#             h3.level = 3
#             h3.save()
#
#         if (str(row['h4'])) != 'nan':
#             h4, _ = HeadLine.objects.get_or_create(name=row['h4'].strip())
#             h4.parent_headline = h3
#             h4.level = 4
#             h4.save()
#
#     return Response()


# @api_view(['GET'])
# def read_modules_from_xlsx(request):
#     df = pd.read_excel(r'G:\school\data\modules.xlsx')

#     sub, _ = Subject.objects.get_or_create(name='الرياضيات')
#     for index, row in df.iterrows():
#         row = row.to_dict()
#         Module.objects.get_or_create(id=row['id'], name=row['name'], subject=sub)
#     return Response()
#
#

# @api_view(['GET'])
# def read_lessons_from_xlsx(request):
#     df = pd.read_excel(r'G:\school\data\lessons.xlsx')

#     for index, row in df.iterrows():
#         row = row.to_dict()
#         module = Module.objects.get(id=row['module'])
#         lsn, _ = Lesson.objects.get_or_create(id=row['id'], name=row['name'], module=module)
#         skills = str(row['skills']).split(',')
#         for i in skills:
#             if i != 'nan':
#                 skill = Skill.objects.get(id=i)
#                 lsn.skills.add(skill)
#     return Response()

# @api_view(['GET'])
# def read_questions_from_xlsx(request):
#     # images, question type final or multi, correct answer
#     df = pd.read_excel(r'G:\school\data\questions.xlsx')
#     ques_type = 0
#     for index, row in df.iterrows():
#         row = row.to_dict()
#         if ques_type % 2 == 0:
#             qes, _ = FinalAnswerQuestion.objects.get_or_create(id=row['id'], body=row['body'])
#         else:
#             qes, _ = MultipleChoiceQuestion.objects.get_or_create(id=row['id'], body=row['body'])
#         ques_type += 1
#         skills = str(row['skills']).split(',')

#         for i in skills:
#             if i != 'nan':
#                 skill = Skill.objects.get(id=i)
#                 qes.skills.add(skill)

#         gsk = str(row['generalSkills']).split(',')
#         for i in gsk:
#             if i != 'nan':
#                 skill = GeneralSkill.objects.get(id=i)
#                 qes.tags.add(skill)
#     return Response()


# @api_view(['POST'])
# def similar_question(request):
#     def similar_by_headline(question, question_weight):
#         levels_weight = [15, 10, 6, 3, 1, 0]
#         # get lesson
#         tag = question.tags.exclude(headbase=None).first().headbase
#
#         if hasattr(tag, 'h1'):
#             main_headline = tag.h1
#             lesson = main_headline.lesson
#
#         elif hasattr(tag, 'headline'):
#             main_headline = tag.headline
#             headline = tag
#             while hasattr(headline, 'headline'):
#                 headline = headline.headline.parent_headline
#             lesson = headline.h1.lesson
#
#         # add headlines questions
#         headlines = lesson.get_all_headlines()
#         questions = Question.objects.filter(tags__in=headlines)
#         for question in questions:
#             question_weight[question.id] = question_weight.get(question.id, 0)
#
#         # weight the headlines
#         wastes_headlines = {main_headline}
#         weighted_headlines = {levels_weight[0]: {main_headline}}
#         wastes_headlines |= set(main_headline.get_all_child_headlines())
#         weighted_headlines[levels_weight[1]] = set(main_headline.get_all_child_headlines())
#         similarity_level = 1
#         while hasattr(main_headline, 'parent_headline'):
#             main_headline = main_headline.parent_headline
#             if hasattr(main_headline, 'headline'):
#                 main_headline = main_headline.headline
#                 weighted_headlines[levels_weight[similarity_level + 1]] = (
#                                                                                       set(main_headline.get_all_child_headlines()) | {
#                                                                                   main_headline}) - wastes_headlines
#                 wastes_headlines |= weighted_headlines[levels_weight[similarity_level + 1]]
#             elif hasattr(main_headline, 'h1'):
#                 main_headline = main_headline.h1
#                 weighted_headlines[levels_weight[similarity_level + 1]] = (
#                                                                                       set(main_headline.get_all_child_headlines()) | {
#                                                                                   main_headline}) - wastes_headlines
#                 wastes_headlines |= weighted_headlines[levels_weight[similarity_level + 1]]
#             similarity_level += 1
#         weighted_headlines[levels_weight[similarity_level + 1]] = set(lesson.get_all_headlines()) - wastes_headlines
#
#         # add question weight
#         for weight, headlines in weighted_headlines.items():
#             questions = Question.objects.filter(tags__in=headlines)
#             for question in questions:
#                 question_weight[question.id] += weight
#
#         return question_weight
#
#     def similar_by_author(question, question_weight):
#         author = question.tags.exclude(author=None).first().author
#         questions = Question.objects.filter(tags=author)
#         for question in questions:
#             question_weight[question.id] = question_weight.get(question.id, 0) + 2
#         return question_weight
#
#     def similar_by_level(question, question_weight):
#         level = question.tags.exclude(questionlevel=None).first().questionlevel
#         questions = Question.objects.filter(tags=level)
#         for question in questions:
#             question_weight[question.id] = question_weight.get(question.id, 0) + 3
#         return question_weight
#
#     data = request.data
#     question = data.pop('question_id', None)
#     by_headlines = data.pop('by_headlines', False)
#     by_author = data.pop('by_author', False)
#     by_level = data.pop('by_level', False)
#
#     question = Question.objects.get(id=question)
#     question_weight = {}
#     if by_headlines:
#         question_weight = similar_by_headline(question, question_weight)
#     if by_author:
#         question_weight = similar_by_author(question, question_weight)
#     if by_level:
#         question_weight = similar_by_level(question, question_weight)
#
#     sorted_question = sorted(question_weight.keys(), key=lambda x: question_weight[x], reverse=True)
#     questions = []
#     for question_id in sorted_question:
#         questions.append(Question.objects.get(id=question_id))
#
#     serializer = QuestionSerializer(questions, many=True)
#     return Response(serializer.data)





