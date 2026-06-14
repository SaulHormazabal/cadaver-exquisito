# cadaver-exquisito

Monolito **Django 6** que sirve de base para el proyecto. Incluye una app de ejemplo
(`stories`) que demuestra las convenciones técnicas del repositorio: vistas genéricas
basadas en clases, filtrado con `django-filter` (`FilterView` + `FilterSet`), signals
conectados con decoradores, frontend con Django templates + HTMX y suite de tests de
Django.

## Stack

- Python 3.12+
- Django 6
- PostgreSQL 16
- [django-filter](https://django-filter.readthedocs.io/), [django-htmx](https://django-htmx.readthedocs.io/), [django-environ](https://django-environ.readthedocs.io/), [django-allauth](https://docs.allauth.org/)
- Bootstrap 5 y [htmx](https://htmx.org/) por CDN
- Gestor de paquetes: [UV](https://docs.astral.sh/uv/)
- Docker (para PostgreSQL en desarrollo)

## Apps

- **`users`** — usuario personalizado **solo-email, sin username** (`USERNAME_FIELD = 'email'`),
  con `AUTH_USER_MODEL = 'users.User'`.
- **`stories`** — app de ejemplo que ejercita los lineamientos del proyecto. Es un vehículo
  de demostración; puede ampliarse o reemplazarse por el dominio real.

## Autenticación

Sin contraseña, mediante **código enviado por correo** (django-allauth, *Login by Code*):

- **Registro** (`/accounts/signup/`): ingresar el email → llega un código → confirmarlo.
- **Login** (`/accounts/login/`): ingresar el email → llega un código → confirmarlo.
- Crear/editar/eliminar historias requiere haber iniciado sesión; el listado y el detalle
  son públicos.
- En **desarrollo** el correo se imprime en la consola (el código aparece en la terminal);
  en **producción** se configura SMTP por variables de entorno.
- El panel `/admin/` usa email + contraseña (crea un superusuario con `createsuperuser`).

## Puesta en marcha

Requisitos previos: [UV](https://docs.astral.sh/uv/getting-started/installation/) y Docker.

```bash
# 1. Instalar dependencias (UV crea el entorno y resuelve Python 3.12)
uv sync

# 2. Configurar variables de entorno
cp .env.example .env        # ajustar valores si es necesario

# 3. Levantar PostgreSQL
docker compose up -d db

# 4. Aplicar migraciones
uv run python manage.py migrate

# 5. (Opcional) Crear un superusuario
uv run python manage.py createsuperuser

# 6. Arrancar el servidor de desarrollo
uv run python manage.py runserver
```

La aplicación queda disponible en http://127.0.0.1:8000/ (la raíz redirige al listado de
historias en `/stories/`). El panel de administración está en `/admin/`.

## Tests

```bash
uv run python manage.py test
```

## Estructura

```
config/            # proyecto Django: settings.py, urls.py, wsgi/asgi
users/             # modelo de usuario personalizado
stories/           # app de ejemplo: models, filters, signals, views, templates, tests
templates/         # base.html (Bootstrap + htmx por CDN)
docker-compose.yml # servicio PostgreSQL para desarrollo
.env.example       # plantilla de variables de entorno
```

## Configuración

Las variables se leen desde `.env` con `django-environ`. El archivo `.env` está
git-ignored; usa `.env.example` como plantilla.

| Variable | Descripción |
|---|---|
| `SECRET_KEY` | Clave secreta de Django |
| `DEBUG` | `True`/`False` |
| `ALLOWED_HOSTS` | Lista separada por comas |
| `DATABASE_URL` | URL de conexión a PostgreSQL |

## Convenciones

Para contribuir respetando los lineamientos del proyecto (vistas genéricas, `FilterView`,
`filters.py`, `signals.py` con `@receiver`, HTMX, tests de Django, dependencias con UV),
revisa [`CLAUDE.md`](./CLAUDE.md).
