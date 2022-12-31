from rest_framework import serializers
from .models import Subject, Skill, Module, Lesson, Question, Choice


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'semester']


class SkillSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField('status_value')

    @staticmethod
    def status_value(obj):
        return False

    class Meta:
        model = Skill
        fields = ['id', 'name', 'status']


class LessonSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField('status_value')

    @staticmethod
    def status_value(obj):
        return False

    class Meta:
        model = Lesson
        fields = ['id', 'name', 'status']


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
        fields = ['body']


class QuestionSerializer(serializers.ModelSerializer):
    choices = serializers.SerializerMethodField()

    def get_choices(self, obj):
        choices = obj.choice_set.all()
        serializer = ChoiceSerializer(choices, many=True)
        return serializer.data

    class Meta:
        model = Question
        fields = ['id', 'body', 'correct_answer', 'choices']
