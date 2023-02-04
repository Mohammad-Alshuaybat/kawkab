from rest_framework.decorators import api_view
from rest_framework.response import Response

from user.models import User
from user.utils import check_user, get_user
from .models import Subject, Skill, Module, Question, Lesson, GeneralSkill, FinalAnswerQuestion, AdminFinalAnswer, \
    MultipleChoiceQuestion, AdminMultipleChoiceAnswer, QuestionLevel
from .serializers import SubjectSerializer, TagSerializer, ModuleSerializer

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
def marking(request):

    def check_lesson(_skills):
        lessons = Lesson.objects.filter(skills__in=_skills)
        lesson_dic = {}
        for lesson in lessons:
            lesson_dic[lesson] = 1-len(set(lesson.skills.all()).difference(set(_skills)))/lesson.skills.count()
        return lesson_dic

    def check_module(_skills):
        modules = Module.objects.filter(lesson__skills__in=_skills)
        mod_dic = {}
        for module in modules:
            mod_dic[module] = 1 - len(module.skills.difference(set(_skills))) / len(module.skills)
        return mod_dic

    def lesson_module(module_ques, lesson_per):
        modules_lessons = {}
        lessons_ques = {}

        for module in module_ques.keys():
            modules_lessons[module] = set(lesson_per.keys()).intersection(module.lesson_set.all())

        for module, lessons in modules_lessons.items():
            lessons_ques = {**lessons_ques, **distribute_questions(module_ques[module], {lesson: lesson_per[lesson] for lesson in lessons})}

        return lessons_ques

    def skill_lesson(lesson_ques, skill_set):
        lesson_skill = {}
        skill_ques = {}

        for lesson in lesson_ques.keys():
            lesson_skill[lesson] = skill_set.intersection(lesson.skills.all())

        for lesson, skills in lesson_skill.items():
            skill_ques = {**skill_ques, **distribute_questions(lesson_ques[lesson], skills)}

        return skill_ques

    def questions(skill_ques):
        question_list = set()
        for skill, question_num in skill_ques.items():
            question_set = set()
            check = 0
            while len(question_set) < question_num:
                questions = Question.objects.filter(skills=skill)
                if len(questions) >= 1:
                    question_set.add(random.choice(questions))
                if check > question_num*5:
                    break
            question_list = question_list | question_set
        return question_list

    def distribute_questions(question_num, percentages):
        distribution_set = {}

        if isinstance(percentages, dict):
            total_percentage = sum(percentages.values())

            for key, percentage in percentages.items():
                distribution_set[key] = int(question_num * (percentage / total_percentage)) if int(
                    question_num * (percentage / total_percentage)) != 0 else 1
        else:
            total_percentage = len(percentages)

            for key in percentages:
                distribution_set[key] = int(question_num * (1 / total_percentage)) if int(
                    question_num * (1 / total_percentage)) != 0 else 1

        while sum(distribution_set.values()) != question_num:
            if sum(distribution_set.values()) < question_num:
                distribution_set[random.choice(list(percentages))] += 1
            else:
                distribution_set[max(distribution_set, key=distribution_set.get)] -= 1

        return distribution_set

    data = request.data
    # answers = data.pop('answers', None)
    # subject = data.pop('subject', None)
    answers = {'7ea0caad-8947-4e5b-8e78-a9deeb771ac1': {'duration': 4, 'body': '1'},
               'f3692291-3e19-4548-8614-fd3fedbf321a': {'duration': 6, 'body': '0'},
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

    import time

    skill_set = set(question.skills.all())

    start = time.perf_counter()
    print(distribute_questions(2, check_lesson(skill_set)))
    end = time.perf_counter()
    print(end - start)

    start = time.perf_counter()
    print(distribute_questions(2, check_module(skill_set)))
    end = time.perf_counter()
    print(end - start)

    print(lesson_module(distribute_questions(2, check_module(skill_set)), check_lesson(skill_set)))

    print(questions(skill_lesson(lesson_module(distribute_questions(2, check_module(skill_set)), check_lesson(skill_set)), skill_set)))
    return Response(1)


@api_view(['POST'])
def module_lesson_skill(request):
    data = request.data
    subject_id = data.pop('subject_id', None)

    try:
        user = User.objects.get(**data)
        modules = Module.objects.filter(subject__id=subject_id)
        serializer = ModuleSerializer(modules, many=True)
        return Response(serializer.data)
    except:
        return Response(0)

# @api_view(['POST'])
# def lessons_quiz(request):
#     data = request.data
#     lessons = data.pop('lessons', None)
#     question_num = data.pop('question_num', None)
#
#     skills = []
#     for lesson in lessons:
#         skills += list(Lesson.objects.get(id=lesson).skills.all().values_list('id', flat=True))
#
#     skills = list(set(skills))
#     question_set = set()
#     try:
#         User.objects.get(**data)
#         counter = 0
#         while len(question_set) < question_num:
#             questions = Question.objects.filter(skills=skills[counter % len(skills)])
#             if len(questions) >= 1:
#                 question_set.add(random.choice(questions))
#             counter += 1
#             if counter > question_num * 3:
#                 break
#
#         serializer = QuestionSerializer(question_set, many=True)
#         return Response(serializer.data)
#     except:
#         return Response(0)
    # @api_view(['POST'])
    # def lessons_quiz(request):
    #     data = request.data
    #     skills = data.pop('skills', None)
    #     question_num = data.pop('question_num', None)
    #     print(skills)
    # [skills]
    # modules = {}
    # Lesson.objects.filter(skills)
    # for lesson in lessons:
    #   modules['lesson.module.id'].add(lesson.id)
    #
    # dic = {
    #     '1': {
    #         'lessons': [
    #             {'a': {
    #                 'skills': ['+', '-'],
    #                 'skills_num': 2
    #             }},
    #             {'b': {
    #                 'skills': ['*'],
    #                 'skills_num': 1
    #             }}
    #         ],
    #         'skills_num': 3
    #     },
    #     '2': {
    #         'lessons': [
    #             {'c': {
    #                 'skills': ['^', '%', '$'],
    #                 'skills_num': 3
    #             }},
    #             {'d': {
    #                 'skills': ['#'],
    #                 'skills_num': 1
    #             }}
    #         ],
    #         'skills_num': 4
    #     }
    # }
    # # 10
    # question_num = [0.4, 0.5]
    #
    # return Response(0)


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

    for index, row in df.iterrows():
        row = row.to_dict()
        qes, _ = Question.objects.get_or_create(id=row['id'], body=row['body'])
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

    skills = ['fc2d75ee-65b4-4ac1-bb04-7545d516482f', '831e0cb9-7aac-45cd-b81d-76fa3a4ca2e5', '405f405e-d9ee-4a9c-a2d9-0fb8370559bb', '60f2adf8-c9f7-46ea-9271-cb74e1ee22ad', 'b071031d-6a9f-4fe5-8433-1e2ea703b9e4',
              '1980e4ac-2e08-4c77-99e2-247c58b5dd36', 'e99c2d17-11b6-45b9-bb33-3ec6ba3cf416']
    general_skills = ['fe495661-6d99-47a3-8180-8ab97c76770b', '92d22737-379f-4b7d-ac44-bb28154d6851']
    question_num = 10

    skls = set()
    for i in skills:
        skls.add(Skill.objects.get(id=i))

    def weight_module(_skills):
        modules = Module.objects.filter(lesson__skills__in=_skills)
        module_weights = {}
        for module in modules:
            module_weights[str(module.id)] = len(set(module.skills).intersection(_skills)) / module.skills.count()

        sum_weights = sum(module_weights.values())
        module_weights = {module: weight / sum_weights for module, weight in module_weights.items()}

        return module_weights

    def weight_lessons(_skills):
        lessons = Lesson.objects.filter(skills__in=_skills)
        lesson_weights = {}
        for lesson in lessons:
            lesson_weights[str(lesson.id)] = len(set(lesson.skills.all()).intersection(_skills)) / lesson.skills.count()

        sum_weights = sum(lesson_weights.values())
        lesson_weights = {lesson: weight / sum_weights
                          for lesson, weight in lesson_weights.items()}

        return lesson_weights

    def distribute_questions(question_num, percentages):  # TODO reformat
        distribution_set = {}

        if isinstance(percentages, dict):
            total_percentage = sum(percentages.values())

            for key, percentage in percentages.items():
                distribution_set[key] = int(question_num * (percentage / total_percentage)) or 1

        else:
            total_percentage = len(percentages)

            for key in percentages:
                distribution_set[str(key.id)] = int(question_num * (1 / total_percentage)) or 1
        # while sum(distribution_set.values()) != question_num:
        #     if sum(distribution_set.values()) < question_num:
        #         distribution_set[random.choice(list(percentages))] += 1
        #     else:
        #         distribution_set[max(distribution_set, key=distribution_set.get)] -= 1

        return distribution_set

    def lesson_module(module_ques, lesson_weights):  # TODO reformat
        modules_lessons = {}
        lessons_ques = {}

        lessons = set()
        for lesson in lesson_weights.keys():
            lessons.add(Lesson.objects.get(id=lesson))

        for module in module_ques.keys():
            modules_lessons[module] = lessons.intersection(Module.objects.get(id=module).lesson_set.all())

        for module, lessons in modules_lessons.items():
            lessons_ques.update(distribute_questions(module_ques[module],
                                                     {str(lesson.id): lesson_weights[str(lesson.id)] for lesson in
                                                      lessons}))
        return lessons_ques

    def skill_lesson(lesson_ques, _skills):
        lesson_skill = {}
        skill_ques = {}

        for lesson in lesson_ques.keys():
            lesson_skill[lesson] = _skills.intersection(Lesson.objects.get(id=lesson).skills.all())
            # {skill_set.intersection(lesson.skills.all()):1} to remove else in distributeQuestion
        for lesson, skills in lesson_skill.items():
            skill_ques.update(distribute_questions(lesson_ques[lesson]*40, skills))

        return skill_ques

    def BQ():
        weighted_modules = weight_module(skls)
        print(weighted_modules)
        weighted_lessons = weight_lessons(skls)
        print(weighted_lessons)
        # module_questions = distribute_questions(8, weighted_modules)
        # lesson_questions = lesson_module(module_questions, weighted_lessons)
        return skill_lesson(weighted_lessons, skls)
    return Response(BQ())

    # try:
    #     User.objects.get(**data)
    #     counter = 0
    #     while len(question_set) < question_num:
    #         questions = Question.objects.filter(skills=skills[counter % len(skills)])
    #         if len(questions) >= 1:
    #             question_set.add(random.choice(questions))
    #         counter += 1
    #         if counter > question_num * 5:
    #             break

    # serializer = QuestionSerializer(question_set, many=True)
    # return Response(serializer.data)
    # except:
    #     return Response(0)


def questions(skill_ques):
    question_list = set()
    for skill, question_num in skill_ques.items():
        question_set = set()
        check = 0
        while len(question_set) < question_num:
            questions = Question.objects.filter(skills=skill)
            if len(questions) >= 1:
                #if questions
                question_set.add(random.choice(questions))
            check += 1
            if check > question_num * 5:
                break
        question_list = question_list | question_set
        #question_list |= question_set

    return question_list


# print(questions(skill_lesson(lesson_module(distribute_questions(2, check_module(skill_set)), check_lesson(skill_set)), skill_set)))
# questions(skill_lesson(lesson_module(distribute_questions(2, check_module(skill_set)), check_lesson(skill_set)), skill_set))
