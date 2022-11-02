from django import forms
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post, User, Comment, Follow

amount_posts: int = 10
test_amposts: int = 20


class PostsViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',)
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст',
            group=cls.group)

    @classmethod
    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts',
                kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'test_user'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': 1}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': 1}
            ): 'posts/post_create.html',
            reverse('posts:post_create'): 'posts/post_create.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_guest_client_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts',
                kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'test_user'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': 1}
            ): 'posts/post_detail.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_create_post(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': 1}
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.text, 'Текст')

    def test_group_page_show_correct(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:group_posts',
            kwargs={'slug': 'test-slug'}
        ))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.text, 'Текст')
        self.assertEqual(
            response.context['group'],
            Group.objects.get(title='Тестовая группа')
        )

    def test_profile_page_show_correc(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': 'test_user'}
        ))
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author, self.user)
        self.assertEqual(first_object.text, 'Текст')
        self.assertEqual(response.context['profile'], self.user)

    def test_detail_page_show_correct(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': 1}
        ))
        self.assertEqual(response.context['post'].text, 'Текст')

    def test_unfollowing_posts(self):
        """Тестирование отсутствия поста автора у нового пользователя."""
        new_user = User.objects.create(username='test_user1')
        authorized_client = Client()
        authorized_client.force_login(new_user)
        response_unfollow = authorized_client.get(
            reverse('posts:follow_index'))
        context_unfollow = response_unfollow.context
        self.assertEqual(len(context_unfollow['page_obj']), 0)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',)
        Post.objects.bulk_create(
            Post(author=cls.user,
                 group=Group.objects.get(title='Тестовая группа'),
                 text='Текст1') for _ in range(test_amposts))

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='test_user')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_contain_required_records(self):
        pages_names = [
            reverse('posts:index'),
            reverse('posts:group_posts',
                    kwargs={'slug': 'test-slug'}),
            reverse(
                'posts:profile',
                kwargs={'username': 'test_user'}
            )
        ]
        for reverse_name in pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 amount_posts)
                response = self.guest_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']),
                                 amount_posts)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testcomment')
        cls.group = Group.objects.create(
            title='test-group3',
            slug='test-slug3',
            description='description3'
        )
        cls.post = Post.objects.create(
            text='test-text3',
            author=cls.user,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='test-comment',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_add_comment(self):
        """Валидная форма создает комментарий."""
        form_data = {
            'text': 'Текст комментария',
            'post': self.post,
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertTrue(
            Comment.objects.filter(
                text='Текст комментария',
                post=self.post
            ).exists()
        )


class Testfollow(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testfollow', password='pass'
        )
        self.user.save()
        self.client.login(username='testfollow', password='pass')
        self.text = "test text  "

    def response_get(self, name, rev_args=None, followed=True):
        return self.client.get(
            reverse(
                name,
                kwargs=rev_args
            ),
            follow=followed
        )

    def response_post(self, name, post_args=None, rev_args=None, fol=True):
        return self.client.post(
            reverse(
                name,
                kwargs=rev_args
            ),
            data=post_args,
            follow=fol)

    def test_auth_follow_add(self):
        """ Авторизованный пользователь подписывается на других.
        """
        following = User.objects.create(username='following')
        self.response_post(
            'posts:profile_follow',
            rev_args={'username': following})
        self.assertIs(
            Follow.objects.filter(user=self.user, author=following).exists(),
            True)

    def test_auth_follow_dell(self):
        """ Авторизованный пользователь удаляет из подписок.
        """
        following = User.objects.create(username='following')
        self.response_post(
            'posts:profile_unfollow',
            rev_args={'username': following})
        self.assertIs(
            Follow.objects.filter(user=self.user, author=following).exists(),
            False)

    def test_new_post(self):
        """ Новая запись появляется в ленте тех, кто подписан.
        """
        following = User.objects.create(username='following1')
        Follow.objects.create(user=self.user, author=following)
        post = Post.objects.create(author=following, text=self.text)
        response = self.response_get('posts:follow_index')
        self.assertIn(post, response.context['page_obj'].object_list)

    def test_new_post_invisible(self):
        """ Новая запись не появляется в ленте, кто не подписан.
        """
        following = User.objects.create(username='following1')
        post = Post.objects.create(author=following, text=self.text)
        self.client.logout()
        User.objects.create_user(
            username='testfollow1',
            password='pass')
        self.client.login(username='testfollow1', password='pass')
        response = self.response_get('posts:follow_index')
        self.assertNotIn(post, response.context['page_obj'].object_list)
