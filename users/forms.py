from allauth.account.forms import (
    ConfirmEmailVerificationCodeForm,
    ConfirmLoginCodeForm,
    LoginForm,
    RequestLoginCodeForm,
    SignupForm,
)
from django import forms


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


class BootstrapLoginForm(BootstrapFormMixin, LoginForm):
    pass


class BootstrapSignupForm(BootstrapFormMixin, SignupForm):
    pass


class BootstrapRequestLoginCodeForm(BootstrapFormMixin, RequestLoginCodeForm):
    pass


class BootstrapConfirmLoginCodeForm(BootstrapFormMixin, ConfirmLoginCodeForm):
    pass


class BootstrapConfirmEmailVerificationCodeForm(
    BootstrapFormMixin, ConfirmEmailVerificationCodeForm
):
    pass
