from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import viewsets, status

from rest_framework_simplejwt import views as jwt_views

from accounts import serializers
from accounts.permissions import IsUnauthenticated


class UserViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], permission_classes=[IsUnauthenticated])
    def register(self, request):
        serializer = serializers.UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(data={'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsUnauthenticated])
    def login(self, request):
        return jwt_views.token_obtain_pair(request._request)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        return jwt_views.token_blacklist(request._request)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def refresh(self, request):
        return jwt_views.token_refresh(request._request)
