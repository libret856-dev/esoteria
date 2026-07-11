# Esotería — Catálogo Espiritual

> **Estado:** Implementado
> **Última actualización:** julio 2026 — Mejoras de seguridad v1

---

## 1. Descripción del proyecto

Sistema web de catálogo espiritual con dos roles de usuario. Los **editores** (con login) pueden crear, editar y eliminar velas, oraciones y categorías. Los **consultores** (sin login, acceso público) pueden buscar y ver velas y oraciones en secciones separadas del catálogo.

Las **categorías** funcionan como etiquetas (relación muchos a muchos): una vela u oración puede tener varias categorías asociadas (ej. "Salud" y "Buena Suerte"), y una categoría puede estar en múltiples velas y oraciones. Esto permite filtrar por categoría en el catálogo público.

**Novedades implementadas:**
- Tema visual **cósmico oscuro** (fondo espacio, estrellas animadas, texto dorado, glassmorphism)
- Sistema de **colores por categoría** — cada categoría tiene un color hex asignable desde el panel admin; badges, bordes, auras y placeholders se tiñen dinámicamente
- **Tarjetas con animaciones permanentes** — entrada escalonada (stagger), levitación infinita, brillo tipo aura, sombra parallax
- **Placeholder con gradiente** en tarjetas que no tienen imagen: violeta por defecto, o combinación multicolor si tiene categorías
- **Glosario colapsable de categorías** en el catálogo público (tooltips visibles también en móvil)
- Campo `descripcion` en velas (características físicas: color, tamaño, aroma, etc.)
- **Elementos relacionados** en el modal: al ver una vela se muestran oraciones relacionadas por categorías (y viceversa)
- Animación **bounce** en apertura/cierre del modal
- Tooltips con descripción de categorías en badges
- **Glosario con colores** — cada categoría en el glosario muestra su color como fondo tintado (más visible al hover)
- **Glosario clickeable** — al hacer clic en una categoría del glosario se filtra el catálogo, mostrando solo velas y oraciones de esa categoría
- **Imágenes en oraciones** — las oraciones ahora soportan subida y visualización de imágenes (igual que velas)
- **Paginación** — catálogo público (12 items/página) y dashboard (15 items/página) con páginas independientes por sección
- **Vista previa de imagen** — preview en vivo al seleccionar archivo en formularios de velas y oraciones
- **Modal close sticky** — botón de cierre del modal se mantiene visible al hacer scroll en dispositivos móviles
- **Chips toggle para categorías** — selección múltiple de categorías con chips coloreados clickeables (sin Ctrl+click, funcional en móvil) en formularios del dashboard
- **Texto a voz en oraciones** — botón "🔊 Leer oración" / "⏹ Detener oración" en el modal usando Web Speech API con voz en español; se detiene al cerrar el modal; oculto si la API o voz en español no están disponibles
- **Campo `proposito` en oraciones** — propósito/beneficio de cada oración con acordeón desplegable "¿Para qué funciona?" en el modal
- **Protección contra XSS** — escape de HTML en el modal del catálogo público para prevenir inyección de scripts
- **Validación real de imágenes** — verificación de contenido con Pillow (`Image.open().verify()`) además de la extensión
- **Rate limiting en login** — bloqueo de 15 minutos tras 5 intentos fallidos de inicio de sesión

---

## 2. Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11 + Flask |
| ORM | SQLAlchemy |
| Autenticación | Flask-Login + Werkzeug (password hashing) |
| Formularios | WTForms + Flask-WTF |
| Base de datos | PostgreSQL 15 |
| Contenedores | Docker + docker-compose |
| Frontend | HTML + CSS vanilla (sin frameworks) |
| Templates | Jinja2 |
| Imágenes | Subida de archivos con validación de tipo y tamaño |

---

## 3. Estructura de archivos

```
esoteria/
├── docker-compose.yml
├── Dockerfile
├── .env                          # Variables de entorno
├── requirements.txt
├── run.py                        # Entry point (con wait_for_db)
├── config.py                     # Config class (UPLOAD_FOLDER, etc.)
├── seed.py                       # Datos iniciales (admin + demo)
└── app/
    ├── __init__.py               # create_app() factory
    ├── models.py                 # SQLAlchemy models
    ├── forms.py                  # WTForms
    ├── routes/
    │   ├── __init__.py
    │   ├── auth.py               # Login, logout, change password
    │   ├── velas.py              # CRUD de velas
    │   ├── oraciones.py          # CRUD de oraciones
    │   ├── categorias.py         # CRUD de categorías
    │   └── public.py             # Catálogo público + API + dashboard
    ├── templates/
    │   ├── base.html             # Layout (universo + estrellas + canvas animado)
    │   ├── home.html             # Página de inicio
    │   ├── login.html
    │   ├── change_password.html
    │   ├── catalog.html          # Catálogo con tabs, modal con bounce + relacionados
    │   ├── dashboard.html        # Panel CRUD con tabs (incluye columna Descripción)
    │   ├── vela-form.html        # Crear/editar vela (con campo descripción + sugerencias categorías)
    │   ├── oracion-form.html     # Crear/editar oración (con campo imagen)
    │   ├── categorias.html       # Gestión de categorías
    │   └── categoria-form.html   # Editar categoría
    ├── ejemplo/                  # Prototipos de pruebas visuales
    │   ├── catalog-cards-prototype.html
    │   ├── category-colors-prototype.html
    │   └── multicolor-placeholder-prototype.html
    └── static/
        ├── style.css             # Tema cósmico oscuro + glassmorphism + responsive
        └── uploads/              # Imágenes subidas (creado en tiempo de ejecución)
```

---

## 4. Base de datos (6 tablas)

### Tabla: `usuarios`

| Columna | Tipo | Notas |
|---|---|---|
| id | SERIAL | PK |
| username | VARCHAR(80) | UNIQUE, NOT NULL |
| password_hash | VARCHAR(256) | NOT NULL |
| created_at | TIMESTAMP | DEFAULT now() |

### Tabla: `categorias`

| Columna | Tipo | Notas |
|---|---|---|
| id | SERIAL | PK |
| nombre | VARCHAR(100) | UNIQUE, NOT NULL |
| descripcion | TEXT | NULL |
| color | VARCHAR(7) | NULL — hex color (#RRGGBB) para asignar color visual a la categoría |

### Tabla: `velas`

| Columna | Tipo | Notas |
|---|---|---|
| id | SERIAL | PK |
| nombre | VARCHAR(200) | NOT NULL |
| imagen | VARCHAR(256) | NULL — ruta del archivo subido |
| descripcion | TEXT | NULL — características físicas (color, tamaño, aroma, etc.) |
| created_at | TIMESTAMP | DEFAULT now() |
| updated_at | TIMESTAMP | DEFAULT now() |

### Tabla: `oraciones`

| Columna | Tipo | Notas |
|---|---|---|
| id | SERIAL | PK |
| nombre | VARCHAR(200) | NOT NULL |
| contenido | TEXT | NOT NULL |
| proposito | TEXT | NULL — propósito/beneficio de la oración (visible en acordeón del modal) |
| imagen | VARCHAR(256) | NULL — ruta del archivo subido |
| created_at | TIMESTAMP | DEFAULT now() |

### Tabla puente: `vela_categorias`

| Columna | Tipo | Notas |
|---|---|---|
| vela_id | INTEGER | FK → velas.id (CASCADE) |
| categoria_id | INTEGER | FK → categorias.id (CASCADE) |
| | | PK compuesta: (vela_id, categoria_id) |

### Tabla puente: `oracion_categorias`

| Columna | Tipo | Notas |
|---|---|---|
| oracion_id | INTEGER | FK → oraciones.id (CASCADE) |
| categoria_id | INTEGER | FK → categorias.id (CASCADE) |
| | | PK compuesta: (oracion_id, categoria_id) |

---

## 5. Rutas

| Ruta | Método | Acceso | Descripción |
|---|---|---|---|
| `/` | GET | Público | Home con enlaces a catálogo |
| `/login` | GET, POST | Público | Formulario de inicio de sesión |
| `/logout` | GET | Editores | Cierra sesión |
| `/change-password` | GET, POST | Editores | Cambiar contraseña del usuario logueado |
| `/catalog` | GET | **Público** | Catálogo con pestañas (Todo/Velas/Oraciones), búsqueda y filtro por categoría |
| `/api/velas/<id>` | GET | **Público** | JSON con datos de vela + oraciones relacionadas (para modal) |
| `/api/oraciones/<id>` | GET | **Público** | JSON con datos de oración + velas relacionadas (para modal) |
| `/dashboard` | GET | Editores | Panel con tabs para velas y oraciones |
| `/velas/create` | GET, POST | Editores | Formulario nueva vela (con carga de imagen y descripción) |
| `/velas/<id>/edit` | GET, POST | Editores | Formulario editar vela |
| `/velas/<id>/delete` | POST | Editores | Eliminar vela |
| `/oraciones/create` | GET, POST | Editores | Formulario nueva oración |
| `/oraciones/<id>/edit` | GET, POST | Editores | Formulario editar oración |
| `/oraciones/<id>/delete` | POST | Editores | Eliminar oración |
| `/categorias` | GET, POST | Editores | Listar y crear categorías (ordenadas por más reciente) |
| `/categorias/<id>/edit` | GET, POST | Editores | Editar categoría |
| `/categorias/<id>/delete` | POST | Editores | Eliminar categoría |

---

## 6. Roles y permisos

| Rol | Login | Permisos |
|---|---|---|
| **Editor** | Sí (user/pass en BD) | CRUD completo de velas, oraciones y categorías. Accede a `/dashboard`, `/velas/*`, `/oraciones/*`, `/categorias/*`, `/change-password`. Ve opciones adicionales en el menú. |
| **Consultor** | No (público) | Solo puede acceder a `/`, `/catalog` y `/api/velas/<id>`, `/api/oraciones/<id>`. No ve menú de edición. |

La distinción se maneja con Flask-Login: si `current_user.is_authenticated`, se muestran las opciones de editor. Si no, solo el catálogo público.

---

## 7. Relación muchos a muchos: Categorías

Las categorías funcionan como etiquetas (tags):

- Una **vela** puede tener varias categorías (ej: "Salud" y "Buena Suerte")
- Una **oración** puede tener varias categorías
- Una **categoría** puede estar asociada a múltiples velas y múltiples oraciones

Esto se implementa con dos tablas puente: `vela_categorias` y `oracion_categorias`.

### Sugerencias de categorías en formularios

En el formulario de creación/edición de velas, el select de categorías se renderiza manualmente con `title` en cada opción mostrando la descripción de la categoría al pasar el cursor (tooltips con descripciones como sugerencia).

---

## 8. Catálogo público

El catálogo (`/catalog`) tiene tres pestañas en la parte superior:

1. **Todo** — muestra velas y oraciones juntos
2. **🕯️ Velas** — solo velas
3. **📿 Oraciones** — solo oraciones

Cada sección muestra tarjetas con:
- **Velas:** imagen (completa, sin recortes) o placeholder con gradiente multicolor según categorías, nombre y badges de categorías coloreados
- **Oraciones:** imagen (completa, sin recortes) o placeholder con gradiente multicolor según categorías, nombre y badges de categorías coloreados

Todas las tarjetas tienen:
- **Animación de entrada escalonada** (`stagger-fade-in`) con delay progresivo
- **Levitación infinita** (`float`) que se detiene al hover
- **Aura brillante** alrededor de la tarjeta (`@keyframes aura`)
- **Sombra parallax** que se desplaza con el mouse (JS)
- **Borde con glow** que sigue el color de la categoría principal
- **Badges coloreados** con el color hex de cada categoría (fondo, texto y borde tintados)
- **Badge glow** animado con sombra blanca universal

### Filtros
- **Búsqueda por texto** (nombre, ILIKE)
- **Filtro por categoría** — al hacer clic en una categoría del glosario se filtra el catálogo mostrando solo velas y oraciones de esa categoría
- **Glosario de categorías** desplegable al hacer clic en "📖 Glosario de categorías" — muestra todas las categorías con su color de fondo tintado (más intenso al hover), nombre y descripción; funcional también en móvil

### Modal de detalle
Al hacer clic en una tarjeta se abre un **modal** con:
- Animación **bounceIn** al abrir y **bounceOut** al cerrar
- Imagen (completa sin recortes), nombre, badges de categorías
- **Descripción** de la vela (características físicas)
- **Elementos relacionados:** al final del modal se muestran tarjetas clickeables de oraciones/velas que comparten categorías (cargadas vía API)

Las APIs `/api/velas/<id>` y `/api/oraciones/<id>` ahora devuelven también arreglos `oraciones_relacionadas` y `velas_relacionadas` respectivamente (hasta 4 items cada uno).

---

## 9. Dashboard (editores)

Panel con dos pestañas (tabs):

### Velas
- Tabla con columnas: ID, Nombre, Imagen (miniatura), **Descripción** (preview 80 caracteres), Categorías, Creado, Acciones
- Botón "Nueva vela"
- Editar / Eliminar por fila

### Oraciones
- Tabla con columnas: ID, Nombre, Imagen (miniatura), Contenido (preview 80 caracteres), Categorías, Creado, Acciones
- Botón "Nueva oración"
- Editar / Eliminar por fila

---

## 10. Seed (datos iniciales)

Al arrancar el sistema por primera vez (cuando la tabla `usuarios` está vacía), se ejecuta automáticamente un seed que crea:

- **Admin por defecto:**
  - Username: `admin`
  - Password: definida en `.env` como `ADMIN_PASSWORD` (valor por defecto: `admin123`)

- **Categorías demo (6):**
  - Salud, Buena Suerte, Protección, Amor, Prosperidad, Limpieza Espiritual

- **Velas demo (5):** con nombres, descripciones físicas detalladas (color, tamaño, aroma, materiales), imágenes placeholder y categorías asignadas

- **Oraciones demo (5):** con nombres, contenido y categorías asignadas

---

## 11. Docker

### `Dockerfile`

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "run.py"]
```

### `docker-compose.yml`

Dos servicios:

```yaml
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/esoteria
      - SECRET_KEY=clave-secreta-cambiar-en-produccion
      - ADMIN_PASSWORD=admin123
    depends_on:
      - db
    volumes:
      - uploads:/app/app/static/uploads

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=esoteria
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
  uploads:
```

### Flujo de inicio

```bash
docker compose up --build
```

Esto levanta PostgreSQL → `run.py` espera hasta 30 segundos a que la BD esté lista (`wait_for_db()`) → Flask crea las tablas con SQLAlchemy (`db.create_all()`) → se ejecuta el seed si la BD está vacía → el servidor queda listo en `http://localhost:5000`.

---

## 12. Diseño visual

### Paleta de colores: Tema Cósmico Oscuro + Acentos Dorados

| Elemento | Color | Hex |
|---|---|---|
| **Fondo página** | Gradiente espacio negro → morado → violeta | `#000000` → `#12042E` → `#2A0E5C` → `#4B1B9A` |
| **Header** | Morado oscuro semitransparente | `rgba(18, 4, 46, 0.95)` |
| **Superficies** (cards, forms) | Glassmorphism blanco 7% + blur | `rgba(255,255,255,0.07)` + `backdrop-filter` |
| **Overlay** (entre estrellas y contenido) | Negro semitransparente sutil | `rgba(0, 0, 0, 0.2)` |
| **Acento principal** | Dorado | `#FFD700` |
| **Hover acento** | Dorado claro | `#FFE8A3` |
| **Bordes** | Dorado semitransparente | `rgba(255, 215, 0, 0.15)` |
| **Inputs** | Fondo blanco 8% + borde dorado | `rgba(255,255,255,0.08)` |
| **Texto principal** | Dorado claro | `#F0E6B6` |
| **Texto secundario** | Dorado opaco | `#E2CC80` |
| **Sombras** | Violeta profundo | `rgba(75, 27, 154, 0.3)` |

### Efectos visuales

| Efecto | Descripción |
|---|---|---|
| **Estrellas fijas CSS** | 6 puntos de luz con `radial-gradient` y animación `parpadeo` (opacidad 0.3 → 0.5) |
| **Estrellas dinámicas Canvas** | 80 estrellas que caen suavemente, algunas doradas (15%) |
| **Glassmorphism** | Tarjetas, forms y modales con `backdrop-filter: blur(10px)` |
| **Stagger entrance** | Tarjetas aparecen escalonadamente con `animation-delay` progresivo (0.05s × índice) |
| **Levitación infinita** | `@keyframes float` — levitación suave permanente; se pausa al hover |
| **Aura brillante** | `@keyframes aura` — resplandor que rodea la tarjeta permanentemente |
| **Sombra parallax** | JS mueve la sombra siguiendo el cursor del mouse dentro de la tarjeta |
| **Border glow** | Borde sutil con brillo animado, tintado del color de la categoría principal |
| **Badge glow** | `@keyframes badge-glow` — sombra blanca pulsante en badges |
| **Placeholder gradiente** | Tarjetas sin imagen muestran gradiente: violeta por defecto, o combinación multicolor si tiene categorías (mezcla armónica de 1, 2, 3 o 4+ colores) |
| **Modal bounce** | `bounceIn` → escala 0.3 → 1.08 → 0.92 → 1 (0.4s) / `bounceOut` → inverso (0.3s) |
| **Botones** | Gradiente dorado con hover más brillante + sombra |

### Catálogo público

```
┌──────────────────────────────────────────────────┐
│  [Todo]  [🕯️ Velas]  [📿 Oraciones]    [📖 Glosario]│
├──────────────────────────────────────────────────┤
│  🔍 [Buscar...]                                │
├──────────────────────────────────────────────────┤
│                                                  │
│  🕯️ VELAS                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ [grad    ]│  │ [img    ]│  │ [grad    ]│        │
│  │ 🌈       │  │ completa │  │ 🌈       │        │
│  │ [Salud]  │  │ [Amor]   │  │ [Prot.]  │        │
│  │ [Suerte] │  │          │  │          │        │
│  └──────────┘  └──────────┘  └──────────┘        │
│  ──── levitación + aura + border glow ───         │
│                                                    │
│  📿 ORACIONES                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ [img    ]│  │ 🌈      │  │ [img    ]│        │
│  │ Oración 1│  │ Oración 2│  │ Oración 3│        │
│  │ [Salud]  │  │ [Suerte] │  │ [Amor]   │        │
│  └──────────┘  └──────────┘  └──────────┘        │
└──────────────────────────────────────────────────┘
```

---

## 13. Funcionalidades clave

### Subida de imágenes (velas y oraciones)
- Botón personalizado "Seleccionar imagen" con estilo dorado
- Muestra el nombre del archivo seleccionado
- **Vista previa en vivo:** al seleccionar un archivo se muestra una previsualización inmediata usando `FileReader` (JS)
- Extensiones permitidas: jpg, jpeg, png, gif, webp
- Las imágenes se guardan en `app/static/uploads/` con nombre sanitizado
- Límite de 16MB por archivo
- Las imágenes se muestran completas sin recortes (`object-fit: contain`)
- Disponible tanto en velas como en oraciones

### Descripción de velas
- Campo `descripcion` (TEXT) para características físicas: color, tamaño, peso, aroma, materiales
- Visible en el formulario de creación/edición, en el dashboard (preview 80 caracteres) y en el modal del catálogo público

### Gestión de categorías
- Ruta independiente `/categorias` con formulario de creación y tabla de listado
- Incluye selector de color (`input type="color"`) en creación y edición
- Columna "Color" en la tabla con un círculo de muestra + código hex
- Ordenadas por más reciente primero (ORDER BY id DESC)
- Las categorías se pueden editar y eliminar
- Al eliminar una categoría, se eliminan también las relaciones en las tablas puente (CASCADE)
- En el formulario de velas y oraciones, las categorías se muestran con tooltips descriptivos y fondo tintado del color correspondiente

### Elementos relacionados
- Al abrir el modal de una vela, se muestran hasta 4 oraciones que comparten categorías
- Al abrir el modal de una oración, se muestran hasta 4 velas que comparten categorías
- Las tarjetas relacionadas son clickeables y abren su propio modal

### Colores por categoría
- Cada categoría tiene un campo `color` (VARCHAR(7), formato #RRGGBB) persistido en BD
- Asignable desde el panel admin con un `input type="color"` nativo
- Definidos 6 colores semilla en `seed.py` (Salud=#4CAF50, Buena Suerte=#26A69A, Protección=#42A5F5, Amor=#E91E63, Prosperidad=#FFB300, Limpieza Espiritual=#7E57C2)
- Los badges en el catálogo usan el color inline: fondo con 22 de alpha, texto sólido, borde con 44 de alpha
- El borde y aura de cada tarjeta se tiñen del color de su primera categoría
- Placeholders combinan colores de todas las categorías de la velas/oración:
  - **1 categoría:** color sólido → degradado al centro
  - **2 categorías:** degradado lineal
  - **3 categorías:** degradado radial desde el centro
  - **4+ categorías:** fondo con gradiente de 4 colores distribuidos
- En formularios de creación/edición, las opciones del select de categorías se muestran con fondo tintado del color correspondiente

### Glosario de categorías
- Botón "📖 Glosario de categorías" en el catálogo público
- Al hacer clic, se despliega un panel con cada categoría, su color (círculo de muestra), nombre y descripción
- Cada ítem del glosario tiene un círculo coloreado con el color de la categoría
- Al hacer clic en una categoría del glosario, se filtra el catálogo por esa categoría
- Funciona también en dispositivos táctiles (soluciona la limitación de tooltips nativos en móvil)

### Búsqueda y filtros
- Campo de texto que busca por nombre (ILIKE)
- Selector de categoría (dropdown con tooltips descriptivos en cada opción)
- Los filtros se combinan (texto + categoría)
- Pestañas para filtrar por tipo (Todo / Velas / Oraciones)
- Si no hay resultados, mensaje "No se encontraron resultados"

### Diseño responsive
- Menú hamburguesa en móvil con animación
- Catálogo en una sola columna en dispositivos móviles
- Tablas con scroll horizontal en pantallas pequeñas
- Modal adaptable a cualquier tamaño de pantalla con animación bounce
- Todos los elementos se adaptan desde 480px hasta escritorio

---

## 14. Temas pendientes

- [ ] **Registro de nuevos editores:** si se necesita formulario de registro o solo el admin puede crear otros editores
- [ ] **Búsqueda por contenido de oraciones:** actualmente solo busca por nombre
- [ ] **Buscador en el dashboard:** campo de búsqueda para filtrar velas y oraciones por nombre en el panel de administración



### Completados

- [x] **Tooltips de categorías visibles en móvil:** implementado como glosario colapsable de categorías en el catálogo público
- [x] **Selector de color para categorías:** columna `color` en BD, picker en admin, badges y placeholders tintados dinámicamente
- [x] **Diferenciación visual de velas:** animaciones permanentes (stagger, levitación, aura, sombra parallax, border glow)
- [x] **Placeholder con gradiente:** violeta por defecto; multicolor según categorías si las tiene
- [x] **Paginación:** catálogo público con 12 items/página y dashboard con 15 items/página; páginas independientes por sección en vista "Todo"
- [x] **Imágenes en oraciones:** subida y visualización de imágenes en oraciones (modelo, formulario, rutas, API, dashboard, catálogo)
- [x] **Glosario con colores y clickeable:** círculos de color por categoría y filtrado al hacer clic
- [x] **Diferenciación visual de oraciones:** las oraciones ahora soportan imágenes propias y placeholders con gradiente multicolor según categorías
- [x] **Galería de imágenes (vista previa):** preview en vivo al seleccionar archivo en formularios de velas y oraciones con `FileReader`
- [x] **Modal close sticky:** botón de cierre del modal ahora usa `position: sticky` para mantenerse visible al hacer scroll en móvil
- [x] **Selección múltiple de categorías con chips toggle:** reemplazado el `<select multiple>` (Ctrl+click) por chips coloreados clickeables en formularios del dashboard; funciona en móvil sin necesidad de Ctrl+click
- [x] **Texto a voz en oraciones:** botón "🔊 Leer oración" / "⏹ Detener oración" en el modal con Web Speech API, voz en español; se detiene al cerrar el modal; oculto si no hay soporte
- [x] **Campo `proposito` en oraciones:** columna `proposito` en BD, textarea en formulario, columna en dashboard, y acordeón desplegable "¿Para qué funciona?" en el modal del catálogo público
- [x] **Protección contra XSS en modal:** función `escapeHtml()` que sanitiza todo contenido de usuario antes de insertarlo en el DOM del modal
- [x] **Validación de imágenes con Pillow:** verificación de que el archivo subido es una imagen real usando `Image.open().verify()`, además de la validación de extensión
- [x] **Rate limiting en login:** bloqueo temporal de 15 minutos después de 5 intentos fallidos, usando `session` de Flask

---

## 15. Notas para implementación futura

- **Flujo de inicio:** `docker compose up --build` → espera 30s a PostgreSQL → tablas → seed → servidor en `http://localhost:5000`
- **Si se añade una columna nueva a la BD con Docker:** usar `docker compose down -v` y luego `docker compose up --build` para recrear volúmenes
- **El admin por defecto** se crea solo si la tabla `usuarios` está vacía (para no sobrescribir cambios)
- **El `.env`** debe incluir: `SECRET_KEY`, `DATABASE_URL`, `ADMIN_PASSWORD`
- **`requirements.txt`** incluye: `Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, WTForms, Werkzeug, psycopg2-binary, python-dotenv, Pillow`
- **Modal:** implementado con HTML + CSS + JS vanilla (sin librerías externas), con animaciones bounceIn/bounceOut
- **Estrellas animadas:** canvas con 80 estrellas + 6 estrellas fijas CSS + overlay oscuro para contraste
- **Colores de categoría:** se almacenan como `VARCHAR(7)` en BD y se renderizan inline en los templates (background con 22 alpha, borde con 44 alpha, texto sólido). No se usan variables CSS porque los colores son dinámicos desde la BD.
- **Placeholder gradients:** se genera un `style` inline con el gradiente CSS apropiado según la cantidad de categorías (1, 2, 3 o 4+). La función `get_placeholder_gradient()` en `public.py` prepara los colores, y el template construye el gradiente.
- **Las tarjetas** usan `animation-delay` basado en el índice del loop de Jinja (`{{ loop.index0 }}`) para el stagger effect
- **Vista previa de imagen:** función `previewImagen()` en `base.html` usa `FileReader.readAsDataURL()` para mostrar preview en vivo al seleccionar archivo. Los estilos `.image-preview` ocultan/muestran el `<img>` con clase `.hidden`.
- **La sombra parallax** se actualiza con JS (`mousemove` dentro de la tarjeta) y se revierte al hacer `mouseleave`
- **La búsqueda** se hace del lado del servidor (GET `/catalog?q=texto&categoria=id&tipo=velas`)
- **Paginación:** usa `?page=N` en tabs individuales y `?page_velas=N&page_oraciones=N` en vista "Todo". Dashboard usa `?tab=velas&page=N`. Los filtros `q`, `categoria`, `tipo` se preservan en la navegación.
- **PostgreSQL** se conecta usando `psycopg2-binary` con URI desde variable de entorno `DATABASE_URL`
- **Contraseña admin** se lee de variable de entorno `ADMIN_PASSWORD` con fallback a `admin123`
- **Categorías** se ordenan por `id DESC` (más reciente primero) en todos los listados
- **Imágenes** usan `object-fit: contain` para mostrarse completas sin recortes
