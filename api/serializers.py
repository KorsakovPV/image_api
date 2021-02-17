from rest_framework import serializers

from content.models import Post


class PostsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    class Meta:
        fields = '__all__'
        model = Post
        read_only_fields = ['pub_date']
