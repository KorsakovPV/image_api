from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from content.models import Post


class PostsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')

    def validate(self, data):
        image = data.get('image')
        if image:
            if image.size > 200*1024:
                raise ValidationError("Image file too large ( > 200kb )")
        return data

    class Meta:
        fields = '__all__'
        model = Post
        read_only_fields = ['pub_date']
