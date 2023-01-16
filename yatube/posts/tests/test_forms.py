import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Создание пользователя
        cls.user = User.objects.create_user(username='auth')
        # Создание группы
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        # Создание поста
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=self.small_gif,
            content_type='image/gif'
        )
        self.form_data = {
            'text': 'Новый текст поста',
            'group': PostCreateFormTests.group.id,
            'image': self.uploaded,
        }
        self.comment_form_data = {
            'author': PostCreateFormTests.user,
            'post': PostCreateFormTests.post,
            'text': 'Новый комментарий',
        }
        # Создание гостевого клиента в БД
        self.guest_client = Client()
        # Создание авторизированного клиента в БД
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает пост с изображением."""
        # Подсчитаем количество постов в Post
        posts_count = Post.objects.count()
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': PostCreateFormTests.user}
        ))
        # Проверяем, увеличилось ли количество постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создался новый пост со следующим по счету id
        self.assertTrue(
            Post.objects.filter(
                author=PostCreateFormTests.user,
                text=self.form_data['text'],
                group=PostCreateFormTests.group,
                id=PostCreateFormTests.post.id + 1,
                image=f'posts/{self.uploaded}'
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма редактирует пост."""
        # Подсчитаем актуальное количество постов в Post
        posts_count = Post.objects.count()
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostCreateFormTests.post.id}
            ),
            data=self.form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': PostCreateFormTests.post.id}
        ))
        # Проверяем, не изменилось ли количество постов
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что изменения в посте вступили в силу
        self.assertTrue(
            Post.objects.filter(
                author=PostCreateFormTests.user,
                text=self.form_data['text'],
                group=PostCreateFormTests.group,
                id=PostCreateFormTests.post.id,
            ).exists()
        )

    def test_guest_create_post(self):
        """Невалидная форма не создает пост."""
        # Подсчитаем количество постов в Post
        posts_count = Post.objects.count()
        # Отправляем POST-запрос
        self.guest_client.post(
            reverse('posts:post_create'),
            data=self.form_data,
        )
        # Проверяем, не изменилось ли количество постов
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что новый пост с заданными данными не создался
        self.assertFalse(
            Post.objects.filter(
                text=self.form_data['text'],
                group=PostCreateFormTests.group,
            ).exists()
        )

    def test_authorized_user_comment(self):
        """Авторизированный пользователь может комментировать пост и
            после успешной отправки комментарий появляется на странице поста.
        """
        # Подсчитаем количество комментириев
        comments_count = Comment.objects.count()
        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostCreateFormTests.post.id}
            ),
            data=self.comment_form_data,
            follow=True,
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': PostCreateFormTests.post.id})
        )
        # Проверяем, увеличилось ли количество комментариев
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        # Проверяем, что новый комментарий находится в указанном посте
        self.assertTrue(
            Comment.objects.filter(
                author=PostCreateFormTests.user,
                post=PostCreateFormTests.post,
                text=self.comment_form_data['text'],
            ).exists()
        )

    def test_guest_user_comment(self):
        """Гость не может комментировать посты."""
        # Подсчитаем количество комментириев
        comments_count = Comment.objects.count()
        # Отправляем POST-запрос
        self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': PostCreateFormTests.post.id}
            ),
            data=self.comment_form_data,
            follow=True,
        )
        # Проверяем, не изменилось ли количество комментариев
        self.assertEqual(Comment.objects.count(), comments_count)
        # Проверяем, что новый комментарий не создался
        self.assertFalse(
            Comment.objects.filter(
                text=self.comment_form_data['text'],
            ).exists()
        )
