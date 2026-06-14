# CLAUDE.md

Guía para trabajar en este repositorio. Mantenla corta y específica del proyecto.

## Resumen

Monolito **Django 6** (`config/`) gestionado con **UV**. Requiere **Python 3.12+**.

Apps:
- **`users`** — usuario personalizado **solo-email, sin username** (`User`, `USERNAME_FIELD =
  'email'`, `UserManager` propio). `AUTH_USER_MODEL = 'users.User'`.
- **`corpse`** — el juego del **cadáver exquisito**: historia colaborativa por turnos.
  `Story` (la pieza, con `visibility` TAIL/FULL, `tail_words`, `max_fragments`, `status`
  OPEN/CLOSED) y `Fragment` (cada contribución, con `order` y
  `UniqueConstraint(story, order)`). Sigue los lineamientos del proyecto (CBV genéricas,
  `FilterView`, signals, HTMX, tests). Montada en la raíz (`config/urls.py`).

## Autenticación

Sin contraseña, con **django-allauth** (*Login by Code*). **Login y registro unificados**:
no hay página de registro aparte.
- `/accounts/login/` → ingresar el email → llega un **código por correo** → confirmarlo en
  `/accounts/login/code/confirm/`. **Si la cuenta no existe, se crea** (ver
  `users.forms.BootstrapRequestLoginCodeForm.clean_email`).
- `/accounts/signup/` redirige al login (no hay registro separado).
- La sesión **siempre se recuerda** (`ACCOUNT_SESSION_REMEMBER = True`, sin checkbox).
- Los superusuarios (`createsuperuser`, pide email + contraseña) entran a `/admin/` con
  contraseña; los usuarios finales son passwordless.
- Las vistas de **escritura** de historias (`create`/`contribute`/`close`) exigen login
  (`LoginRequiredMixin`); listado y detalle son públicos.
- Formularios y botones de allauth reestilados con Bootstrap (`users/forms.py` vía
  `ACCOUNT_FORMS`, y overrides en `templates/allauth/elements/` y `templates/account/`).
- En desarrollo el correo usa el backend de **consola** (el código aparece en la terminal).

## Dinámica del juego (app `corpse`)

Historia colaborativa por turnos, **asíncrona** (sin tiempo real):

- **Inicio:** crear una `Story` incluye su **primer `Fragment`** (orden 1) escrito por el
  creador, junto con los ajustes: `visibility` (`TAIL` = solo el final del fragmento
  anterior / `FULL` = el último fragmento completo), `tail_words` (solo aplica en `TAIL`) y
  `max_fragments` (`>= 2`).
- **Visibilidad / ocultamiento (seguridad):** mientras la historia está `OPEN`, el servidor
  **nunca** envía los fragmentos ocultos. El detalle muestra solo `Story.visible_snippet()`
  del último fragmento. El texto completo (`Story.assembled_text()` / fragmentos atribuidos)
  se revela **solo** cuando `CLOSED`.
- **Turno (sin dos seguidos):** un usuario autenticado puede aportar el siguiente fragmento
  si la historia está `OPEN`, no está llena, y **no es** el autor del último fragmento
  (validado en `FragmentCreateView`).
- **Concurrencia:** `order = fragment_count + 1` dentro de una transacción; la
  `UniqueConstraint(story, order)` corta la carrera (al saltar `IntegrityError` se
  re-renderiza con el nuevo snippet).
- **Cierre/revelado:** un signal `post_save` en `Fragment` cierra la historia al alcanzar
  `max_fragments`; el creador también puede cerrarla antes (`StoryCloseView`, solo POST).

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
  un `filters.py` por app (ej. `corpse/filters.py`).
- **Signals:** definirlos en `signals.py`, conectarlos con el decorador `@receiver`, e
  importarlos desde `AppConfig.ready()` (ver `corpse/apps.py` y `corpse/signals.py`).
- **Frontend:** Django templates. Lo dinámico se implementa con **HTMX** (htmx por CDN en
  `templates/base.html`; `django_htmx` aporta `request.htmx`). Patrón: la vista devuelve un
  partial en peticiones HTMX — ver `StoryListView.get_template_names` en `corpse/views.py`.
- **Estilos:** Bootstrap 5 por CDN.
- **Tests:** suite de Django (`TestCase`), en el paquete `tests/` de cada app
  (`test_models.py`, `test_filters.py`, `test_views.py`).

## Estructura

```
config/            settings.py (django-environ, allauth, AUTH_USER_MODEL, middleware), urls.py
users/             models.py (User solo-email + UserManager), admin.py, tests/
corpse/            models.py (Story + Fragment), forms.py, filters.py, signals.py, apps.py,
                   views.py, urls.py, admin.py
                   templates/corpse/ (+ partials/_story_table.html para HTMX), tests/
templates/         base.html (Bootstrap + htmx por CDN); allauth/layouts/base.html (override)
docker-compose.yml servicio PostgreSQL para desarrollo
.env / .env.example
```

Las páginas de auth las aporta allauth; se reestilan extendiendo `base.html` vía el override
`templates/allauth/layouts/base.html`.
