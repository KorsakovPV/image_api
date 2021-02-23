import base64
import json

from django.test import Client, TestCase
from django.urls import reverse, path, include
import factory
from rest_framework import status
from rest_framework.authtoken.models import Token

from image_api.settings import BASE_DIR
from users.models import User
from content.models import Post, Image
from rest_framework.test import APIRequestFactory, APIClient, APITestCase, \
    URLPatternsTestCase


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
        self.path_img = f'{BASE_DIR}/api/tests/test_data/'

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

    # TODO Доделать тест. Тест не сохраняет картинку.
    def test_post_image(self):
        url = reverse('posts-list')
        image = f'{self.path_img}test_image_2.jpg'
        with open(image, 'rb') as img:
            image_bytes = img.read()
        im_b64 = base64.b64encode(image_bytes).decode("utf8")
        headers = {
            'Content-type': 'multipart/form-data; boundary=<calculated when request is sent>',
            'Accept': '*/*'}
        data = {
            'text': 'test post',
            'post_images': [im_b64],
        }
        response = self.client_authentication.post(url, data=data,
                                                   headers=headers,
                                                   format='json')
