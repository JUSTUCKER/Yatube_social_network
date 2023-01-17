from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Comment, Follow, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Создание пользователя
        cls.user = User.objects.create_user(username='auth')
        # Создание группы
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        # Создание поста
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост' * settings.SYMBOL_MULTIPLIER,
        )

    def test_model_post_have_correct_object_name(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        text = post.text[:15]
        self.assertEqual(str(post), text)

    def test_model_post_verbose_name(self):
        """verbose_name в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'created': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_model_post_help_text(self):
        """help_text в полях модели Post совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_model_group_have_correct_object_name(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = GroupModelTest.group
        title = group.title
        self.assertEqual(str(group), title)

    def test_model_group_verbose_name(self):
        """verbose_name в полях модели Group совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название',
            'slug': 'Ссылка',
            'description': 'Описание',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Создание пользователя
        cls.user = User.objects.create_user(username='auth')
        # Создание поста
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        # Создание комментария
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Комментарий' * settings.SYMBOL_MULTIPLIER,
            post=cls.post,
        )

    def test_model_comment_have_correct_object_name(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        comment = CommentModelTest.comment
        text = comment.text[:15]
        self.assertEqual(str(comment), text)

    def test_model_comment_verbose_name(self):
        """verbose_name в полях модели Comment совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_verboses = {
            'post': 'Название поста',
            'author': 'Имя автора',
            'text': 'Текст комментария',
            'created': 'Дата публикации',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Создание автора
        cls.author_user = User.objects.create_user(username='author')
        # Создание подписчика
        cls.follower_user = User.objects.create_user(username='follower')
        # Создание подписки
        cls.follow = Follow.objects.create(
            user=cls.follower_user,
            author=cls.author_user,
        )

    def test_model_follow_have_correct_object_name(self):
        """Проверяем, что у модели Follow корректно работает __str__."""
        follow = FollowModelTest.follow
        text = (
            f'{self.follow.user.username} '
            f'следит за {self.follow.author.username}'
        )
        self.assertEqual(str(follow), text)

    def test_model_follow_verbose_name(self):
        """verbose_name в полях модели Follow совпадает с ожидаемым."""
        follow = FollowModelTest.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор поста',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    follow._meta.get_field(value).verbose_name, expected)
