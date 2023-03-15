from rest_framework import serializers
from .models import Subject, Tag, Module, Lesson, Question, FinalAnswerQuestion, MultipleChoiceQuestion, \
    AdminMultipleChoiceAnswer, H1


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class LessonSerializer(serializers.ModelSerializer):
    h1s = serializers.SerializerMethodField()

    def get_h1s(self, obj):
        h1s = H1.objects.filter(lesson=obj).values_list('id', flat=True)
        # serializer = TagSerializer(h1s, many=True)
        return h1s

    class Meta:
        model = Lesson
        fields = ['name', 'h1s']


class ModuleSerializer(serializers.ModelSerializer):
    lessons = serializers.SerializerMethodField()

    def get_lessons(self, obj):
        lessons = Lesson.objects.filter(module=obj)
        serializer = LessonSerializer(lessons, many=True)
        return serializer.data

    class Meta:
        model = Module
        fields = ['name', 'lessons', 'semester']


class AdminMultipleChoiceAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminMultipleChoiceAnswer
        fields = ['id', 'body', 'image']


class FinalAnswerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalAnswerQuestion
        fields = '__all__'


class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    correct_answer = AdminMultipleChoiceAnswerSerializer(many=False)
    choices = AdminMultipleChoiceAnswerSerializer(many=True)

    class Meta:
        model = MultipleChoiceQuestion
        fields = ['id', 'body', 'image', 'hint', 'correct_answer', 'choices']


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
