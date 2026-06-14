from allauth.account.forms import (
    ConfirmEmailVerificationCodeForm,
    ConfirmLoginCodeForm,
    RequestLoginCodeForm,
)
from allauth.account.models import EmailAddress
from django import forms
from django.contrib.auth import get_user_model


class BootstrapFormMixin:
    """Aplica las clases de Bootstrap 5 a los widgets del formulario.

    allauth renderiza sus formularios con `form.as_p`, que respeta los `attrs`
    del widget; basta con fijar la clase adecuada según el tipo de campo.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                css_class = 'form-check-input'
            elif isinstance(widget, forms.Select):
                css_class = 'form-select'
            else:
                css_class = 'form-control'
            existing = widget.attrs.get('class', '')
            widget.attrs['class'] = f'{existing} {css_class}'.strip()


class BootstrapRequestLoginCodeForm(BootstrapFormMixin, RequestLoginCodeForm):
    """Login unificado: si el email no tiene cuenta, se crea al pedir el código."""

    def clean_email(self):
        email = super().clean_email()
        if email and self._user is None:
            User = get_user_model()
            user = User.objects.create_user(email=email)
            EmailAddress.objects.create(
                user=user, email=email, primary=True, verified=False
            )
            self._user = user
        return email


class BootstrapConfirmLoginCodeForm(BootstrapFormMixin, ConfirmLoginCodeForm):
    pass


class BootstrapConfirmEmailVerificationCodeForm(
    BootstrapFormMixin, ConfirmEmailVerificationCodeForm
):
    pass
