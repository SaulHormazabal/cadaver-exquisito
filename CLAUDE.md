# CLAUDE.md

Guía para trabajar en este repositorio. Mantenla corta y específica del proyecto.

## Resumen

Monolito **Django 6** (`config/`) gestionado con **UV**. Requiere **Python 3.12+**.

Apps:
- **`users`** — usuario personalizado **solo-email, sin username** (`User`, `USERNAME_FIELD =
  'email'`, `UserManager` propio). `AUTH_USER_MODEL = 'users.User'`.
- **`stories`** — app de ejemplo que demuestra los lineamientos del proyecto
  (CBV genéricas, `FilterView`, signals, HTMX, tests). Es un vehículo de demostración:
  puede ampliarse o reemplazarse por el dominio real.

## Autenticación

Sin contraseña, con **django-allauth** (*Login by Code*). Tanto el alta como el inicio de
sesión se completan ingresando un **código que llega por correo**:
- Registro: `/accounts/signup/` (solo email) → código de verificación → confirmar en
  `/accounts/confirm-email/`.
- Login: `/accounts/login/` → "código de acceso" → confirmar en `/accounts/login/code/confirm/`.
- Los superusuarios (`createsuperuser`, pide email + contraseña) entran a `/admin/` con
  contraseña; los usuarios finales son passwordless.
- Las vistas de **escritura** de historias (`create`/`update`/`delete`) exigen login
  (`LoginRequiredMixin`); listado y detalle son públicos.
- En desarrollo el correo usa el backend de **consola** (el código aparece en la terminal).

## Comandos

Todo se ejecuta a través de UV (`uv run ...`):

```bash
docker compose up -d db                       # PostgreSQL local — requerido antes de migrar/correr
uv run python manage.py migrate               # aplicar migraciones
uv run python manage.py makemigrations        # generar migraciones
uv run python manage.py test                  # suite de tests
uv run python manage.py runserver             # servidor de desarrollo
uv run python manage.py createsuperuser       # crea un users.User
```

Dependencias: usar `uv add <paquete>` (o `uv remove`). **No** editar `pyproject.toml` a
mano ni usar `pip`.

## Configuración / entorno

Las variables se leen desde `.env` con **`django-environ`** en `config/settings.py`.
Para empezar: copiar `.env.example` → `.env` y ajustar. `.env` está en `.gitignore`.

Variables: `DATABASE_URL`, `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, y las de correo
(`EMAIL_BACKEND` y, para SMTP en producción, `EMAIL_HOST`/`EMAIL_PORT`/`EMAIL_HOST_USER`/
`EMAIL_HOST_PASSWORD`/`EMAIL_USE_TLS`/`DEFAULT_FROM_EMAIL`).

PostgreSQL se levanta con `docker-compose.yml` (servicio `db`, `postgres:16`); sus
credenciales deben coincidir con el `DATABASE_URL` del `.env`.

## Convenciones (lineamientos a respetar al añadir features)

- **Vistas:** genéricas basadas en clases (`ListView`, `DetailView`, `CreateView`, etc.).
- **Listados con filtro:** usar `FilterView` de `django-filter`. Los `FilterSet` viven en
  un `filters.py` por app (ej. `stories/filters.py`).
- **Signals:** definirlos en `signals.py`, conectarlos con el decorador `@receiver`, e
  importarlos desde `AppConfig.ready()` (ver `stories/apps.py` y `stories/signals.py`).
- **Frontend:** Django templates. Lo dinámico se implementa con **HTMX** (htmx por CDN en
  `templates/base.html`; `django_htmx` aporta `request.htmx`). Patrón: la vista devuelve un
  partial en peticiones HTMX — ver `StoryListView.get_template_names` en `stories/views.py`.
- **Estilos:** Bootstrap 5 por CDN.
- **Tests:** suite de Django (`TestCase`), en el paquete `tests/` de cada app
  (`test_models.py`, `test_filters.py`, `test_views.py`).

## Estructura

```
config/            settings.py (django-environ, allauth, AUTH_USER_MODEL, middleware), urls.py
users/             models.py (User solo-email + UserManager), admin.py, tests/
stories/           models.py, filters.py, signals.py, apps.py, views.py, urls.py, admin.py
                   templates/stories/ (+ partials/_story_table.html para HTMX), tests/
templates/         base.html (Bootstrap + htmx por CDN); allauth/layouts/base.html (override)
docker-compose.yml servicio PostgreSQL para desarrollo
.env / .env.example
```

Las páginas de auth las aporta allauth; se reestilan extendiendo `base.html` vía el override
`templates/allauth/layouts/base.html`.
