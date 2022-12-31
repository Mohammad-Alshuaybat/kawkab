from rest_framework.decorators import api_view
from rest_framework.response import Response

from user.models import User
from .models import Subject, Skill, Module, Question, Lesson, Choice
from .serializers import SubjectSerializer, SkillSerializer, ModuleSerializer, QuestionSerializer

import random


@api_view(['POST'])
def subject_set(request):
    data = request.data

    try:
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
        skills = Skill.objects.filter(subject__id=subject_id)
        serializer = SkillSerializer(skills, many=True)
        return Response(serializer.data)
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
def skills_quiz(request):
    data = request.data
    skills = data.pop('skills', None)
    question_num = data.pop('question_num', None)
    question_set = set()
    try:
        User.objects.get(**data)
        counter = 0
        while len(question_set) < question_num:
            questions = Question.objects.filter(skills=skills[counter % len(skills)])
            if len(questions) >= 1:
                question_set.add(random.choice(questions))
            counter += 1
            if counter > question_num * 3:
                break

        serializer = QuestionSerializer(question_set, many=True)
        return Response(serializer.data)
    except:
        return Response(0)


@api_view(['POST'])
def lessons_quiz(request):
    data = request.data
    lessons = data.pop('lessons', None)
    question_num = data.pop('question_num', None)

    skills = []
    for lesson in lessons:
        skills += list(Lesson.objects.get(id=lesson).skills.all().values_list('id', flat=True))

    skills = list(set(skills))
    question_set = set()
    try:
        User.objects.get(**data)
        counter = 0
        while len(question_set) < question_num:
            questions = Question.objects.filter(skills=skills[counter % len(skills)])
            if len(questions) >= 1:
                question_set.add(random.choice(questions))
            counter += 1
            if counter > question_num * 3:
                break

        serializer = QuestionSerializer(question_set, many=True)
        return Response(serializer.data)
    except:
        return Response(0)


@api_view(['POST'])
def add_question(request):
    data = request.data
    skills = data.pop('skills', None)
    generalSkills = data.pop('generalSkills', None)
    choices = data.pop('choices', None)

    question = Question.objects.create(**data)
    for skill in skills:
        _skill, _ = Skill.objects.get_or_create(name=skill)
        question.skills.add(_skill)

    for generalSkill in generalSkills:
        _skill, _ = Skill.objects.get_or_create(name=generalSkill, type='general')
        question.skills.add(_skill)

    for choice in choices:
        Choice.objects.create(body=choice, question=question)

    return Response(1)
