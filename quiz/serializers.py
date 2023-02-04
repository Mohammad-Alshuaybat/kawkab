from rest_framework import serializers
from .models import Subject, Tag, Module, Lesson, Question


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'semester', 'classification']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['name', 'skills']


class ModuleSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    def get_lessons(self, obj):
        lessons = obj.lesson_set.all()
        serializer = LessonSerializer(lessons, many=True)
        return serializer.data

    class Meta:
        model = Module
        fields = ['name', 'lessons']
