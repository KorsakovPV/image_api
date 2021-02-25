import base64
from io import BytesIO

from django.test import Client, TestCase
from django.urls import reverse
import factory
from rest_framework import status
from rest_framework.authtoken.models import Token

from image_api.settings import BASE_DIR
from users.models import User
from content.models import Post, Image
from rest_framework.test import APIRequestFactory, APIClient, APITestCase

from django.core.files import File
import PIL


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
        self.path_img = f'{BASE_DIR}/api/tests/test_data/'

    def test_post_image(self):
        url = reverse('posts-list')
        image = f'{self.path_img}test_image_2.jpg'
        with open(image, 'rb') as img:
            # image_bytes = img.read()
            # im_b64 = base64.b64encode(image_bytes).decode("utf8")
            # headers = {
            #     'Content-type': 'multipart/form-data; boundary=<calculated when '
            #                     'request is sent>',
            #     'Accept': '*/*',
            #     'Accept-Encoding': 'gzip, deflate, br'
            # }
            data = {
                'text': 'test post',
                'post_images': img,
            }
            response = self.client_authentication.post(url, data=data,
                                                       # headers=headers,
                                                       # format='json'
                                                       )
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Image.objects.all().count(), 1)

    def test_post_not_image(self):
        url = reverse('posts-list')
        image = f'{self.path_img}test_image_4_invalide.txt'
        with open(image, 'rb') as img:
            data = {
                'text': 'test post',
                'post_images': img,
            }
            response = self.client_authentication.post(url, data=data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            # TODO грузит неизображение как изображение
            self.assertEqual(Image.objects.all().count(), 1)


    def test_post_invalid_image(self):
        url = reverse('posts-list')
        image = f'{self.path_img}test_image_1_6mb.jpeg'
        with open(image, 'rb') as img:
            data = {
                'text': 'test post',
                'post_images': img,
            }
            response = self.client_authentication.post(url, data=data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            # TODO грузит не валидное изображение
            self.assertEqual(Image.objects.all().count(), 1)


    def test_post_image_pil(self):
        url = reverse('posts-list')
        image1 = self.get_image_file('image.png')
        image2 = self.get_image_file('image2.png')
        headers = {
            'Content-type': 'multipart/form-data; boundary=<calculated when '
                            'request is sent>',
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br'
        }
        data = {
            'text': 'test post',
            'post_images': image1,
            #     'image2.png': image2,
            # },
        }
        response = self.client_authentication.post(url,
                                                   data=data,
                                                   headers=headers,
                                                   # format='json'
                                                   )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # TODO Доделать тест. Тест не сохраняет картинку.
        self.assertEqual(Image.objects.all().count(), 1)
