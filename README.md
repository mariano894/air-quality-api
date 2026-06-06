# 🌫️ Air Quality API — Guatemala City

API pública construida con **FastAPI + MySQL** para consultar y registrar mediciones de calidad del aire de la Embajada de EE.UU. en Ciudad de Guatemala.

Contaminantes monitoreados: **PM2.5**, **PM10**, **O3 (Ozono)**.

---

## 📁 Estructura del proyecto

```
air-quality-api/
├── app/
│   ├── main.py          # Aplicación FastAPI + CORS
│   ├── config.py        # Variables de entorno (pydantic-settings)
│   ├── database.py      # Conexión MySQL + Session
│   ├── models.py        # Modelo SQLAlchemy (tabla measurements)
│   ├── schemas.py       # Schemas Pydantic request/response
│   ├── crud.py          # Operaciones de base de datos
│   └── routers/
│       └── measurements.py  # Todos los endpoints
├── scripts/
│   ├── schema.sql       # DDL para crear la BD y tabla
│   └── seed_from_csv.py # Importar CSV histórico
├── .env.example
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## 🚀 Inicio rápido con Docker

```bash
# 1. Clonar y entrar al proyecto
git clone <repo>
cd air-quality-api

# 2. Levantar MySQL + API
docker-compose up -d

# 3. Importar datos históricos del CSV
docker-compose exec api python scripts/seed_from_csv.py \
    --csv /ruta/al/us-embassy__guatemala_city__guatemala-air-quality.csv

# 4. Abrir documentación interactiva
open http://localhost:8000/docs
```

---

## ⚙️ Instalación manual

### Requisitos
- Python 3.12+
- MySQL 8.0+

### Pasos

```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales MySQL

# Crear BD y tabla
mysql -u root -p < scripts/schema.sql

# Importar CSV histórico
python scripts/seed_from_csv.py --csv ruta/al/archivo.csv

# Iniciar el servidor
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔌 Endpoints

### GET

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/v1/measurements` | Listar mediciones (paginado + filtros) |
| `GET` | `/api/v1/measurements/{id}` | Obtener por ID |
| `GET` | `/api/v1/measurements/by-date/{fecha}` | Obtener por fecha |

#### Parámetros de filtro (`GET /api/v1/measurements`)

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `page` | int | Número de página (default: 1) |
| `page_size` | int | Registros por página 1-500 (default: 50) |
| `date_from` | date | Fecha inicio del rango `YYYY-MM-DD` |
| `date_to` | date | Fecha fin del rango `YYYY-MM-DD` |
| `year` | int | Filtrar por año |
| `month` | int | Filtrar por mes (1-12) |

#### Ejemplo de respuesta

```json
{
  "total": 1541,
  "page": 1,
  "page_size": 50,
  "results": [
    {
      "id": 1,
      "date": "2025-06-01",
      "pm25": 28.5,
      "pm10": 45.0,
      "o3": 12.0,
      "source": "US Embassy Guatemala City",
      "pm25_category": "Moderado",
      "created_at": "2025-06-01T10:00:00",
      "updated_at": "2025-06-01T10:00:00"
    }
  ]
}
```

### POST

| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/measurements` | Registrar una medición |
| `POST` | `/api/v1/measurements/bulk` | Inserción masiva (hasta 500) |

#### Body `POST /api/v1/measurements`

```json
{
  "date": "2025-06-01",
  "pm25": 28.5,
  "pm10": 45.0,
  "o3": 12.0,
  "source": "US Embassy Guatemala City"
}
```

---

## 📊 Categorías AQI para PM2.5

| Rango µg/m³ | Categoría |
|-------------|-----------|
| 0 – 12 | Bueno |
| 12.1 – 35.4 | Moderado |
| 35.5 – 55.4 | Insalubre para grupos sensibles |
| 55.5 – 150.4 | Insalubre |
| 150.5 – 250.4 | Muy insalubre |
| > 250.5 | Peligroso |

---

## 🔒 Seguridad en producción

- Agregar **API Key** o **JWT** para los endpoints `POST`/`PUT`/`DELETE`
- Configurar rate limiting con `slowapi`
- Usar HTTPS con certificado SSL (nginx + Let's Encrypt)
- No exponer el puerto 3306 de MySQL públicamente
