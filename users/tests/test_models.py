from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    def test_custom_user_model_is_active(self):
        self.assertEqual(User.__name__, 'User')
        self.assertEqual(User._meta.app_label, 'users')

    def test_create_user(self):
        user = User.objects.create_user(username='ada', password='secret123')
        self.assertTrue(user.check_password('secret123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin = User.objects.create_superuser(
            username='root', password='secret123'
        )
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)

    def test_str_uses_display_name_when_present(self):
        user = User.objects.create_user(
            username='grace', password='secret123', display_name='Grace H.'
        )
        self.assertEqual(str(user), 'Grace H.')

    def test_str_falls_back_to_username(self):
        user = User.objects.create_user(username='solo', password='secret123')
        self.assertEqual(str(user), 'solo')
