# your_app/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet
from .views import ProjectViewSet,ClientViewSet


router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'clients/(?P<client_pk>\d+)/projects', ProjectViewSet, basename='project')
router.register(r'projects', ProjectViewSet, basename='projects')


urlpatterns = [
    path('', include(router.urls)),
]
