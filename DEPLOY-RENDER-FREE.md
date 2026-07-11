# Deploy a Render — 100% Gratuito

> Arquitectura: **Render** (web) + **Neon** (PostgreSQL) + **Cloudinary** (imágenes)
> Costo mensual: **$0 USD**

## Stack gratuito

| Servicio | Uso | Free tier | ¿Caduca? |
|----------|-----|-----------|:--------:|
| [Render](https://render.com) | Web service (Flask) | 512 MB RAM, 0.1 CPU, 750 h/mes, 100 GB ancho de banda | **No**, permanente |
| [Neon](https://neon.tech) | PostgreSQL | 0.5 GB almacenamiento, 100 CU-h/mes, auto-suspend | **No**, permanente |
| [Cloudinary](https://cloudinary.com) | Imágenes (velas/oraciones) | 25 créditos/mes (~25 GB almacenamiento O 25 GB descarga) | **No**, permanente |

### Por qué NO usar los servicios gratuitos de Render

- **Render PostgreSQL free**: la base de datos se **elimina automáticamente a los 30 días**. Alternativa → Neon.
- **Render Disk free**: el almacenamiento persistente solo está disponible desde $7/mes. Alternativa → Cloudinary.

### Limitaciones a aceptar

- **Cold start**: el web service se duerme a los 15 min de inactividad. La primera visita tarda 30-60s en cargar.
- **Horas de cómputo Neon**: 100 CU-h/mes. Un catálogo con tráfico bajo consume ~10-30 CU-h/mes.
- **Créditos Cloudinary**: 25/mes. ~50 imágenes consumen ~3-5 créditos/mes.
- **Sin backups automáticos** de BD en el free tier de Neon.

---

## Setup inicial (pasos manuales)

### 1. Neon — Crear base de datos

1. Registrarse en https://neon.tech (GitHub, sin tarjeta de crédito)
2. Crear un proyecto (región **US East** o la más cercana)
3. En "Connection Details", copiar el **connection string** (`postgresql://user:pass@ep-.../neondb`)
4. Guardar para usarlo como `DATABASE_URL` en Render

### 2. Cloudinary — Crear cuenta de imágenes

1. Registrarse en https://cloudinary.com (sin tarjeta de crédito)
2. Ir a **Dashboard** → copiar:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
3. Guardar para usarlos como variables de entorno en Render

### 3. Render — Crear Web Service

1. Subir el código a un repositorio de **GitHub**
2. Registrarse en https://render.com con GitHub
3. Dashboard → **New +** → **Web Service**
4. Conectar el repositorio
5. Configurar:

| Campo | Valor |
|-------|-------|
| Name | `esoteria` |
| Runtime | `Docker` |
| Branch | `main` |
| Plan | **Free** |
| Dockerfile Path | `./Dockerfile` |

6. Agregar **Environment Variables**:

| Variable | Valor |
|----------|-------|
| `DATABASE_URL` | Connection string de Neon |
| `CLOUDINARY_CLOUD_NAME` | De Cloudinary Dashboard |
| `CLOUDINARY_API_KEY` | De Cloudinary Dashboard |
| `CLOUDINARY_API_SECRET` | De Cloudinary Dashboard |
| `SECRET_KEY` | Click en **Generate** |

7. Click en **Deploy Web Service**
8. La app quedará disponible en `https://esoteria.onrender.com`

### 4. Configurar ADMIN_PASSWORD

Tras el primer deploy:

1. Ir a Render Dashboard → Environment
2. Agregar: `ADMIN_PASSWORD` = contraseña deseada
3. Ir a **Manual Deploy** → **Deploy latest commit**
4. El admin se crea automáticamente con username `admin` y esa contraseña

---

## Archivos del proyecto

### `requirements.txt`

```
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
WTForms==3.1.1
Werkzeug==3.0.1
psycopg2-binary==2.9.9
python-dotenv==1.0.0
Pillow==10.2.0
cloudinary==1.40.0
gunicorn==22.0.0
```

### `Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN chmod +x entrypoint.sh
CMD ["./entrypoint.sh"]
```

### `entrypoint.sh`

```bash
#!/bin/bash
set -e
python -c "
from app import create_app
from config import Config
import os, time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from app.models import db
from seed import seed_data

app = create_app()
with app.app_context():
    url = app.config['SQLALCHEMY_DATABASE_URI']
    engine = create_engine(url)
    for i in range(30):
        try:
            conn = engine.connect()
            conn.close()
            break
        except OperationalError:
            if i < 29:
                time.sleep(1)
    else:
        raise RuntimeError('No se pudo conectar a la base de datos')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()
    seed_data()
"
exec gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} run:app
```

### `run.py`

```python
from app import create_app
app = create_app()
```

### `config.py`

```python
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clave-secreta-cambiar-en-produccion')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://user:password@localhost:5432/esoteria')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'tiff', 'tif', 'ico'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
```

### `app/__init__.py`

```python
import cloudinary
import cloudinary.uploader
import cloudinary.api
from flask import Flask
from flask_login import LoginManager
from config import Config
from app.models import db, Usuario

login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    cloudinary.config(
        cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
        api_key=app.config['CLOUDINARY_API_KEY'],
        api_secret=app.config['CLOUDINARY_API_SECRET'],
        secure=True
    )

    db.init_app(app)
    login_manager.init_app(app)

    from app.routes.auth import auth_bp
    from app.routes.velas import velas_bp
    from app.routes.oraciones import oraciones_bp
    from app.routes.categorias import categorias_bp
    from app.routes.public import public_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(velas_bp)
    app.register_blueprint(oraciones_bp)
    app.register_blueprint(categorias_bp)
    app.register_blueprint(public_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(Usuario, int(user_id))

    return app
```

### `app/routes/velas.py` — Fragmento del upload

```python
result = cloudinary.uploader.upload(file.stream, folder='esoteria')
vela.imagen = result['secure_url']
```

Reemplaza esta línea anterior (guardado local):
```python
img.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename), optimize=True, quality=85)
vela.imagen = filename
```

### `app/routes/oraciones.py` — Mismo cambio que velas

### Templates — Cambio de URLs

Donde antes se usaba:
```jinja
<img src="{{ url_for('static', filename='uploads/' + vela.imagen) }}">
```

Ahora se usa (URL directa de Cloudinary):
```jinja
<img src="{{ vela.imagen }}">
```

En el modal JavaScript de `catalog.html`, reemplazar:
```javascript
const baseUrl = '{{ url_for("static", filename="uploads/") }}';
// ...
data.imagen ? `<img src="${baseUrl}${data.imagen}"...`
```

Por:
```javascript
// ya no se necesita baseUrl
data.imagen ? `<img src="${data.imagen}"...`
```

### `render.yaml`

```yaml
services:
  - type: web
    name: esoteria
    runtime: docker
    plan: free
    envVars:
      - key: SECRET_KEY
        generateValue: true
      - key: ADMIN_PASSWORD
        sync: false
      - key: DATABASE_URL
        sync: false
      - key: CLOUDINARY_CLOUD_NAME
        sync: false
      - key: CLOUDINARY_API_KEY
        sync: false
      - key: CLOUDINARY_API_SECRET
        sync: false
```

---

## Desarrollo local

El `docker-compose.yml` original sigue funcionando para desarrollo local sin necesidad de Cloudinary (usa almacenamiento local como antes). Para desarrollo:

```bash
docker compose up --build
```

## Mantenimiento

- Para **actualizar el seed** o cambiar datos iniciales: editar `seed.py` y redeployear en Render
- Para **ver logs**: Render Dashboard → esoteria → Logs
- Para **acceder a la BD**: usar `psql` con el connection string de Neon, o Neon Dashboard → SQL Editor
- Las **imágenes subidas** se gestionan desde Cloudinary Dashboard
