from datetime import timedelta

from django.db.models import Sum
from rest_framework import serializers
from .models import Subject, Tag, Module, Lesson, Question, FinalAnswerQuestion, MultipleChoiceQuestion, \
    AdminMultipleChoiceAnswer, H1, UserAnswer, AdminFinalAnswer, UserFinalAnswer, UserMultipleChoiceAnswer, UserQuiz


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


class AdminFinalAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminFinalAnswer
        fields = ['id', 'body']


class AdminMultipleChoiceAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminMultipleChoiceAnswer
        fields = ['id', 'body', 'image']


class FinalAnswerQuestionSerializer(serializers.ModelSerializer):
    correct_answer = AdminFinalAnswerSerializer(many=False)

    class Meta:
        model = FinalAnswerQuestion
        fields = ['id', 'body', 'image', 'idealDuration', 'hint', 'correct_answer']


class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    correct_answer = AdminMultipleChoiceAnswerSerializer(many=False)
    choices = AdminMultipleChoiceAnswerSerializer(many=True)

    class Meta:
        model = MultipleChoiceQuestion
        fields = ['id', 'body', 'image', 'idealDuration', 'hint', 'correct_answer', 'choices']


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


class UserFinalAnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(many=False)

    class Meta:
        model = UserFinalAnswer
        fields = ['body', 'duration', 'question']


class UserMultipleChoiceAnswerSerializer(serializers.ModelSerializer):
    choice = AdminMultipleChoiceAnswerSerializer(many=False)
    question = QuestionSerializer(many=False)

    class Meta:
        model = UserMultipleChoiceAnswer
        fields = ['choice', 'duration', 'question']


class UserAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAnswer
        fields = '__all__'

    def to_representation(self, obj):
        if hasattr(obj, 'usermultiplechoiceanswer'):
            serializer = UserMultipleChoiceAnswerSerializer(obj.usermultiplechoiceanswer).data
        elif hasattr(obj, 'userfinalanswer'):
            serializer = UserFinalAnswerSerializer(obj.userfinalanswer).data
        else:
            serializer = super().to_representation(obj)
        return serializer


class UserQuizSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()
    creationDate = serializers.DateTimeField(format='%I:%M %p • %d/%m/%Y %A')
    duration = serializers.SerializerMethodField()
    attempt_duration = serializers.SerializerMethodField()

    class Meta:
        model = UserQuiz
        fields = ['id', 'subject', 'creationDate', 'duration', 'attempt_duration']

    def get_subject(self, obj):
        return obj.subject.name

    def get_duration(self, obj):
        return obj.duration.total_seconds()

    def get_attempt_duration(self, obj):
        total_duration = obj.useranswer_set.aggregate(Sum('duration'))['duration__sum']
        total_duration_seconds = total_duration.total_seconds() if total_duration else 0
        return total_duration_seconds

