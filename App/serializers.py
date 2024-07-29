from rest_framework import serializers
from .models import Client, Project
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ProjectSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)  # Read-only for output
    client_name = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'project_name', 'client', 'client_name', 'users', 'created_at', 'created_by']
        read_only_fields = ['client', 'created_at', 'created_by']

    def get_client_name(self, obj):
        return obj.client.client_name

    def get_created_by(self, obj):
        return obj.created_by.username if obj.created_by else None

    def create(self, validated_data):
        users_data = validated_data.pop('users', [])
        project = Project.objects.create(**validated_data)
        for user_data in users_data:
            user = User.objects.get(id=user_data['id'])
            project.users.add(user)
        return project

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['users'] = UserSerializer(instance.users.all(), many=True).data
        return representation
class ClientSerializer(serializers.ModelSerializer):
    created_by = serializers.SerializerMethodField()
    projects = ProjectSerializer(many=True, read_only=True) 
    updated_at = serializers.SerializerMethodField()  
    class Meta:
        model = Client
        fields = ['id', 'client_name', 'projects', 'created_at', 'created_by', 'updated_at']
        read_only_fields = ['created_at', 'created_by', 'updated_at']

    def get_created_by(self, obj):
        return obj.created_by.username

    def get_projects(self, obj):
        request = self.context.get('request')
        if request and request.method == 'GET' and 'pk' in request.resolver_match.kwargs:
            return ProjectSerializer(obj.projects.all(), many=True).data
        return []
    def to_representation(self, instance):
        representation = super().to_representation(instance)
    
        request = self.context.get('request')
        if request and request.method != 'GET':
            representation.pop('projects', None)
        return representation

    def get_updated_at(self, obj):
        request = self.context.get('request')
        if request and request.method in ['GET', 'PUT', 'PATCH']:
            return obj.updated_at.isoformat()
        return None