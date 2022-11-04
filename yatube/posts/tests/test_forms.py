from django.test import Client, TestCase
from posts.models import User, Group, Post, Comment
from posts.forms import PostForm
from django.urls import reverse
from http import HTTPStatus


class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_client_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': 'test_user'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(
            text='текст',
            author=self.user,
            group=self.group,
        ).exists())

    def test_authorized_client_post_edit(self):
        form_data = {
            'text': 'текст новый',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.pk}))
        self.post.refresh_from_db()
        self.assertEqual(form_data['text'], 'текст новый')

    def test_guest_create_post(self):
        posts_count = Post.objects.count()
        form_data = {'text': 'Тестовый текст'}
        self.guest_client.post(reverse('posts:post_create'), data=form_data)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_guest_edit_post(self):
        posts_count = Post.objects.count()
        form_data = {'text': 'редактированый текст'}
        self.guest_client.post(reverse('posts:post_create'), data=form_data)
        edit_post = Post.objects.get(id=self.post.pk)
        self.assertEqual(edit_post, self.post)
        self.assertEqual(Post.objects.count(), posts_count)


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.form = PostForm()

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.user)

    def test_comment_form_create_database_entry(self):
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'test_comment',
        }
        kwargs = {"post_id": self.post.pk}
        response = self.authorized_user.post(
            reverse('posts:add_comment', kwargs=kwargs),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertRedirects(response, reverse('posts:post_detail',
                                               kwargs=kwargs))
        self.assertTrue(Comment.objects.filter(
            text='test_comment',
            author=self.user,
            post=self.post
        ))

    def test_comment_form_guest_not_create_database_entry(self):
        form_data = {
            'text': 'test_comment',
        }
        kwargs = {"post_id": self.post.pk}
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs=kwargs),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
