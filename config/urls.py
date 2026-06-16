"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from allauth.account.views import RequestLoginCodeView
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Login unificado por código: /accounts/login/ pide el email y envía el código.
    # Si la cuenta no existe, se crea (ver users.forms.BootstrapRequestLoginCodeForm).
    # Sin contraseña ni registro aparte: /accounts/signup/ redirige al login.
    path('accounts/login/', RequestLoginCodeView.as_view(), name='account_login'),
    path(
        'accounts/signup/',
        RedirectView.as_view(pattern_name='account_login', permanent=False),
        name='account_signup',
    ),
    path('accounts/', include('allauth.account.urls')),
    path('historias/', include('corpse.urls')),
    path('', RedirectView.as_view(pattern_name='corpse:list', permanent=False)),
]
