from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.permissions import IsOwnerORReadOnly
from api.serializers import PostsSerializer
from content.models import Post


class PostsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerORReadOnly, IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostsSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)