from django.test import Client, TestCase
from django.urls import reverse
import factory
from users.models import User
from content.models import Post, Image
from rest_framework.test import APIRequestFactory, APIClient


class UserFactory(factory.Factory):
    """
    Класс Factory.

    Класс для создания пользователей через библиотеку Factory Boy.
    """

    class Meta:
        """Модель экземпляры которой создаем."""

        model = User

    username = 'Test user'
    email = 'test@test.test'
    password = '12345six'
    first_name = 'Test user first_name'


def _create_user(**kwargs):
    """Создаем пользователя."""
    user = UserFactory.create(**kwargs)
    user.save()
    return user


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.factory = APIRequestFactory()
        self.client = APIClient()
        self.user = _create_user()
        # self.authorized_client = Client()

    # redoc
    # createAuthToken post
    # posts-list get
    # post-create post
    # post-retrieve get
    # post-update put
    # post-destroy del
    # post-partialUpdate patch

    # Отправляем запрос через client,
    # созданный в setUp()
    # url_names = {'redoc': '',
    #              'get_token': '',
    #              }

    def test_redoc_page(self):
        url_redoc = reverse('redoc')
        response = self.guest_client.get(url_redoc)
        self.assertEqual(response.status_code, 200,
                         msg='Cтраница {} должна быть доступна.'.format(
                             url_redoc))


    # TODO переделать тест аутентификации
    def test_authtoken_url(self):
        url_authtoken = reverse('get_token')
        response = self.guest_client.post(url_authtoken)
        self.assertEqual(response.status_code, 400,
                         msg='Ресурс {} без переданных обязательных полей '
                             'должен выдавать ошибку 400.'.format(
                             url_authtoken))
        response = self.client.post(url_authtoken,
                                          {
                                              "username": self.user.username,
                                              "password": self.user.password
                                          },
                                          format='json')
        response2 = self.factory.post(url_authtoken,
                                          {
                                              "username": self.user.username,
                                              "password": self.user.password
                                          },
                                          format='json')

        print(10)
