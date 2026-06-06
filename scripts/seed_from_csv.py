"""
Script para importar el CSV histórico de calidad del aire a MySQL.

Uso:
    python scripts/seed_from_csv.py --csv data/us-embassy__guatemala_city__guatemala-air-quality.csv
"""
import sys
import os
import argparse
from datetime import datetime

# Agrega el directorio raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal, engine, Base
from app.models import Measurement


def parse_date(value: str):
    """Parsea fechas en formato YYYY/M/D o YYYY-MM-DD."""
    for fmt in ("%Y/%m/%d", "%Y-%m-%d", "%Y/%#m/%#d"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    # Último intento flexible
    parts = value.strip().replace("-", "/").split("/")
    if len(parts) == 3:
        return datetime(int(parts[0]), int(parts[1]), int(parts[2])).date()
    raise ValueError(f"Formato de fecha no reconocido: {value}")


def to_float_or_none(value) -> float | None:
    try:
        v = str(value).strip()
        return float(v) if v else None
    except (ValueError, TypeError):
        return None


def seed(csv_path: str, dry_run: bool = False):
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)

    df = pd.read_csv(csv_path)
    df.columns = [c.strip().lower() for c in df.columns]

    print(f"📂 CSV cargado: {len(df)} filas")
    print(f"   Columnas: {df.columns.tolist()}\n")

    db = SessionLocal()
    inserted = skipped = errors = 0

    try:
        for _, row in df.iterrows():
            try:
                measurement_date = parse_date(str(row["date"]))
            except ValueError as e:
                print(f"  ⚠️  Fecha inválida: {row['date']} — {e}")
                errors += 1
                continue

            # Verificar si ya existe
            existing = db.query(Measurement).filter(
                Measurement.date == measurement_date
            ).first()
            if existing:
                skipped += 1
                continue

            record = Measurement(
                date=measurement_date,
                pm25=to_float_or_none(row.get("pm25")),
                pm10=to_float_or_none(row.get("pm10")),
                o3=to_float_or_none(row.get("o3")),
                source="US Embassy Guatemala City",
            )

            if not dry_run:
                db.add(record)
            inserted += 1

        if not dry_run:
            db.commit()
            print(f"✅ Importación completada:")
        else:
            print(f"🔍 Dry-run completado (no se escribió nada):")

        print(f"   Insertados : {inserted}")
        print(f"   Omitidos   : {skipped} (duplicados)")
        print(f"   Errores    : {errors}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error durante la importación: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed air quality data from CSV")
    parser.add_argument("--csv", required=True, help="Ruta al archivo CSV")
    parser.add_argument("--dry-run", action="store_true", help="Solo simular, no escribir")
    args = parser.parse_args()
    seed(args.csv, dry_run=args.dry_run)
