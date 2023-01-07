from rest_framework import serializers
from .models import Subject, Skill, Module, Lesson, Question, Choice


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'semester']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['id', 'name', 'skills']


class ModuleSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField('status_value')

    @staticmethod
    def status_value(obj):
        return False

    def get_lessons(self, obj):
        lessons = obj.lesson_set.all()
        serializer = LessonSerializer(lessons, many=True)
        return serializer.data

    class Meta:
        model = Module
        fields = ['name', 'status', 'lessons']


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'body']


class QuestionSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()

    def get_choices(self, obj):
        choices = obj.choice_set.all()
        print(choices)
        serializer = ChoiceSerializer(choices, many=True)
        return serializer.data

    class Meta:
        model = Question
        fields = ['id', 'body', 'correct_answer', 'image', 'choices']
