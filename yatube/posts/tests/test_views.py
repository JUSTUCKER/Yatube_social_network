import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Follow, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTest(TestCase):
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
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        # Создание поста
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создание авторизированного клиента в БД
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def post_fields_check(self, post):
        """Метод, проверяющий содержимое поста."""
        with self.subTest(post=post):
            self.assertEqual(post.author, PostPagesTest.post.author)
            self.assertEqual(post.text, PostPagesTest.post.text)
            self.assertEqual(post.group, PostPagesTest.post.group)
            self.assertEqual(post.image, f'posts/{self.uploaded}')

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': PostPagesTest.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={
                    'username': PostPagesTest.user.username
                }
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': PostPagesTest.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': PostPagesTest.post.id}
            ): 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        self.post_fields_check(response.context['page_obj'][0])

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': PostPagesTest.group.slug}
            )
        )
        self.assertIn('page_obj', response.context)
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        self.post_fields_check(response.context['page_obj'][0])
        self.assertIn('group', response.context)
        # Проверяем, что содержимое контекста 'group' совпадает с ожидаемым
        self.assertEqual(
            response.context.get('group').title, PostPagesTest.group.title
        )
        self.assertEqual(
            response.context.get('group').slug, PostPagesTest.group.slug
        )
        self.assertEqual(
            response.context.get('group').description,
            PostPagesTest.group.description
        )

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile', kwargs={
                    'username': PostPagesTest.user.username
                }
            )
        )
        self.assertIn('page_obj', response.context)
        # Взяли первый элемент из списка и проверили, что его содержание
        # совпадает с ожидаемым
        self.post_fields_check(response.context['page_obj'][0])
        self.assertIn('author', response.context)
        # Проверяем, что содержимое контекста 'author' совпадает с ожидаемым
        self.assertEqual(
            response.context.get('author'),
            PostPagesTest.user
        )

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail', kwargs={'post_id': PostPagesTest.post.id}
            )
        )
        self.assertIn('post', response.context)
        self.post_fields_check(response.context.get('post'))

    def test_post_create_and_edit_show_correct_context(self):
        """Шаблоны post_create и post_edit сформированы
            с правильным контекстом."""
        urls = (
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={
                'post_id': PostPagesTest.post.id
            })
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                for value, expected in form_fields.items():
                    form_field = (
                        response.context.get('form').fields.get(value)
                    )
                    self.assertIsInstance(form_field, expected)

    def test_post_in_index_group_profile_pages(self):
        """При указании группы, пост появляется на главной,
            в выбранноой группе и в профиле автора."""
        urls = (
            reverse('posts:index'),
            reverse(
                'posts:group_list', kwargs={'slug': PostPagesTest.group.slug}
            ),
            reverse(
                'posts:profile', kwargs={
                    'username': PostPagesTest.user.username
                }
            )
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                page_object = response.context['page_obj']
                self.assertIn(PostPagesTest.post, page_object)

    def test_post_not_in_another_group(self):
        """Не попал ли пост в группу, для которой не был предназначен."""
        new_post = Post.objects.create(
            author=PostPagesTest.user,
            text='Новый тестовый пост',
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': PostPagesTest.group.slug}
        ))
        page_object = response.context['page_obj']
        self.assertNotIn(new_post, page_object)

    def test_index_cache(self):
        """Проверка кеша главной страницы."""
        # Запрос к главной странице с существующим постом
        response = self.authorized_client.get(reverse('posts:index'))
        # Удаление существующего поста
        Post.objects.filter(id=PostPagesTest.post.id).delete()
        # Запрос к главной странице после удаления поста
        response_after_delete = self.authorized_client.get(
            reverse('posts:index')
        )
        # Проверка: контекст страницы должен остаться закеширован
        self.assertEqual(response.content, response_after_delete.content)
        # Принудительная отчистка кеша
        cache.clear()
        # Запрос к главной странице после чистки кеша
        response_new_cache = self.authorized_client.get(
            reverse('posts:index')
        )
        # Проверка: контекст страницы должен обновиться
        self.assertNotEqual(response.content, response_new_cache.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Создание пользователя в БД
        cls.user = User.objects.create_user(username='auth')
        # Создание группы в БД
        cls.group = Group.objects.create(
            title='Прикольная группа',
            slug='group_slug',
            description='Тестовое описание группы',
        )
        # Создание 13 постов группе БД
        Post.objects.bulk_create([Post(
            author=cls.user,
            text=f'Текст поста номер {count}',
            group=cls.group,
        ) for count in range(13)])

    def setUp(self):
        # Создание гостевого клиента в БД
        self.guest_client = Client()

    def test_pages_contains_ten_records(self):
        """Проверка работы пагинатора."""
        urls = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={
                'slug': PaginatorViewsTest.group.slug
            }),
            reverse('posts:profile', kwargs={
                'username': PaginatorViewsTest.user.username
            }),
        )
        pages_and_posts_count = {
            '': settings.AMOUNT_POSTS,
            '?page=2': 3,
        }
        for url in urls:
            for num_page, posts_count in pages_and_posts_count.items():
                with self.subTest(url=url):
                    response = self.guest_client.get(url + num_page)
                    self.assertEqual(
                        len(response.context['page_obj']), posts_count
                    )


class FollowViewsTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # Создание автора в БД
        cls.user_author = User.objects.create_user(username='author')
        # Создание пользователя в БД
        cls.user = User.objects.create_user(username='follower')
        # Создание поста
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
        )

    def setUp(self):
        # Создание клиента автора в БД
        self.author_client = Client()
        self.author_client.force_login(self.user_author)
        # Создание клиента подписчика в БД
        self.user_client = Client()
        self.user_client.force_login(self.user)

    def test_follow_and_unfollow(self):
        """Авторизованный пользователь может подписываться на других
            пользователей и удалять их из подписок."""
        # Проверка работы подписки
        zero_follows_count = Follow.objects.count()
        self.user_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.user_author}
            )
        )
        self.assertEqual(Follow.objects.count(), zero_follows_count + 1)
        # Проверка работы отписки
        self.user_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_author}
        ))
        self.assertEqual(Follow.objects.count(), zero_follows_count)

    def test_follower_view_post(self):
        """Новая запись пользователя появляется в ленте тех,
            кто на него подписан."""
        # Подписка на автора
        self.user_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_author})
        )
        # Создание нового поста
        new_post = Post.objects.create(
            author=FollowViewsTests.user_author,
            text='Тестовый пост',
        )
        # Проверка, появился ли новый пост в ленте подписчика
        response = self.user_client.get(
            reverse('posts:follow_index')
        )
        page_object = response.context['page_obj']
        self.assertIn(new_post, page_object)

    def test_unfollower_dont_view_post(self):
        """Новая запись пользователя не появляется в ленте тех,
            кто на него не подписан."""
        # Создание нового поста
        new_post = Post.objects.create(
            author=FollowViewsTests.user_author,
            text='Тестовый пост',
        )
        # Проверка, появился ли новый пост в ленте не подписчика
        response = self.user_client.get(
            reverse('posts:follow_index')
        )
        page_object = response.context['page_obj']
        self.assertNotIn(new_post, page_object)
