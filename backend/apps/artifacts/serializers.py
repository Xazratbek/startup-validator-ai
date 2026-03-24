from rest_framework import serializers
from .models import GeneratedArtifact
class GeneratedArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedArtifact
        fields = '__all__'
