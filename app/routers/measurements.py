from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from app.database import get_db
from app import crud, schemas

router = APIRouter()


# ─── GET endpoints ───────────────────────────────────────────────────────────

@router.get(
    "/measurements",
    response_model=schemas.MeasurementListOut,
    summary="Listar mediciones",
    description=(
        "Retorna el historial de mediciones individuales con paginación y "
        "filtros opcionales por rango de fechas, año y mes."
    ),
)
def list_measurements(
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(50, ge=1, le=500, description="Registros por página (máx. 500)"),
    date_from: Optional[date] = Query(None, description="Fecha inicio del rango (YYYY-MM-DD)"),
    date_to: Optional[date] = Query(None, description="Fecha fin del rango (YYYY-MM-DD)"),
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Filtrar por año"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Filtrar por mes (1-12)"),
    db: Session = Depends(get_db),
):
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="date_from no puede ser mayor que date_to.",
        )

    skip = (page - 1) * page_size
    total, records = crud.get_measurements(
        db, skip=skip, limit=page_size,
        date_from=date_from, date_to=date_to,
        year=year, month=month,
    )

    results = [schemas.MeasurementOut.from_orm_with_aqi(r) for r in records]
    return schemas.MeasurementListOut(
        total=total, page=page, page_size=page_size, results=results
    )


@router.get(
    "/measurements/by-date/{measurement_date}",
    response_model=schemas.DailyAverageOut,
    summary="Promedio diario por fecha",
    description=(
        "Retorna el promedio de PM2.5, PM10 y O3 calculado sobre todos los "
        "registros existentes para la fecha indicada, junto con la cantidad "
        "de mediciones que componen el cálculo."
    ),
)
def get_daily_average_by_date(measurement_date: date, db: Session = Depends(get_db)):
    result = crud.get_daily_average(db, measurement_date)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existen mediciones para la fecha {measurement_date}.",
        )
    from app.schemas import _pm25_aqi_category
    result["pm25_category"] = _pm25_aqi_category(result["pm25_avg"])
    return schemas.DailyAverageOut(**result)


@router.get(
    "/measurements/{measurement_id}",
    response_model=schemas.MeasurementOut,
    summary="Obtener medición individual por ID",
)
def get_measurement(measurement_id: int, db: Session = Depends(get_db)):
    record = crud.get_measurement_by_id(db, measurement_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medición con ID {measurement_id} no encontrada.",
        )
    return schemas.MeasurementOut.from_orm_with_aqi(record)


# ─── POST endpoints ──────────────────────────────────────────────────────────

@router.post(
    "/measurements",
    response_model=schemas.MeasurementOut,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una medición",
    description=(
        "Inserta una nueva medición. Se permiten múltiples registros "
        "para la misma fecha (distintas lecturas del día)."
    ),
)
def create_measurement(
    payload: schemas.MeasurementCreate,
    db: Session = Depends(get_db),
):
    record = crud.create_measurement(db, payload)
    return schemas.MeasurementOut.from_orm_with_aqi(record)


@router.post(
    "/measurements/bulk",
    response_model=schemas.BulkInsertResult,
    status_code=status.HTTP_201_CREATED,
    summary="Inserción masiva de mediciones",
    description=(
        "Permite insertar hasta 500 mediciones en una sola solicitud. "
        "Se aceptan múltiples registros con la misma fecha."
    ),
)
def bulk_create_measurements(
    payload: schemas.MeasurementBulkCreate,
    db: Session = Depends(get_db),
):
    inserted = crud.bulk_create_measurements(db, payload.measurements)
    return schemas.BulkInsertResult(
        inserted=inserted,
        message=f"{inserted} registro(s) insertado(s) correctamente.",
    )


# ─── PUT endpoint ────────────────────────────────────────────────────────────

@router.put(
    "/measurements/{measurement_id}",
    response_model=schemas.MeasurementOut,
    summary="Actualizar medición",
)
def update_measurement(
    measurement_id: int,
    payload: schemas.MeasurementCreate,
    db: Session = Depends(get_db),
):
    record = crud.update_measurement(db, measurement_id, payload)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medición con ID {measurement_id} no encontrada.",
        )
    return schemas.MeasurementOut.from_orm_with_aqi(record)


# ─── DELETE endpoint ─────────────────────────────────────────────────────────

@router.delete(
    "/measurements/{measurement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar medición",
)
def delete_measurement(measurement_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_measurement(db, measurement_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Medición con ID {measurement_id} no encontrada.",
        )
