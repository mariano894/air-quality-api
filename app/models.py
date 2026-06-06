from sqlalchemy import Column, Integer, Float, Date, DateTime, String, func
from app.database import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(Date, nullable=False, index=True, comment="Fecha de medición (YYYY-MM-DD)")
    pm25 = Column(Float, nullable=True, comment="Material particulado fino PM2.5 (µg/m³)")
    pm10 = Column(Float, nullable=True, comment="Material particulado grueso PM10 (µg/m³)")
    o3 = Column(Float, nullable=True, comment="Ozono troposférico O3 (ppb)")
    source = Column(String(100), nullable=True, default="US Embassy Guatemala City", comment="Fuente de los datos")
    created_at = Column(DateTime, server_default=func.now(), comment="Fecha de inserción del registro")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment="Última actualización")
