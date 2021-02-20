from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta

from content.models import Post, Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['image']
        model = Image


class PostsSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(read_only=True,
                                          slug_field='username')
    post_images = ImageSerializer(read_only=True, many=True)

    class Meta:
        fields = ['id', 'text', 'pub_date', 'author', 'post_images']
        model = Post
        read_only_fields = ['pub_date']

    def create(self, validated_data):
        post = Post.objects.create(**validated_data)
        files = self.context['request'].FILES.getlist('post_images')
        for file in files:
            Image.objects.create(post=post, image=file)
        return post

    def update(self, instance, validated_data):
        Image.objects.filter(post=instance).delete()
        files = self.context['request'].FILES.getlist('post_images')
        for file in files:
            Image.objects.create(post=instance, image=file)
        raise_errors_on_nested_writes('update', self, validated_data)
        info = model_meta.get_field_info(instance)
        m2m_fields = []
        for attr, value in validated_data.items():
            if attr in info.relations and info.relations[attr].to_many:
                m2m_fields.append((attr, value))
            else:
                setattr(instance, attr, value)
        instance.save()
        for attr, value in m2m_fields:
            field = getattr(instance, attr)
            field.set(value)
        return instance

    def validate(self, data):
        files = self.context['request'].FILES.getlist('post_images')
        for file in files:
            if file.size > 200 * 1024:
                raise ValidationError(
                    "Image file '{}' too large ( > 200kb )".format(file.name))
        return data
