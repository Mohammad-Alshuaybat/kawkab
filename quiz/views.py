from math import ceil

from rest_framework.decorators import api_view
from rest_framework.response import Response

from user.models import User
from user.utils import check_user, get_user
from .models import Subject, Skill, Module, Question, Lesson, GeneralSkill, FinalAnswerQuestion, AdminFinalAnswer, \
    MultipleChoiceQuestion, AdminMultipleChoiceAnswer, QuestionLevel
from .serializers import SubjectSerializer, TagSerializer, ModuleSerializer, \
    QuestionSerializer, FinalAnswerQuestionSerializer, MultipleChoiceQuestionSerializer

import random
import datetime
import pandas as pd


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
    skills = data.pop('skills', None)
    generalSkills = data.pop('generalSkills', None)
    choices = data.pop('choices', None)
    correct_answer = data.pop('correct_answer', None)
    level = data.pop('level', None)
    levels = {'0': 'easy', '1': 'inAverage', '2': 'hard'}

    if len(choices) == 0:
        question, _ = FinalAnswerQuestion.objects.get_or_create(**data)
        correct_answer, _ = AdminFinalAnswer.objects.get_or_create(body=correct_answer)
        question.correct_answer = correct_answer
    else:
        question, _ = MultipleChoiceQuestion.objects.get_or_create(**data)
        correct_answer, _ = AdminMultipleChoiceAnswer.objects.get_or_create(body=correct_answer)
        question.correct_answer = correct_answer

        for choice in choices:
            cho, _ = AdminMultipleChoiceAnswer.objects.get_or_create(body=list(choice.keys())[0], notes=list(choice.values())[0])
            question.choices.add(cho)

    for skill in skills:
        _skill, _ = Skill.objects.get_or_create(name=skill)
        question.skills.add(_skill)

    for generalSkill in generalSkills:
        _skill, _ = GeneralSkill.objects.get_or_create(name=generalSkill)
        question.tags.add(_skill)

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
    question.save()
    return Response(1)
# upload = Upload(file=image_file)
# image_url = upload.file.url
# >>> QuizAnswer.objects.create(duration=datetime.timedelta(seconds = 68400))


@api_view(['GET'])
def read_skills_from_xlsx(request):
    df = pd.read_excel(r'G:\school\data\skills.xlsx')

    sub, _ = Subject.objects.get_or_create(name='الرياضيات')
    for index, row in df.iterrows():
        row = row.to_dict()
        if row['type'] == 2:
            GeneralSkill.objects.get_or_create(id=row['id'], name=row['name'], subject=sub)
        else:
            Skill.objects.get_or_create(id=row['id'], name=row['name'], subject=sub)

    for index, row in df.iterrows():
        row = row.to_dict()
        dependencies = str(row['dependencies']).split(',')
        for i in dependencies:
            if i != 'nan':
                dep_skill = Skill.objects.get(id=i)
                Skill.objects.get(id=row['id']).dependencies.add(dep_skill)
    return Response()


@api_view(['GET'])
def read_modules_from_xlsx(request):
    df = pd.read_excel(r'G:\school\data\modules.xlsx')

    sub, _ = Subject.objects.get_or_create(name='الرياضيات')
    for index, row in df.iterrows():
        row = row.to_dict()
        Module.objects.get_or_create(id=row['id'], name=row['name'], subject=sub)

    return Response()


@api_view(['GET'])
def read_lessons_from_xlsx(request):
    df = pd.read_excel(r'G:\school\data\lessons.xlsx')

    for index, row in df.iterrows():
        row = row.to_dict()
        module = Module.objects.get(id=row['module'])
        lsn, _ = Lesson.objects.get_or_create(id=row['id'], name=row['name'], module=module)
        skills = str(row['skills']).split(',')
        for i in skills:
            if i != 'nan':
                skill = Skill.objects.get(id=i)
                lsn.skills.add(skill)
    return Response()


@api_view(['GET'])
def read_questions_from_xlsx(request):
    # images, question type final or multi, correct answer
    df = pd.read_excel(r'G:\school\data\questions.xlsx')
    ques_type = 0
    for index, row in df.iterrows():
        row = row.to_dict()
        if ques_type % 2 == 0:
            qes, _ = FinalAnswerQuestion.objects.get_or_create(id=row['id'], body=row['body'])
        else:
            qes, _ = MultipleChoiceQuestion.objects.get_or_create(id=row['id'], body=row['body'])
        ques_type += 1
        skills = str(row['skills']).split(',')

        for i in skills:
            if i != 'nan':
                skill = Skill.objects.get(id=i)
                qes.skills.add(skill)

        gsk = str(row['generalSkills']).split(',')
        for i in gsk:
            if i != 'nan':
                skill = GeneralSkill.objects.get(id=i)
                qes.tags.add(skill)

    return Response()


@api_view(['POST'])
def build_quiz(request):
    data = request.data
    # skills = data.pop('skills', None)
    # general_skills = data.pop('general_skills', None)
    # question_num = data.pop('question_num', None)
    # quiz_level = data.pop('quiz_level', None)

    def weight_module(_skills, question_number):
        modules = Module.objects.filter(lesson__skills__in=_skills)
        module_weights = {}
        for module in modules:
            module_weights[str(module.name)] = len(set(module.skills).intersection(_skills)) / module.skills.count()

        sum_weights = sum(module_weights.values())
        module_weights = {module: weight / sum_weights * question_number for module, weight in module_weights.items()}

        return module_weights

    def weight_lessons(_skills):
        lessons = Lesson.objects.filter(skills__in=_skills)
        lesson_weights = {}
        for lesson in lessons:
            lesson_weights[str(lesson.name)] = len(set(lesson.skills.all()).intersection(_skills)) / lesson.skills.count()

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

    def lesson_skill(lesson_weight, _skills):
        lessons_skills = {}

        for lesson in lesson_weight.keys():
            lessons_skills[lesson] = _skills.intersection(Lesson.objects.get(name=lesson).skills.all())

        return lessons_skills

    def get_questions(lessons_skills, modules_lessons_normalized_weights):
        question_set = set()
    # hardness
        for module, lessons_weight in modules_lessons_normalized_weights.items():
            for lesson, questions in lessons_weight['lessons'].items():
                counter = 0
                temp_question_set = set()
                while len(temp_question_set) < questions:
                    skill = list(lessons_skills[lesson])[counter % len(lessons_skills[lesson])]
                    _questions = Question.objects.filter(skills=skill)
                    if _questions:
                        temp_question_set.add(random.choice(_questions))
                    counter += 1
                    if counter > questions * 5:
                        break
                question_set |= temp_question_set
        serializer = QuestionSerializer(question_set, many=True)
        return serializer.data

    def distribute_questions_on_dic(question_num, weighted_dic):
        distribution_set = {}

        total_weights = sum(weighted_dic.values())

        for key, weight in weighted_dic.items():
            distribution_set[key] = int(question_num * (weight / total_weights)) or 1

        while sum(distribution_set.values()) != question_num:
            random_key = random.choice(list(weighted_dic.keys()))
            if sum(distribution_set.values()) < question_num:
                distribution_set[random_key] += 1
            elif distribution_set[random_key] != 0:
                distribution_set[random_key] -= 1

        return distribution_set

    def distribute_questions_on_list(question_num, items_list):  # TODO reformat
        distribution_set = {}

        total_percentage = len(items_list)

        for key in items_list:
            distribution_set[str(key.id)] = int(question_num * (1 / total_percentage)) or 1

        while sum(distribution_set.values()) != question_num:
            random_key = str(random.choice(list(items_list)).id)
            if sum(distribution_set.values()) < question_num:
                distribution_set[random_key] += 1
            elif distribution_set[random_key] != 0:
                distribution_set[random_key] -= 1

        return distribution_set

    def BQ():
        skills_name = ['حالات خاصة من ضرب المقادير الجبرية', 'التحليل بإخراج العامل المشترك الأكبر', 'التحليل بتجميع الحدود', 'تحليل ثلاثيات الحدود',
                       'حالات خاصة من التحليل', 'تبسيط المقادير الجبرية النسبية', 'SSS', 'SAS', 'HL', 'ASA']

        skills = set()
        for i in skills_name:
            skills.add(Skill.objects.get(name=i))

        question_number = 100
        weighted_modules = weight_module(skills, question_number)
        weighted_lessons = weight_lessons(skills)
        lessons_skills = lesson_skill(weighted_lessons, skills)
        print(lessons_skills)
        modules_lessons_weights = lesson_module(weighted_modules, weighted_lessons)
        modules_lessons_normalized_weights = normalize_lessons_weight(modules_lessons_weights)
        print(modules_lessons_normalized_weights)
        questions = get_questions(lessons_skills, modules_lessons_normalized_weights)
        return questions
    return Response(BQ())


@api_view(['POST'])
def marking(request):
    data = request.data
    # answers = data.pop('answers', None)
    # subject = data.pop('subject', None)
    answers = {'7ea0caad-8947-4e5b-8e78-a9deeb771ac1': {'duration': 4, 'body': 'f3692291-3e19-4548-8614-fd3fedbf321a'},
               '9e344153-fb83-41fc-8bd1-ac86f7496d33': {'duration': 0, 'body': '3'}}
    subject = 'الرياضيات'
    attempt_duration = 0
    correct_questions = 0
    skill_set = set()

    # user = User.objects.get(**data)
    user = User.objects.get(email='osama@gmail.com')
    subject = Subject.objects.get(name=subject)
    quiz = QuizAnswer.objects.create(subject=subject, user=user)
    for ID, ans in answers.items():
        question = Question.objects.get(id=ID)
        answer = QuestionAnswer.objects.create(body=ans['body'], duration=datetime.timedelta(seconds=ans['duration']), question=question, quiz_answer=quiz)
        attempt_duration += answer.duration.total_seconds()
        correct_questions += 1 if answer.check_answer else 0
        skill_set.update(set(question.skills.all()))

    return Response(1)
