from math import ceil

from rest_framework.decorators import api_view
from rest_framework.response import Response

from user.models import User
from user.utils import check_user, get_user
from .models import Subject, Module, Question, Lesson, FinalAnswerQuestion, AdminFinalAnswer, \
    MultipleChoiceQuestion, AdminMultipleChoiceAnswer, QuestionLevel, H1, HeadLine, HeadBase, UserFinalAnswer, \
    UserMultipleChoiceAnswer, UserQuiz, Author, LastImageName
from .serializers import SubjectSerializer, TagSerializer, ModuleSerializer, \
    QuestionSerializer, FinalAnswerQuestionSerializer, MultipleChoiceQuestionSerializer

import random
import datetime
# import pandas as pd


@api_view(['POST'])
def subject_set(request):
    data = request.data

    if check_user(data):
        user = get_user(data)

        subjects = Subject.objects.filter(grade=user.grade)
        subjectSerializer = SubjectSerializer(subjects, many=True).data

        return Response(subjectSerializer)

    else:
        return Response(0)


@api_view(['POST'])
def skill_set(request):
    data = request.data
    subject_id = data.pop('subject_id', None)

    if check_user(data):
        skills = Skill.objects.filter(subject__id=subject_id)
        skillSerializer = TagSerializer(skills, many=True)

        generalSkills = GeneralSkill.objects.filter(subject__id=subject_id)
        generalSkillSerializer = TagSerializer(generalSkills, many=True)

        skill_set = {'skills': skillSerializer.data, 'generalSkills': generalSkillSerializer.data}
        return Response(skill_set)
    else:
        return Response(0)


@api_view(['POST'])
def module_set(request):
    data = request.data
    subject_id = data.pop('subject_id', None)

    if check_user(data):
        modules = Module.objects.filter(subject__id=subject_id)
        moduleSerializer = ModuleSerializer(modules, many=True).data
        return Response(moduleSerializer)
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
        headline, _ = H1.objects.get_or_create(name=headline)
        question.tags.add(headline)
    else:
        headline, _ = HeadLine.objects.get_or_create(name=headline, level=headline_level)
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
# upload = Upload(file=image_file)
# image_url = upload.file.url
# QuizAnswer.objects.create(duration=datetime.timedelta(seconds = 68400))


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
#     df = pd.read_excel(r'G:\school\data\headlines.xlsx')
#
#     for index, row in df.iterrows():
#         lesson, _ = Lesson.objects.get_or_create(name=row['lesson'])
#         row = row.to_dict()
#         if row['type'] == 1:
#             H1.objects.get_or_create(name=row['name'], lesson=lesson)
#         else:
#             HeadLine.objects.get_or_create(name=row['name'], parent_headline=parent_headline)
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
#
#     return Response()


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
def build_quiz(request):
    data = request.data
    # h1s = data.pop('h1s', None)
    # general_skills = data.pop('general_skills', None)
    # question_num = data.pop('question_num', None)
    # quiz_level = data.pop('quiz_level', None)

    def weight_module(h1s, question_number):
        modules = Module.objects.filter(lesson__h1__in=h1s).distinct()

        module_weights = {}
        for module in modules:
            module_weights[str(module.name)] = len(set(module.get_main_headlines).intersection(h1s)) / module.get_main_headlines.count()

        sum_weights = sum(module_weights.values())
        module_weights = {module: weight / sum_weights * question_number for module, weight in module_weights.items()}

        return module_weights

    def weight_lessons(h1s):
        lessons = Lesson.objects.filter(h1__in=h1s)

        lesson_weights = {}
        for lesson in lessons:
            lesson_weights[str(lesson.name)] = len(set(lesson.get_main_headlines).intersection(h1s)) / lesson.get_main_headlines.count()

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
            lesson_headline[lesson] = h1s.intersection(Lesson.objects.get(name=lesson).get_main_headlines)

        for lesson, h1s in lesson_headline.items():
            h2s = HeadLine.objects.filter(parent_headline__in=h1s)
            h3s = HeadLine.objects.filter(parent_headline__in=h2s)
            h4s = HeadLine.objects.filter(parent_headline__in=h3s)
            h5s = HeadLine.objects.filter(parent_headline__in=h4s)

            lesson_headline[lesson] = set(h1s) | set(h2s) | set(h3s) | set(h4s) | set(h5s)

        return lesson_headline

    def quiz_level(level, number_of_question):
        if level == 1:
            return [QuestionLevel.objects.get(name=1)] * number_of_question
        elif level == 2:
            return random.shuffle([QuestionLevel.objects.get(name=2)] * number_of_question // 2 + [QuestionLevel.objects.get(name=1)] * (number_of_question - number_of_question // 2))
        else:
            return [QuestionLevel.objects.get(name=2)] * number_of_question

    def get_questions(lesson_headline, modules_lessons_normalized_weights, quiz_level):
        question_set = set()

        for module, lessons_weight in modules_lessons_normalized_weights.items():
            for lesson, questions in lessons_weight['lessons'].items():
                headline_counter = 0
                temp_question_set = set()
                while len(temp_question_set) < questions:
                    headline = list(lesson_headline[lesson])[headline_counter % len(lesson_headline[lesson])]

                    _questions = Question.objects.filter(tags=headline).filter(tags=quiz_level[0])
                    quiz_level.pop(quiz_level[0])
                    if _questions:
                        temp_question_set.add(random.choice(_questions))
                    headline_counter += 1
                    if headline_counter > questions * 5:
                        break
                question_set |= temp_question_set
        serializer = QuestionSerializer(question_set, many=True)
        return serializer.data

    def BQ():
        h1s_name = ['حالات خاصة من ضرب المقادير الجبرية', 'التحليل بإخراج العامل المشترك الأكبر', 'التحليل بتجميع الحدود', 'تحليل ثلاثيات الحدود',
                       'حالات خاصة من التحليل', 'تبسيط المقادير الجبرية النسبية', 'SSS', 'SAS', 'HL', 'ASA']

        h1s = set()
        for name in h1s_name:
            h1s.add(H1.objects.get(name=name))

        question_number = 100
        weighted_modules = weight_module(h1s, question_number)
        weighted_lessons = weight_lessons(h1s)
        lesson_headline = lesson_headlines(weighted_lessons, h1s)
        print(lesson_headline)
        modules_lessons_weights = lesson_module(weighted_modules, weighted_lessons)
        modules_lessons_normalized_weights = normalize_lessons_weight(modules_lessons_weights)
        print(modules_lessons_normalized_weights)
        level = quiz_level(quiz_level, question_number)
        questions = get_questions(lesson_headline, modules_lessons_normalized_weights, level)
        return questions
    return Response(BQ())


@api_view(['POST'])
def marking(request):
    data = request.data
    # answers = data.pop('answers', None)
    # subject = data.pop('subject', None)
    # user = User.objects.get(**data)

    answers = {'7ea0caad-8947-4e5b-8e78-a9deeb771ac1': {'duration': 4, 'body': 'f3692291-3e19-4548-8614-fd3fedbf321a'},
               '9e344153-fb83-41fc-8bd1-ac86f7496d33': {'duration': 0, 'body': '3'}}
    subject = 'الرياضيات'

    attempt_duration = 0
    correct_questions = 0
    headline_set = set()

    user = User.objects.get(email='osama@gmail.com')
    subject = Subject.objects.get(name=subject)
    quiz = UserQuiz.objects.create(subject=subject, user=user)
    for ID, ans in answers.items():
        question = Question.objects.get(id=ID)
        if hasattr(question, 'finalanswerquestion'):
            answer = UserFinalAnswer.objects.create(body=ans['body'],
                                                   duration=datetime.timedelta(seconds=ans['duration']),
                                                   question=question, quiz=quiz)
        elif hasattr(question, 'multiplechoicequestion'):
            choice = AdminMultipleChoiceAnswer.objects.get(id=ans['body'])
            answer = UserMultipleChoiceAnswer.objects.create(choice=choice,
                                                   duration=datetime.timedelta(seconds=ans['duration']),
                                                   question=question, quiz=quiz)
        attempt_duration += answer.duration.total_seconds()
        correct_questions += 1 if answer == question.correct_answer else 0
        headline_set.update(set(question.tags.filter(instance_of=HeadBase)))

    return Response({'correct_questions': correct_questions, 'attempt_duration': attempt_duration, 'headline_set': headline_set})


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
        print(weighted_headlines)

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
