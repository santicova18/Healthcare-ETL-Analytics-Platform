# Acceso por roles (3) + levantar el server (front)

Este proyecto es un **backend Django** que expone un “front” basado en vistas/templates (p.ej. Dashboard) y también endpoints bajo `/api/...`.

> Importante: el repo **no define contraseñas hardcodeadas** para roles. Por seguridad, aquí te dejo cómo crear los 3 usuarios con sus roles usando el modelo real.

---

## 1) Roles disponibles (según `authentication/models.py`)
El modelo `User` tiene un campo `role` con estos valores:
- **Administrador**
- **Médico**
- **Analista**

---

## 2) Crear los 3 usuarios (Administrador / Médico / Analista)
### Opción A (rápida): Django shell
Ejecuta:

```bat
python backend/manage.py shell
```

Dentro del shell:

```python
from authentication.models import User

# crea usuarios (ajusta username/password si quieres)
admin = User.objects.create_user(username='admin', password='Admin123!', role='Administrador')
medico = User.objects.create_user(username='medico', password='Medico123!', role='Médico')
analista = User.objects.create_user(username='analista', password='Analista123!', role='Analista')

print(admin.username, medico.username, analista.username)
```

> Si algún usuario ya existe y te falla, usa `get_or_create` o borra previamente esos registros.

### Opción B: Admin de Django
1. Crea superusuario:
   ```bat
   python backend/manage.py createsuperuser
   ```
2. Entra a `http://localhost:8000/admin/`.
3. Crea/edita usuarios y asigna el campo **role**.

---

## 3) Entrar al front desde el navegador
### Levantar el server
Desde la raíz del repo:

1) Instala dependencias:
```bat
pip install -r requirements/base.txt
```

2) Ejecuta migraciones (si hace falta):
```bat
python backend/manage.py migrate
```

3) Corre Django:
```bat
python backend/manage.py runserver 8000
```

### URLs para navegar (front)
- **Dashboard (front principal):**
  - `http://localhost:8000/dashboard/`
  - o también puede redirigir a `http://localhost:8000/api/dashboard/` dependiendo de rutas/redirects.
- **Login (vista plantilla):**
  - `http://localhost:8000/auth/`
  - o el path de login usado por redirecciones: `http://localhost:8000/api/auth/login/`

> El login está implementado en `apps/authentication/views.py` y si el usuario ya está autenticado redirige al dashboard.

---

## 4) Probar por rol (quick checks)
1. Abre el login en el navegador.
2. Inicia sesión con cada usuario:
   - admin / Admin123!
   - medico / Medico123!
   - analista / Analista123!
3. Verifica que el Dashboard y las secciones del front/links protegidos cargan o deniegan según rol.

---

# Nota sobre credenciales en el MD
Las credenciales de arriba (admin/medico/analista) y sus passwords (**Admin123!**, **Medico123!**, **Analista123!**) son **las que vas a usar** para loguearte. 

Si ya existen usuarios con esos usernames, Django rechazará la creación; entonces usa `get_or_create` o cambia los usernames/passwords.


