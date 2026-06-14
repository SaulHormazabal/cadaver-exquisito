# CLAUDE.md

Guía para trabajar en este repositorio. Mantenla corta y específica del proyecto.

## Resumen

Monolito **Django 6** (`config/`) gestionado con **UV**. Requiere **Python 3.12+**.

Apps:
- **`users`** — modelo de usuario personalizado (`User(AbstractUser)`).
  `AUTH_USER_MODEL = 'users.User'` (definido desde el inicio del proyecto).
- **`stories`** — app de ejemplo que demuestra los lineamientos del proyecto
  (CBV genéricas, `FilterView`, signals, HTMX, tests). Es un vehículo de demostración:
  puede ampliarse o reemplazarse por el dominio real.

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

Variables: `DATABASE_URL`, `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`.

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
config/            settings.py (django-environ, AUTH_USER_MODEL, middleware HTMX), urls.py
users/             models.py (User), admin.py, tests/
stories/           models.py, filters.py, signals.py, apps.py, views.py, urls.py, admin.py
                   templates/stories/ (+ partials/_story_table.html para HTMX), tests/
templates/         base.html (Bootstrap + htmx por CDN)
docker-compose.yml servicio PostgreSQL para desarrollo
.env / .env.example
```
