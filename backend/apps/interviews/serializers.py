from rest_framework import serializers
from .models import InterviewSession, InterviewMessage

class InterviewMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterviewMessage
        fields = '__all__'

class InterviewSessionSerializer(serializers.ModelSerializer):
    messages = InterviewMessageSerializer(many=True, read_only=True)
    class Meta:
        model = InterviewSession
        fields = '__all__'

class InterviewReplySerializer(serializers.Serializer):
    content = serializers.CharField()
