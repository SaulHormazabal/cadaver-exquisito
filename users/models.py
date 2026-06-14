from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Modelo de usuario personalizado.

    Hereda todo el comportamiento de autenticación de Django y deja espacio
    para campos propios del proyecto.
    """

    display_name = models.CharField('nombre visible', max_length=150, blank=True)
    bio = models.TextField('biografía', blank=True)

    def __str__(self):
        return self.display_name or self.get_username()
