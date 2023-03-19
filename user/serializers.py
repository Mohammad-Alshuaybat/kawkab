from rest_framework import serializers

from user.models import User, DailyTask


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class DailyTaskSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()

    def get_subject(self, obj):
        return obj.subject.name

    class Meta:
        model = DailyTask
        fields = ['subject', 'task', 'done']
