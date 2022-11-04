from django.test import TestCase
from ..models import Group, Post, User, Comment, Follow

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
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='тестовый комментарий))))))))))))))))',
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user,
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(str(self.post), self.post.text[:length])

    def test_models_have_correct_object_names_group(self):
        self.assertEqual(str(self.group), self.group.title)

    def test_models_correct_length_names_comment(self):
        self.assertEqual(str(self.comment), self.comment.text[:length])

    def test_models_have_correct_object_names_follow(self):
        self.assertEqual(str(self.follow), self.follow.user.username)
