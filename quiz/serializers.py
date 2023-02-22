from rest_framework import serializers
from .models import Subject, Tag, Module, Lesson, Question, FinalAnswerQuestion, MultipleChoiceQuestion, \
    AdminMultipleChoiceAnswer


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


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['body', 'skills']


class AdminMultipleChoiceAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminMultipleChoiceAnswer
        fields = '__all__'


class FinalAnswerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalAnswerQuestion
        fields = '__all__'


class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultipleChoiceQuestion
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

    def to_representation(self, obj):
        if hasattr(obj, 'finalanswerquestion'):
            serializer = FinalAnswerQuestionSerializer(obj.finalanswerquestion).data
        elif hasattr(obj, 'multiplechoicequestion'):
            serializer = MultipleChoiceQuestionSerializer(obj.multiplechoicequestion).data
        else:
            serializer = super().to_representation(obj)
        return serializer
