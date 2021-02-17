from django.db import models

from users.models import User


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts')
    image = models.ImageField(upload_to='posts/', null=True,
                              blank=True)  # поле для картинки

    def __str__(self):
        return self.text
