from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Client
from .serializers import ClientSerializer,ProjectSerializer
from django.contrib.auth.models import User 

class ClientViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        queryset = Client.objects.all()
        serializer = ClientSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)    
    
    def create(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = ClientSerializer(data=request.data)
        if serializer.is_valid():
            client = serializer.save(created_by=request.user)
            return Response(ClientSerializer(client).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response({"detail": "Client not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ClientSerializer(client, context={'request': request})
        return Response(serializer.data)


    def update(self, request, pk=None):
        try:
            client = Client.objects.get(pk=pk)
        except Client.DoesNotExist:
            return Response({"detail": "Client not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ClientSerializer(client, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            client = serializer.save()
            return Response(ClientSerializer(client, context={'request': request}).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk=None):
        return self.update(request, pk)
    def destroy(self, request, pk=None):
        try:
            client = Client.objects.get(pk=pk)
            client.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Client.DoesNotExist:
            return Response({"detail": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Project, Client
from .serializers import ProjectSerializer

class ProjectViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        print(f"Logged-in user: {user}")

        queryset = Project.objects.filter(users=user)
        print(f"Projects found: {queryset.count()}")

        serializer = ProjectSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, client_pk=None):
        print(f"Request data: {request.data}")
        print(f"Client PK from URL: {client_pk}")

        try:
            client = Client.objects.get(pk=client_pk)
        except Client.DoesNotExist:
            return Response({"detail": "Client not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            project = serializer.save(client=client, created_by=request.user)
            
            users_data = request.data.get('users', [])
            for user_data in users_data:
                try:
                    user = User.objects.get(id=user_data['id'])
                    project.users.add(user)
                except User.DoesNotExist:
                    return Response({"detail": f"User with ID {user_data['id']} not found."}, status=status.HTTP_404_NOT_FOUND)
            
            project.save()

            response_serializer = ProjectSerializer(project)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)