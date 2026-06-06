from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime


# ─── AQI helpers ────────────────────────────────────────────────────────────

def _pm25_aqi_category(value: Optional[float]) -> Optional[str]:
    if value is None:
        return None
    if value <= 12:
        return "Bueno"
    if value <= 35.4:
        return "Moderado"
    if value <= 55.4:
        return "Insalubre para grupos sensibles"
    if value <= 150.4:
        return "Insalubre"
    if value <= 250.4:
        return "Muy insalubre"
    return "Peligroso"


# ─── Request schemas ─────────────────────────────────────────────────────────

class MeasurementCreate(BaseModel):
    date: date = Field(..., description="Fecha de la medición (YYYY-MM-DD)")
    pm25: Optional[float] = Field(None, ge=0, le=1000, description="PM2.5 en µg/m³")
    pm10: Optional[float] = Field(None, ge=0, le=1000, description="PM10 en µg/m³")
    o3: Optional[float] = Field(None, ge=0, le=1000, description="Ozono O3 en ppb")
    source: Optional[str] = Field("US Embassy Guatemala City", max_length=100)

    @field_validator("date")
    @classmethod
    def date_not_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("La fecha no puede ser futura.")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2025-06-01",
                "pm25": 28.5,
                "pm10": 45.0,
                "o3": 12.0,
                "source": "US Embassy Guatemala City",
            }
        }
    }


class MeasurementBulkCreate(BaseModel):
    measurements: List[MeasurementCreate] = Field(..., min_length=1, max_length=500)


# ─── Response schemas ────────────────────────────────────────────────────────

class MeasurementOut(BaseModel):
    id: int
    date: date
    pm25: Optional[float]
    pm10: Optional[float]
    o3: Optional[float]
    source: Optional[str]
    pm25_category: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm_with_aqi(cls, obj) -> "MeasurementOut":
        data = MeasurementOut.model_validate(obj)
        data.pm25_category = _pm25_aqi_category(obj.pm25)
        return data

    model_config = {"from_attributes": True}


class MeasurementListOut(BaseModel):
    total: int
    page: int
    page_size: int
    results: List[MeasurementOut]


class DailyAverageOut(BaseModel):
    date: date
    total_records: int
    pm25_avg: Optional[float] = Field(None, description="Promedio PM2.5 µg/m³")
    pm10_avg: Optional[float] = Field(None, description="Promedio PM10 µg/m³")
    o3_avg: Optional[float] = Field(None, description="Promedio O3 ppb")
    pm25_category: Optional[str] = Field(None, description="Categoría AQI basada en promedio PM2.5")

    model_config = {
        "json_schema_extra": {
            "example": {
                "date": "2025-06-01",
                "total_records": 3,
                "pm25_avg": 31.2,
                "pm10_avg": 48.7,
                "o3_avg": 11.0,
                "pm25_category": "Moderado",
            }
        }
    }


class BulkInsertResult(BaseModel):
    inserted: int
    message: str
