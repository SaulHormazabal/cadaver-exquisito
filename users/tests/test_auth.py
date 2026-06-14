import re

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse

User = get_user_model()

# Formato del código de allauth, p. ej. "SVNM-QLJH".
CODE_RE = re.compile(r'[A-Z0-9]{4}-[A-Z0-9]{4}')


def extract_code(message):
    return CODE_RE.search(message.body).group(0)


class SignupByCodeTests(TestCase):
    def test_signup_creates_user_and_logs_in_after_email_code(self):
        # 1) Alta solo con email -> usuario creado pero aún no autenticado.
        response = self.client.post(
            reverse('account_signup'), {'email': 'nuevo@example.com'}
        )
        self.assertRedirects(
            response, reverse('account_email_verification_sent')
        )
        user = User.objects.get(email='nuevo@example.com')
        self.assertNotIn('_auth_user_id', self.client.session)

        # 2) Se envió un correo con el código de verificación.
        self.assertEqual(len(mail.outbox), 1)
        code = extract_code(mail.outbox[0])

        # 3) Al confirmar el código, queda verificado y autenticado.
        confirm = self.client.post(
            reverse('account_email_verification_sent'), {'code': code}
        )
        self.assertRedirects(confirm, reverse('stories:list'))
        self.assertEqual(
            self.client.session['_auth_user_id'], str(user.pk)
        )

    def test_signup_with_wrong_code_does_not_authenticate(self):
        self.client.post(
            reverse('account_signup'), {'email': 'nuevo@example.com'}
        )
        self.client.post(
            reverse('account_email_verification_sent'), {'code': 'XXXX-XXXX'}
        )
        self.assertNotIn('_auth_user_id', self.client.session)


class LoginByCodeTests(TestCase):
    def setUp(self):
        # Usuario passwordless ya existente y con email verificado.
        self.user = User.objects.create_user(email='ada@example.com')
        from allauth.account.models import EmailAddress
        EmailAddress.objects.create(
            user=self.user, email=self.user.email, verified=True, primary=True
        )

    def test_existing_user_logs_in_with_emailed_code(self):
        response = self.client.post(
            reverse('account_request_login_code'), {'email': 'ada@example.com'}
        )
        self.assertRedirects(response, reverse('account_confirm_login_code'))
        self.assertEqual(len(mail.outbox), 1)
        code = extract_code(mail.outbox[0])

        confirm = self.client.post(
            reverse('account_confirm_login_code'), {'code': code}
        )
        self.assertRedirects(confirm, reverse('stories:list'))
        self.assertEqual(
            self.client.session['_auth_user_id'], str(self.user.pk)
        )

    def test_login_code_for_unknown_email_creates_no_user(self):
        self.client.post(
            reverse('account_request_login_code'),
            {'email': 'desconocido@example.com'},
        )
        self.assertFalse(
            User.objects.filter(email='desconocido@example.com').exists()
        )
