import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Post, Group, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
TEST_IMAGE = SimpleUploadedFile(
    name='img.jpg',
    content=(
        b'\x47\x49\x46\x38\x39\x61\x02\x00'
        b'\x01\x00\x80\x00\x00\x00\x00\x00'
        b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
        b'\x00\x00\x00\x2C\x00\x00\x00\x00'
        b'\x02\x00\x01\x00\x00\x02\x02\x0C'
        b'\x0A\x00\x3B'
    ),
    content_type='image/jpeg'
)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user('author')
        cls.post = Post.objects.create(
            text='test text',
            author=cls.author,
        )
        cls.group = Group.objects.create(
            title='test group',
            slug='test-slug',
            description='text'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_form_post_create(self):
        """создается новый пост"""
        posts_id = list(Post.objects.values_list('id', flat=True))
        posts_count = len(posts_id)
        form_data = {
            'text': 'create post',
            'group': self.group.id,
            'author': self.author.id,
            'image': TEST_IMAGE,
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        last_post = Post.objects.exclude(id__in=posts_id)
        self.assertEqual(last_post.count(), 1)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.author}))
        self.assertTrue(
            Post.objects.filter(
                text=form_data.get('text'),
                group=form_data.get('group'),
                author=form_data.get('author'),
                image='posts/img.jpg'
            ).exists()
        )

    def test_form_post_edit(self):
        """редактируется существующий пост"""
        post_count = Post.objects.count()
        form_data = {
            'text': 'post edit',
            'group': self.group.id,
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        edited_post = Post.objects.get(id=self.post.id)
        values = {
            edited_post.text: form_data.get('text'),
            edited_post.group: self.group,
            edited_post.author: self.author,
        }
        for field, expected_value in values.items():
            with self.subTest(field=field):
                self.assertEqual(field, expected_value)
        self.assertEqual(Post.objects.count(), post_count)
        self.assertRedirects(response, reverse(
            'posts:post_details', kwargs={'post_id': self.post.id}))

    def test_add_comment(self):
        """добавляется комментарий к посту"""
        comments_count = Comment.objects.filter(post=self.post).count()
        form_data = {'text': 'test comment'}
        response = self.author_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.filter(post=self.post).count(),
                         comments_count + 1)
        self.assertRedirects(response, reverse(
            'posts:post_details', kwargs={'post_id': self.post.id}))
