import os
from io import BytesIO

from django.core.files import File
from django.test import Client, TestCase
from django.urls import reverse

import factory
import PIL
from content.models import Image, Post
from image_api.settings import BASE_DIR, MEDIA_URL
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APIRequestFactory, APITestCase
from users.models import User


class UserFactory(factory.Factory):
    """
    Класс Factory.

    Класс для создания пользователей через библиотеку Factory Boy.
    """

    class Meta:
        """Модель экземпляры которой создаем."""

        model = User

    username = 'Test_user'
    email = 'test@test.test'
    password = '12345six'
    first_name = 'Test user first_name'


def _create_user(**kwargs):
    """Создаем пользователя."""
    user = UserFactory.create(**kwargs)
    user.save()
    return user


class URLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = _create_user()

    def test_redoc_page(self):
        url_redoc = reverse('redoc')
        response = self.guest_client.get(url_redoc)
        self.assertEqual(response.status_code, 200,
                         msg='Cтраница {} должна быть доступна.'.format(
                             url_redoc))


class PostTests(APITestCase):

    def setUp(self):
        self.client_authentication = APIClient()
        self.client_no_authentication = APIClient()
        self.user = _create_user()
        self.token = Token.objects.create(user=self.user).key
        self.client_authentication.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token)

    def test_post_create(self):
        url = reverse('posts-list')
        data = {
            'text': 'test post',
        }
        response = self.client_authentication.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post = Post.objects.last()
        self.assertEqual(post.text, 'test post')

    def test_posts_list(self):
        url = reverse('posts-list')
        response = self.client_no_authentication.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client_authentication.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_posts_retrieve(self):
        post = Post.objects.get_or_create(author=self.user, text='test post')[
            0]
        url = reverse('posts-detail', kwargs={'pk': post.id})
        response = self.client_no_authentication.get(url, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)
        response = self.client_authentication.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('text'), post.text)
        self.assertEqual(response.data.get('author'), post.author.username)

    def test_post_update(self):
        post = Post.objects.get_or_create(author=self.user, text='test post')[
            0]
        url = reverse('posts-detail', kwargs={'pk': post.id})
        response = self.client_no_authentication.put(url, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)
        data = {'text': 'test post put', }
        response = self.client_authentication.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('text'), data.get('text'))

    def test_post_partial_update(self):
        post = Post.objects.get_or_create(author=self.user, text='test post')[
            0]
        url = reverse('posts-detail', kwargs={'pk': post.id})
        response = self.client_no_authentication.patch(url, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)
        data = {'text': 'test post put', }
        response = self.client_authentication.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('text'), data.get('text'))

    def test_post_partial_destroy(self):
        post = Post.objects.get_or_create(author=self.user, text='test post')[
            0]
        url = reverse('posts-detail', kwargs={'pk': post.id})
        response = self.client_no_authentication.delete(url, format='json')
        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)
        response = self.client_authentication.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ImageTests(APITestCase):
    @staticmethod
    def get_image_file(name, ext='png', size=(50, 50), color=(256, 0, 0)):
        file_obj = BytesIO()
        image = PIL.Image.new("RGBA", size=size, color=color)
        image.save(file_obj, ext)
        file_obj.seek(0)
        return File(file_obj, name=name)

    def setUp(self):
        self.client_authentication = APIClient()
        self.user = _create_user()
        self.token = Token.objects.create(user=self.user).key
        self.client_authentication.credentials(
            HTTP_AUTHORIZATION='Token ' + self.token)
        self.path_img = f'{BASE_DIR}{MEDIA_URL}posts/'
        self.img_name = {'1': 'test_image_test_post_image1.png',
                         '2': 'test_image_test_post_image2.png'}

    def test_post_image(self):
        url = reverse('posts-list')
        image1 = self.get_image_file(self.img_name.get('1'))
        data = {'text': 'test post',
                'post_images': [image1], }
        response = self.client_authentication.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Image.objects.all().count(), 1)

    def test_post_images(self):
        url = reverse('posts-list')
        image1 = self.get_image_file(self.img_name.get('1'))
        image2 = self.get_image_file(self.img_name.get('2'))
        data = {'text': 'test post',
                'post_images': [image1, image2], }
        response = self.client_authentication.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Image.objects.all().count(), 2)

    def test_post_invalid_image(self):
        url = reverse('posts-list')
        image1 = self.get_image_file(self.img_name, size=(10000, 5000))
        data = {'text': 'test post',
                'post_images': [image1], }
        response = self.client_authentication.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Image.objects.all().count(), 0)

    def tearDown(self):
        for i in self.img_name.keys():
            if os.path.isfile(f'{self.path_img}{self.img_name.get(i)}'):
                os.remove(f'{self.path_img}{self.img_name.get(i)}')
