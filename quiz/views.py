import time
from math import ceil

from rest_framework.decorators import api_view
from rest_framework.response import Response

from user.models import User
from user.utils import check_user, get_user
from .models import Subject, Module, Question, Lesson, FinalAnswerQuestion, AdminFinalAnswer, \
    MultipleChoiceQuestion, AdminMultipleChoiceAnswer, QuestionLevel, H1, HeadLine, HeadBase, UserFinalAnswer, \
    UserMultipleChoiceAnswer, UserQuiz, Author, LastImageName, Report, SavedQuestion, UserAnswer
from .serializers import SubjectSerializer, TagSerializer, ModuleSerializer, \
    QuestionSerializer, FinalAnswerQuestionSerializer, MultipleChoiceQuestionSerializer, UserAnswerSerializer

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
    import time
    startf = time.perf_counter()

    # def weight_module(h1s, question_number):
    #
    #     modules = Module.objects.filter(lesson__h1__in=h1s).distinct()
    #
    #     module_weights = {}
    #     for module in modules:
    #         main_headlines = module.get_main_headlines()
    #         module_weights[str(module.name)] = len(set(main_headlines).intersection(h1s)) / main_headlines.count()
    #
    #     sum_weights = sum(module_weights.values())
    #     module_weights = {module: weight / sum_weights * question_number for module, weight in module_weights.items()}
    #
    #     return module_weights
    #
    # def weight_lessons(h1s):
    #     lessons = Lesson.objects.filter(h1__in=h1s)
    #
    #     lesson_weights = {}
    #     for lesson in lessons:
    #         lesson_weights[str(lesson.name)] = len(set(lesson.get_main_headlines()).intersection(h1s)) / lesson.get_main_headlines().count()
    #
    #     return lesson_weights

    def weight_module(h1s, question_number):
        modules = Module.objects.annotate(
            num_h1s=Count('lesson__h1', distinct=True),
            num_common_h1s=Count('lesson__h1', filter=Q(lesson__h1__in=h1s), distinct=True)
        ).filter(num_h1s__gt=0)

        module_weights = {}
        for module in modules:
            if module.num_common_h1s > 0:
                module_weights[module.name] = module.num_common_h1s / module.num_h1s

        sum_weights = sum(module_weights.values())
        module_weights = {module: weight / sum_weights * question_number for module, weight in module_weights.items()}

        return module_weights

    def weight_lessons(h1s):
        lessons = Lesson.objects.annotate(
                num_h1s=Count('h1', distinct=True),
                num_common_h1s=Count('h1', filter=Q(h1__in=h1s), distinct=True)
            ).filter(num_h1s__gt=0)

        lesson_weights = {}
        for lesson in lessons:
            if lesson.num_common_h1s > 0:
                lesson_weights[str(lesson.name)] = lesson.num_common_h1s / lesson.num_h1s

        return lesson_weights

    def lesson_module(module_ques, lesson_weights):
        modules_lessons = {}
        modules_lessons_weights = {}

        lessons = set(Lesson.objects.filter(name__in=lesson_weights.keys()))

        for module in module_ques.keys():
            modules_lessons[module] = lessons.intersection(Module.objects.get(name=module).lesson_set.all())

        for module, module_lessons in modules_lessons.items():
            modules_lessons_weights[module] = {'lessons': {str(lesson.name): lesson_weights[str(lesson.name)] for lesson in module_lessons if str(lesson.name) in lesson_weights.keys()},
                                               'weight': module_ques[module]}

        return modules_lessons_weights

    def normalize_lessons_weight(modules_lessons_weights):
        for module, lessons_weight in modules_lessons_weights.items():
            total_lesson_weights = sum(lessons_weight['lessons'].values())
            lessons_weight['lessons'] = {lesson: round(weight / total_lesson_weights * lessons_weight['weight']) for lesson, weight in lessons_weight['lessons'].items()}
        return modules_lessons_weights

    def lesson_headlines(lesson_weight, h1s):
        lesson_headline = {}

        for lesson in lesson_weight.keys():
            lesson_headline[lesson] = h1s.intersection(Lesson.objects.get(name=lesson).get_main_headlines()).values_list('id', flat=True)

        for lesson, h1s in lesson_headline.items():
            h2s = HeadLine.objects.filter(parent_headline__in=h1s).values_list('id', flat=True)
            h3s = HeadLine.objects.filter(parent_headline__in=h2s).values_list('id', flat=True)
            h4s = HeadLine.objects.filter(parent_headline__in=h3s).values_list('id', flat=True)
            h5s = HeadLine.objects.filter(parent_headline__in=h4s).values_list('id', flat=True)
            lesson_headline[lesson] = set(h1s) | set(h2s) | set(h3s) | set(h4s) | set(h5s)

        return lesson_headline

    def quiz_level(level, number_of_question):
        if level == 1:
            return [QuestionLevel.objects.get(name=1)] * number_of_question
        elif level == 2:
            return random.shuffle([QuestionLevel.objects.get(name=2)] * number_of_question // 2 + [QuestionLevel.objects.get(name=1)] * (number_of_question - number_of_question // 2))
        else:
            return [QuestionLevel.objects.get(name=2)] * number_of_question

    def get_questions(lesson_headline, modules_lessons_normalized_weights, quiz_level=[]):
        question_set = set()

        for module, lessons_weight in modules_lessons_normalized_weights.items():
            for lesson, questions in lessons_weight['lessons'].items():
                headline_counter = 0
                temp_question_set = set()
                while len(temp_question_set) < questions:
                    headline = list(lesson_headline[lesson])[headline_counter % len(lesson_headline[lesson])]

                    _questions = Question.objects.filter(tags=headline)#.filter(tags=quiz_level[0])
                    #quiz_level.pop(quiz_level[0])
                    if _questions:
                        temp_question_set.add(random.choice(_questions))
                    headline_counter += 1
                    if headline_counter > questions * 5:
                        break
                question_set |= temp_question_set
        serializer = QuestionSerializer(question_set, many=True)
        return serializer.data

    data = request.data
    h1_ids = data.pop('headlines', None)
    question_number = data.pop('question_num', None)
    quiz_level = data.pop('quiz_level', None)
    duration = data.pop('duration', None)

    if check_user(data):
        h1s = H1.objects.filter(id__in=h1_ids)

        start = time.perf_counter()
        weighted_modules = weight_module(h1s, question_number)
        end = time.perf_counter()
        print(end - start)

        start = time.perf_counter()
        weighted_lessons = weight_lessons(h1s)
        end = time.perf_counter()
        print(end - start)

        print('------------------------------------------------')
        print(weighted_lessons)
        start = time.perf_counter()
        lesson_headline = lesson_headlines(weighted_lessons, h1s)
        # print(lesson_headline)
        end = time.perf_counter()
        print(end - start)

        start = time.perf_counter()
        modules_lessons_weights = lesson_module(weighted_modules, weighted_lessons)
        end = time.perf_counter()
        print(end - start)
        start = time.perf_counter()
        modules_lessons_normalized_weights = normalize_lessons_weight(modules_lessons_weights)
        end = time.perf_counter()
        print(end - start)
        # print(modules_lessons_normalized_weights)
        # level = quiz_level(quiz_level, question_number)
        start = time.perf_counter()
        questions = get_questions(lesson_headline, modules_lessons_normalized_weights)
        end = time.perf_counter()
        print(end - start)
        endf = time.perf_counter()
        print(endf - startf)
        return Response(questions)


    else:
        return Response(0)


@api_view(['POST'])
def marking(request):
    data = request.data
    answers = data.pop('answers', None)
    subject = data.pop('subject', None)
    # print(answers)
    if check_user(data):
        user = get_user(data)

        attempt_duration = 0
        ideal_duration = datetime.timedelta(seconds=0)
        correct_questions = 0
        headline_set = set()

        subject = Subject.objects.get(id=subject)
        quiz = UserQuiz.objects.create(subject=subject, user=user)
        print(quiz.id)
        for ID, ans in answers.items():
            question = Question.objects.get(id=ID)
            if hasattr(question, 'finalanswerquestion'):  # TODO: check
                answer = UserFinalAnswer.objects.create(body=ans.get('body', None),
                                                        duration=datetime.timedelta(seconds=ans['duration']),
                                                        question=question, quiz=quiz)
                correct_questions += 1 if answer == question.finalanswerquestion.correct_answer else 0

            elif hasattr(question, 'multiplechoicequestion'):
                choice = AdminMultipleChoiceAnswer.objects.filter(id=ans.get('id', None)).first()

                answer = UserMultipleChoiceAnswer.objects.create(choice=choice,
                                                                 duration=datetime.timedelta(seconds=ans['duration']),
                                                                 question=question, quiz=quiz)
                correct_questions += 1 if answer == question.multiplechoicequestion.correct_answer else 0

            ideal_duration += question.idealDuration if question.idealDuration is not None else datetime.timedelta(seconds=0)
            attempt_duration += answer.duration.total_seconds()

            # tags = question.tags.all()
            # for tag in tags:
            #     if hasattr(tag, 'headbase'):
            #         tag = tag.headbase
            #         if hasattr(tag, 'h1'):
            #             main_headline = tag.h1
            #             break
            #         elif hasattr(tag, 'headline'):
            #             main_headline = tag.headline
            #             headline = tag
            #             while hasattr(headline, 'headline'):
            #                 headline = headline.headline.parent_headline
            #             lesson = headline.h1.lesson
            #             break
            # headline_set.update(set(question.tags.filter(instance_of=HeadBase)))

        attempt_duration = "{}".format(str(datetime.timedelta(seconds=attempt_duration)))
        return Response({'correct_questions': correct_questions, 'total_question_num': len(answers), 'attempt_duration': attempt_duration, 'ideal_duration':ideal_duration, 'quiz_id':quiz.id})
    else:
        return Response(0)


# @api_view(['POST'])
# def retake_quiz(request):
#     data = request.data
#     question_id = data.pop('question_id', None)
#
#     if check_user(data):
#         user = get_user(data)
#         UserQuiz.objects.filter(user=user).order_by('creationDate');
#         QuestionSerializer(question_set, many=True)


@api_view(['POST'])
def quiz_review(request):
    data = request.data
    quiz_id = data.pop('quiz_id', None)

    if check_user(data):
        quiz = UserQuiz.objects.get(id=quiz_id)
        answers = UserAnswer.objects.filter(quiz=quiz)
        answers_serializer = UserAnswerSerializer(answers, many=True).data
        return Response({'answers': answers_serializer, 'quiz_duration': quiz.duration, 'quiz_subject': quiz.subject.name})

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

    if check_user(data):
        user = get_user(data)
        Report.objects.create(user=user, body=body)
        return Response()

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
            cho, _ = AdminMultipleChoiceAnswer.objects.get_or_create(body=list(choice.keys())[0], notes=list(choice.values())[0])
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


@api_view(['POST'])
def similar_questions(request):
    def similar_by_headlines(question, question_weight):
        levels_weight = [15, 10, 6, 3, 1, 0]
        # get lesson
        tags = question.tags.all()
        for tag in tags:
            if hasattr(tag, 'headbase'):
                tag = tag.headbase
                if hasattr(tag, 'h1'):
                    main_headline = tag.h1
                    lesson = main_headline.lesson
                    break
                elif hasattr(tag, 'headline'):
                    main_headline = tag.headline
                    headline = tag
                    while hasattr(headline, 'headline'):
                        headline = headline.headline.parent_headline
                    lesson = headline.h1.lesson
                    break
        # add headlines questions
        headlines = lesson.get_all_headlines()
        questions = Question.objects.filter(tags__in=headlines)
        for question in questions:
            question_weight[question.id] = question_weight.get(question.id, 0)

        # weight the headlines
        wastes_headlines = {main_headline}
        weighted_headlines = {levels_weight[0]: {main_headline}}
        wastes_headlines |= set(main_headline.get_all_child_headlines())
        weighted_headlines[levels_weight[1]] = set(main_headline.get_all_child_headlines())
        similarity_level = 1
        while hasattr(main_headline, 'parent_headline'):
            main_headline = main_headline.parent_headline
            if hasattr(main_headline, 'headline'):
                main_headline = main_headline.headline
                weighted_headlines[levels_weight[similarity_level+1]] = (set(main_headline.get_all_child_headlines()) | {main_headline}) - wastes_headlines
                wastes_headlines |= weighted_headlines[levels_weight[similarity_level+1]]
            elif hasattr(main_headline, 'h1'):
                main_headline = main_headline.h1
                weighted_headlines[levels_weight[similarity_level + 1]] = (set(main_headline.get_all_child_headlines()) | {
                    main_headline}) - wastes_headlines
                wastes_headlines |= weighted_headlines[levels_weight[similarity_level + 1]]
            similarity_level += 1
        weighted_headlines[levels_weight[similarity_level + 1]] = set(lesson.get_all_headlines()) - wastes_headlines
        # print(weighted_headlines)

        # add question weight
        for weight, headlines in weighted_headlines.items():
            questions = Question.objects.filter(tags__in=headlines)
            for question in questions:
                question_weight[question.id] += weight

        return question_weight

    def similar_by_author(question, question_weight):
        author_name = question.author
        questions = Question.objects.filter(author=author_name)
        for question in questions:
            question_weight[question.id] = question_weight.get(question.id, 0) + 2
        return question_weight

    def similar_by_level(question, question_weight):
        tags = question.tags.all()
        for tag in tags:
            if hasattr(tag, 'questionlevel'):
                level = tag.questionlevel
                break
        questions = Question.objects.filter(tags=level)
        for question in questions:
            question_weight[question.id] = question_weight.get(question.id, 0) + 3
        return question_weight

    data = request.data
    question = data.pop('question', None)
    by_headlines = data.pop('by_headlines', False)
    by_author = data.pop('by_author', False)
    by_level = data.pop('by_level', False)

    question = Question.objects.get(id=question)
    question_weight = {}
    if by_headlines:
        question_weight = similar_by_headlines(question, question_weight)
    if by_author:
        question_weight = similar_by_author(question, question_weight)
    if by_level:
        question_weight = similar_by_level(question, question_weight)

    sorted_question = sorted(question_weight.keys(), key=lambda x: question_weight[x])
    questions = []
    for question_id in sorted_question:
        questions.append(Question.objects.get(id=question_id))

    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)
# {
#         "question": "8d7d2efc-b678-496b-b705-ef91a2091c61",
#         "by_headlines": 1,
#         "by_author": 0,
#         "by_level": 0
# }


def demo():
    ques = MultipleChoiceQuestion.objects.all()
    for i in ques:
        if i.correct_answer not in i.choices.all():
            i.choices.add(i)
