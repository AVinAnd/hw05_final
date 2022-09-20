from django.test import TestCase

from ..models import Post, Group, User, CHARS_IN_STR


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user('auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовые пост'
        )

    def test_model_have_correct_object_names(self):
        """Проверка работы __str__"""
        field_expected_names = {
            self.post.text[:CHARS_IN_STR]: str(self.post),
            self.group.title: str(self.group),
        }
        for field, expected_value in field_expected_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    field, expected_value)

    def test_models_verbose_name(self):
        """Проверка verbose_name"""
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата',
            'author': 'Автор',
            'group': 'Сообщество',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                model_field = self.post._meta.get_field(field)
                self.assertEqual(model_field.verbose_name, expected_value)

    def test_models_help_text(self):
        """Проверка help_text"""
        field_help_text = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)
