from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from typing import Optional, List
from datetime import date

from app.models import Measurement
from app.schemas import MeasurementCreate


def get_measurement_by_id(db: Session, measurement_id: int) -> Optional[Measurement]:
    return db.query(Measurement).filter(Measurement.id == measurement_id).first()


def get_measurements(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
) -> tuple[int, List[Measurement]]:
    query = db.query(Measurement)

    if date_from:
        query = query.filter(Measurement.fecha >= date_from)
    if date_to:
        query = query.filter(Measurement.fecha <= date_to)
    if year:
        query = query.filter(extract("year", Measurement.fecha) == year)
    if month:
        query = query.filter(extract("month", Measurement.fecha) == month)

    total = query.count()
    results = query.order_by(Measurement.fecha.desc()).offset(skip).limit(limit).all()
    return total, results


def get_daily_average(db: Session, measurement_date: date) -> Optional[dict]:
    """
    Retorna el promedio de PM2.5, PM10 y O3 para todos los registros
    de una fecha, junto con la cantidad de mediciones encontradas.
    Retorna None si no hay registros para esa fecha.
    """
    row = (
        db.query(
            func.count(Measurement.id).label("total_records"),
            func.avg(Measurement.pm25).label("pm25_avg"),
            func.avg(Measurement.pm10).label("pm10_avg"),
            func.avg(Measurement.o3).label("o3_avg"),
        )
        .filter(Measurement.fecha == measurement_date)
        .one()
    )

    if row.total_records == 0:
        return None

    def _round(val) -> Optional[float]:
        return round(float(val), 2) if val is not None else None

    return {
        "date": measurement_date,
        "total_records": row.total_records,
        "pm25_avg": _round(row.pm25_avg),
        "pm10_avg": _round(row.pm10_avg),
        "o3_avg": _round(row.o3_avg),
    }


def create_measurement(db: Session, data: MeasurementCreate) -> Measurement:
    obj = Measurement(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def bulk_create_measurements(db: Session, items: List[MeasurementCreate]) -> int:
    """Inserta múltiples registros. Permite fechas repetidas."""
    new_objects = [Measurement(**item.model_dump()) for item in items]
    db.bulk_save_objects(new_objects)
    db.commit()
    return len(new_objects)


def update_measurement(
    db: Session, measurement_id: int, data: MeasurementCreate
) -> Optional[Measurement]:
    obj = get_measurement_by_id(db, measurement_id)
    if not obj:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete_measurement(db: Session, measurement_id: int) -> bool:
    obj = get_measurement_by_id(db, measurement_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True
