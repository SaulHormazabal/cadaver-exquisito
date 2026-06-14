import re

from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

# Formato del código de allauth, p. ej. "SVNM-QLJH".
CODE_RE = re.compile(r'[A-Z0-9]{4}-[A-Z0-9]{4}')


def extract_code(message):
    return CODE_RE.search(message.body).group(0)


class LoginCreatesAccountTests(TestCase):
    """Login unificado: un email sin cuenta se registra al pedir el código."""

    def test_unknown_email_creates_account_and_authenticates(self):
        response = self.client.post(
            reverse('account_login'), {'email': 'nuevo@example.com'}
        )
        self.assertRedirects(response, reverse('account_confirm_login_code'))

        user = User.objects.get(email='nuevo@example.com')
        self.assertEqual(len(mail.outbox), 1)
        code = extract_code(mail.outbox[0])

        confirm = self.client.post(
            reverse('account_confirm_login_code'), {'code': code}
        )
        self.assertRedirects(confirm, reverse('corpse:list'))
        self.assertEqual(self.client.session['_auth_user_id'], str(user.pk))
        # El login por código deja el email verificado.
        self.assertTrue(EmailAddress.objects.get(user=user).verified)

    def test_wrong_code_does_not_authenticate(self):
        self.client.post(reverse('account_login'), {'email': 'nuevo@example.com'})
        self.client.post(
            reverse('account_confirm_login_code'), {'code': 'XXXX-XXXX'}
        )
        self.assertNotIn('_auth_user_id', self.client.session)


class LoginExistingUserTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='ada@example.com')
        EmailAddress.objects.create(
            user=self.user, email=self.user.email, verified=True, primary=True
        )

    def test_existing_user_logs_in_without_creating_duplicate(self):
        response = self.client.post(
            reverse('account_login'), {'email': 'ada@example.com'}
        )
        self.assertRedirects(response, reverse('account_confirm_login_code'))
        code = extract_code(mail.outbox[0])

        confirm = self.client.post(
            reverse('account_confirm_login_code'), {'code': code}
        )
        self.assertRedirects(confirm, reverse('corpse:list'))
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.pk))
        self.assertEqual(User.objects.filter(email='ada@example.com').count(), 1)


class AuthEntrypointsTests(TestCase):
    def test_login_page_renders(self):
        response = self.client.get(reverse('account_login'))
        self.assertEqual(response.status_code, 200)

    def test_signup_redirects_to_login(self):
        # No hay registro separado: signup redirige al login unificado.
        response = self.client.get(reverse('account_signup'))
        self.assertRedirects(response, reverse('account_login'))
