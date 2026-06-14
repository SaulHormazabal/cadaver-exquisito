from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    def test_custom_user_model_is_active(self):
        self.assertEqual(User.__name__, 'User')
        self.assertEqual(User._meta.app_label, 'users')
        self.assertEqual(User.USERNAME_FIELD, 'email')

    def test_create_user_with_password(self):
        user = User.objects.create_user(
            email='ada@example.com', password='secret123'
        )
        self.assertEqual(user.email, 'ada@example.com')
        self.assertTrue(user.check_password('secret123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_without_password_is_unusable(self):
        # Usuarios passwordless (login por código): sin contraseña usable.
        user = User.objects.create_user(email='passwordless@example.com')
        self.assertFalse(user.has_usable_password())

    def test_create_user_requires_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='secret123')

    def test_email_is_normalized(self):
        user = User.objects.create_user(email='Grace@Example.COM')
        # normalize_email pasa el dominio a minúsculas.
        self.assertEqual(user.email, 'Grace@example.com')

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            email='root@example.com', password='secret123'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_str_uses_display_name_when_present(self):
        user = User.objects.create_user(
            email='grace@example.com', display_name='Grace H.'
        )
        self.assertEqual(str(user), 'Grace H.')

    def test_str_falls_back_to_email(self):
        user = User.objects.create_user(email='solo@example.com')
        self.assertEqual(str(user), 'solo@example.com')
