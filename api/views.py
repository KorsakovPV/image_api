from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from api.permissions import IsOwnerORReadOnly
from content.models import Post


class PostsViewSet(viewsets.ModelViewSet):
    permission_classes = [IsOwnerORReadOnly, IsAuthenticated]
    queryset = Post.objects.all()
    serializer_class = PostsSerializer
