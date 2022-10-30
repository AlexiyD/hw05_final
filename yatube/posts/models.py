from enum import unique
from django.db import models
from django.contrib.auth.models import User

length: int = 15


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True, db_index=True,
                            verbose_name="URL", null=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста')
    pub_date = models.DateTimeField('дата публикации', auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='posts_author',
                               verbose_name='Автор'
                               )
    group = models.ForeignKey(Group, on_delete=models.SET_NULL,
                              related_name='posts_group',
                              blank=True, null=True,
                              verbose_name='Группа',
                              help_text='Выберите группу'
                              )
    image = models.ImageField(verbose_name='Изображение',
                              upload_to='posts/',
                              blank=True
                             )

    class Meta:
        ordering = ['-pub_date']
        

    def __str__(self):
        return self.text[:length]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name="comments")
    text = models.TextField(verbose_name='Комментарий')
    created = models.DateTimeField('дата публикации', auto_now_add=True)
    
    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, 
                             related_name='follower', 
                             verbose_name='подписчики'
                             )
    author = models.ForeignKey(User, on_delete=models.CASCADE, 
                               related_name='following', 
                               verbose_name='автор'
                               )
    

    class Meta:
        unique_together = [['user', 'author']]

    def __str__(self):
        return self.user.username