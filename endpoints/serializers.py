from rest_framework import serializers
from .models import Activity, Workout

class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = ['id', 'name', 'has_time', 'has_distance', 'distance_unit']

class WorkoutSerializer(serializers.ModelSerializer):
    activity = serializers.PrimaryKeyRelatedField(queryset=Activity.objects.all())

    class Meta:
        model = Workout
        fields = ['id', 'activity', 'date', 'time', 'distance', 'description', 'rpe']
