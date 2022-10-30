from django.test import TestCase
from ..models import Group, Post, User

length: int = 15


class TaskModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост))))))))))))))))',
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(str(self.post), self.post.text[:length])

    def test_models_have_correct_object_names_group(self):
        self.assertEqual(str(self.group), self.group.title)
