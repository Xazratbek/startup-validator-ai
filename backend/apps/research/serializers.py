from rest_framework import serializers
from .models import ResearchRun, ResearchSource, EvidenceItem, Competitor

class ResearchSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResearchSource
        fields = '__all__'

class EvidenceItemSerializer(serializers.ModelSerializer):
    source = ResearchSourceSerializer(read_only=True)
    class Meta:
        model = EvidenceItem
        fields = '__all__'

class CompetitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competitor
        fields = '__all__'

class ResearchRunSerializer(serializers.ModelSerializer):
    evidence_items = EvidenceItemSerializer(many=True, read_only=True)
    competitors = CompetitorSerializer(many=True, read_only=True)
    class Meta:
        model = ResearchRun
        fields = '__all__'
