from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.http import urlencode

from posts.models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.second_user = User.objects.create_user(username='non_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.non_author_client = Client()
        self.non_author_client.force_login(self.second_user)

    def test_public_pages(self):
        """Страницы доступные любому пользователю,
            в том числе несуществующая страница."""
        field_verboses = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse(
                'posts:group_list', kwargs={'slug': PostURLTest.group.slug}
            ): HTTPStatus.OK,
            reverse(
                'posts:profile', kwargs={
                    'username': PostURLTest.user.username
                }
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail', kwargs={'post_id': PostURLTest.post.id}
            ): HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                response = self.guest_client.get(value)
                self.assertEqual(response.status_code, expected)

    def test_only_authorized_pages(self):
        """Страницы доступные авторизованному пользователю или автору."""
        field_verboses = {
            reverse('posts:post_create'): HTTPStatus.OK,
            reverse(
                'posts:post_edit', kwargs={'post_id': PostURLTest.post.id}
            ): HTTPStatus.OK,
            reverse('posts:follow_index'): HTTPStatus.OK,
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertEqual(response.status_code, expected)

    def test_urls_redirect_for_anonymous_users(self):
        """Страницы перенаправляющие анонимного пользователя."""
        field_verboses = {
            reverse('posts:post_create'): '%s?%s' % (
                reverse('users:login'),
                urlencode({"next": reverse('posts:post_create')})
            ),
            reverse('posts:follow_index'): '%s?%s' % (
                reverse('users:login'),
                urlencode({"next": reverse('posts:follow_index')})
            ),
            reverse(
                'posts:post_edit', kwargs={'post_id': PostURLTest.post.id}
            ): '%s?%s' % (
                reverse('users:login'),
                urlencode({"next": reverse(
                    'posts:post_edit', kwargs={'post_id': PostURLTest.post.id}
                )})
            ),
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                response = self.guest_client.get(value, follow=True)
                self.assertRedirects(response, expected)

    def test_url_redirect_for_non_author(self):
        """Страница редактирования поста перенаправляющая не автора поста."""
        response = self.non_author_client.get(reverse(
            'posts:post_edit', kwargs={'post_id': PostURLTest.post.id}
        ), follow=True)
        expected = reverse(
            'posts:post_detail', kwargs={'post_id': PostURLTest.post.id})
        self.assertRedirects(response, expected)

    def test_public_urls_uses_correct_template(self):
        """Публичные URL-адреса используют соответствующие шаблоны."""
        field_verboses = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': PostURLTest.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={
                    'username': PostURLTest.user.username
                }
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': PostURLTest.post.id}
            ): 'posts/post_detail.html',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertTemplateUsed(response, expected)

    def test_auth_urls_uses_correct_template(self):
        """URL-адреса доступные авторизированным пользователям
            используют соответствующие шаблоны."""
        field_verboses = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': PostURLTest.post.id}
            ): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertTemplateUsed(response, expected)
