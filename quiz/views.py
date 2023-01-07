from rest_framework.decorators import api_view
from rest_framework.response import Response

from user.models import User
from .models import Subject, Skill, Module, Question, Lesson, Choice, QuestionAnswer, QuizAnswer
from .serializers import SubjectSerializer, SkillSerializer, ModuleSerializer, QuestionSerializer

import random


@api_view(['POST'])
def subject_set(request):
    data = request.data

    try:
        # if not User.objects.filter(**data).exists():
        #     return 0

        user = User.objects.get(**data)

        subjects = Subject.objects.filter(grade=user.grade)
        scientific = subjects.filter(classification=0)
        scientificSerializer = SubjectSerializer(scientific, many=True)
        literary = subjects.filter(classification=1)
        literarySerializer = SubjectSerializer(literary, many=True)
        return Response({'scientific': scientificSerializer.data,
                         'literary': literarySerializer.data})
    except:
        return Response(0)


@api_view(['POST'])
def skill_set(request):
    data = request.data
    subject_id = data.pop('subject_id', None)

    try:
        user = User.objects.get(**data)
        skills = Skill.objects.filter(subject__id=subject_id, type=1)
        generalSkills = Skill.objects.filter(subject__id=subject_id, type=2)
        skillSerializer = SkillSerializer(skills, many=True)
        generalSkillsSerializer = SkillSerializer(generalSkills, many=True)
        return Response({'skills': skillSerializer.data, 'generalSkills': generalSkillsSerializer.data})
    except:
        return Response(0)


@api_view(['POST'])
def lesson_set(request):
    data = request.data
    subject_id = data.pop('subject_id', None)

    try:
        user = User.objects.get(**data)
        modules = Module.objects.filter(subject__id=subject_id)
        serializer = ModuleSerializer(modules, many=True)
        return Response(serializer.data)
    except:
        return Response(0)


@api_view(['POST'])
def build_quiz(request):
    data = request.data
    skills = data.pop('skills', None)
    general_skills = data.pop('general_skills', None)
    question_num = data.pop('question_num', None)
    quiz_level = data.pop('quiz_level', None)
    question_set = Question.objects.all()[:question_num]

    # question_set = set()
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

    serializer = QuestionSerializer(question_set, many=True)
    return Response(serializer.data)
    # except:
    #     return Response(0)


@api_view(['POST'])
def marking(request):
    def check_answer(Q, A):
        return Q.correct_answer.strip() == A.body.strip()
    data = request.data
    # answers = data.pop('answers', None)
    # subject = data.pop('subject', None)
    answers = {'2d94f4c7-bcae-4043-bf84-ec613e38f5c4': {'duration': 4, 'body': ''},
               '1f87a81e-7102-4cc0-9269-d3f4e4fb42d4': {'duration': 6, 'body': ''},
               '6b762c73-3467-453d-af52-9cf3c1c8d048': {'duration': 0, 'body': '$25k^2-16$'}}
    subject = 'الرياضيات'
    attempt_duration = 0
    correct_questions = 0
    skill_set = set()
    try:
        # user = User.objects.get(**data)
        user = User.objects.get(email='osama@gmail.com')
        subject = Subject.objects.get(name=subject)
        quiz = QuizAnswer.objects.create(subject=subject, user=user)
        for ID, ans in answers.items():
            question = Question.objects.get(id=ID)
            answer = QuestionAnswer.objects.create(body=ans['body'], duration=ans['duration'], question=question, quiz_answer=quiz)
            attempt_duration += answer.duration
            correct_questions += 1 if check_answer(question, answer) else 0
            skill_set.add(question.skills.all())
        print(attempt_duration)
        print(correct_questions)
        print(skill_set)
        return Response(1)
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

    question, _ = Question.objects.get_or_create(**data)

    for skill in skills:
        _skill, _ = Skill.objects.get_or_create(name=skill)
        question.skills.add(_skill)

    for generalSkill in generalSkills:
        _skill, _ = Skill.objects.get_or_create(name=generalSkill, type=2)
        question.generalSkills.add(_skill)

    for choice in choices:
        Choice.objects.create(body=list(choice.keys())[0], info=list(choice.values())[0], question=question)

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
