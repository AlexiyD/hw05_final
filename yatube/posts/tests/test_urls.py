from django.test import TestCase, Client
from posts.models import Group, Post, User
from http import HTTPStatus


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(title='Тестовый заголовок',
                                         description='Тестовое описание',
                                         slug='test-slug',
                                         )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            pk=2,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_authorized_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/test_user/',
            'posts/post_detail.html': '/posts/2/',
            'posts/post_create.html': '/posts/2/edit/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_urls_guest_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test-slug/',
            'posts/profile.html': '/profile/test_user/',
            'posts/post_detail.html': '/posts/2/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_create_url_template(self):
        response = self.authorized_client.get('/create/')
        self.assertTemplateUsed(response, 'posts/post_create.html')

    def test_index(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_adout(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech(self):
        response = self.authorized_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_list(self):
        response = self.authorized_client.get('/group/test-slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_user(self):
        response = self.guest_client.get('/profile/test_user/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit(self):
        response = self.authorized_client.get('/posts/2/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
