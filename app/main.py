from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import measurements

# Crear tablas al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Air Quality API - Guatemala City",
    description=(
        "API pública para consultar y registrar mediciones de calidad del aire "
        "de la Embajada de EE.UU. en Ciudad de Guatemala. "
        "Contaminantes monitoreados: PM2.5, PM10 y O3."
    ),
    version="1.0.0",
    contact={
        "name": "Air Quality Monitor GT",
        "email": "admin@airquality.gt",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS abierto para uso público
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(measurements.router, prefix="/api/v1", tags=["Mediciones"])


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "Air Quality API - Guatemala City",
        "status": "online",
        "docs": "/docs",
        "version": "1.0.0",
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}
