from rest_framework import serializers
from .models import ScoringResult
class ScoringResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoringResult
        fields = '__all__'
