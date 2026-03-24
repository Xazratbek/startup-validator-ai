from rest_framework import serializers
from .models import Project, StartupProfileSnapshot, Assumption

class StartupProfileSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = StartupProfileSnapshot
        fields = '__all__'

class AssumptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assumption
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    latest_snapshot = serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = ['id','owner','title','idea_one_liner','raw_description','status','current_decision','latest_research_snapshot','latest_structured_model_snapshot','created_at','updated_at','latest_snapshot']
        read_only_fields = ['owner']
    def get_latest_snapshot(self, obj):
        snapshot = obj.snapshots.first()
        return StartupProfileSnapshotSerializer(snapshot).data if snapshot else None
