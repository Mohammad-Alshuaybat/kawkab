from datetime import timedelta

from django.db.models import Sum
from rest_framework import serializers
from .models import Subject, Tag, Module, Lesson, Question, FinalAnswerQuestion, MultipleChoiceQuestion, \
    AdminMultipleChoiceAnswer, H1, UserAnswer, AdminFinalAnswer, UserFinalAnswer, UserMultipleChoiceAnswer, UserQuiz, \
    MultiSectionQuestion, UserMultiSectionAnswer


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
        fields = ['id', 'body', 'image', 'notes']


class FinalAnswerQuestionSerializer(serializers.ModelSerializer):
    correct_answer = AdminFinalAnswerSerializer(many=False)
    level = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    headlines = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = FinalAnswerQuestion
        fields = ['id', 'body', 'image', 'level', 'author', 'headlines', 'idealDuration', 'hint', 'correct_answer', 'type']

    def get_type(self, obj):
        return 'finalAnswerQuestion'

    def get_level(self, obj):
        return round(obj.tags.exclude(questionlevel=None).first().questionlevel.level)

    def get_author(self, obj):
        return obj.tags.exclude(author=None).first().author.name

    def get_headlines(self, obj):
        tags = obj.tags.exclude(headbase=None).all()
        headlines = []
        for tag in tags:
            headbase = tag.headbase
            if hasattr(headbase, 'h1'):
                headlines.append({'headline': headbase.name, 'level': 1})
            else:
                headlines.append({'headline': headbase.name, 'level': headbase.headline.level})
        return headlines


class MultipleChoiceQuestionSerializer(serializers.ModelSerializer):
    correct_answer = AdminMultipleChoiceAnswerSerializer(many=False)
    choices = AdminMultipleChoiceAnswerSerializer(many=True)
    level = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    headlines = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = MultipleChoiceQuestion
        fields = ['id', 'body', 'image', 'level', 'author', 'headlines', 'idealDuration', 'hint', 'correct_answer', 'choices', 'type']

    def get_type(self, obj):
        return 'multipleChoiceQuestion'

    def get_level(self, obj):
        return round(obj.tags.exclude(questionlevel=None).first().questionlevel.level)

    def get_author(self, obj):
        return obj.tags.exclude(author=None).first().author.name

    def get_headlines(self, obj):
        tags = obj.tags.exclude(headbase=None).all()
        headlines = []
        for tag in tags:
            headbase = tag.headbase
            if hasattr(headbase, 'h1'):
                headlines.append({'headline': headbase.name, 'level': 1})
            else:
                headlines.append({'headline': headbase.name, 'level': headbase.headline.level})
        return headlines


class MultiSectionQuestionSerializer(serializers.ModelSerializer):
    sub_questions = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()

    class Meta:
        model = MultiSectionQuestion
        fields = ['id', 'body', 'image', 'author', 'idealDuration', 'hint', 'sub_questions', 'type']

    def get_sub_questions(self, obj):
        sub_questions = []
        for question in obj.sub_questions.all():
            if hasattr(question, 'finalanswerquestion'):
                sub_questions.append(FinalAnswerQuestionSerializer(question.finalanswerquestion).data)
            elif hasattr(question, 'multiplechoicequestion'):
                sub_questions.append(MultipleChoiceQuestionSerializer(question.multiplechoicequestion).data)
        return sub_questions

    def get_author(self, obj):
        return obj.tags.exclude(author=None).first().author.name

    def get_type(self, obj):
        return 'multiSectionQuestion'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

    def to_representation(self, obj):
        if hasattr(obj, 'finalanswerquestion'):
            serializer = FinalAnswerQuestionSerializer(obj.finalanswerquestion).data
        elif hasattr(obj, 'multiplechoicequestion'):
            serializer = MultipleChoiceQuestionSerializer(obj.multiplechoicequestion).data
        elif hasattr(obj, 'multisectionquestion'):
            serializer = MultiSectionQuestionSerializer(obj.multisectionquestion).data
        else:
            serializer = super().to_representation(obj)
        return serializer


class UserFinalAnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(many=False)
    is_correct = serializers.SerializerMethodField()

    class Meta:
        model = UserFinalAnswer
        fields = ['body', 'duration', 'question', 'is_correct']

    def get_is_correct(self, obj):
        return obj == obj.question.finalanswerquestion.correct_answer


class UserMultipleChoiceAnswerSerializer(serializers.ModelSerializer):
    choice = AdminMultipleChoiceAnswerSerializer(many=False)
    question = QuestionSerializer(many=False)
    is_correct = serializers.SerializerMethodField()

    class Meta:
        model = UserMultipleChoiceAnswer
        fields = ['choice', 'duration', 'question', 'is_correct']

    def get_is_correct(self, obj):
        return obj == obj.question.multiplechoicequestion.correct_answer


class UserMultiSectionAnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(many=False)
    sub_questions_answers = serializers.SerializerMethodField()
    is_correct = serializers.SerializerMethodField()

    class Meta:
        model = UserMultiSectionAnswer
        fields = ['sub_questions_answers', 'duration', 'question', 'is_correct']

    def get_sub_questions_answers(self, obj):
        sub_questions_answers = {}
        for answer in obj.sub_questions_answers.all():
            if hasattr(answer, 'userfinalanswer'):
                sub_questions_answers[answer.userfinalanswer.question.id] = answer.userfinalanswer.body
            elif hasattr(answer, 'usermultiplechoiceanswer'):
                sub_questions_answers[answer.usermultiplechoiceanswer.question.id] = answer.usermultiplechoiceanswer.choice.id
        return sub_questions_answers

    def get_is_correct(self, obj):
        is_correct_for_all_sections = True
        if obj.question.multisectionquestion.sub_questions.count() != obj.sub_questions_answers.count():
            return False
        for answer in obj.sub_questions_answers.all():
            if hasattr(answer, 'userfinalanswer'):
                is_correct_for_all_sections = is_correct_for_all_sections and answer.userfinalanswer == answer.userfinalanswer.question.finalanswerquestion.correct_answer
            elif hasattr(answer, 'usermultiplechoiceanswer'):
                is_correct_for_all_sections = is_correct_for_all_sections and answer.usermultiplechoiceanswer == answer.usermultiplechoiceanswer.question.multiplechoicequestion.correct_answer
        return is_correct_for_all_sections


class UserAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserAnswer
        fields = '__all__'

    def to_representation(self, obj):
        if hasattr(obj, 'usermultiplechoiceanswer'):
            serializer = UserMultipleChoiceAnswerSerializer(obj.usermultiplechoiceanswer).data
        elif hasattr(obj, 'userfinalanswer'):
            serializer = UserFinalAnswerSerializer(obj.userfinalanswer).data
        elif hasattr(obj, 'usermultisectionanswer'):
            serializer = UserMultiSectionAnswerSerializer(obj.usermultisectionanswer).data
        else:
            serializer = super().to_representation(obj)
        return serializer
