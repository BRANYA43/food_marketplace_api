from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status

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
