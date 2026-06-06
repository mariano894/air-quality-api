-- ============================================================
-- Air Quality API — Schema MySQL
-- Base de datos: airquality_db
-- ============================================================

CREATE DATABASE IF NOT EXISTS airquality_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE airquality_db;

-- Usuario de la aplicación (ajusta la contraseña)
CREATE USER IF NOT EXISTS 'airquality_user'@'%' IDENTIFIED BY 'changeme';
GRANT SELECT, INSERT, UPDATE, DELETE ON airquality_db.* TO 'airquality_user'@'%';
FLUSH PRIVILEGES;

-- ─── Tabla de mediciones ─────────────────────────────────────────────────────
-- Se permiten múltiples registros por fecha (distintas lecturas del mismo día).
-- El promedio diario se calcula en la capa de aplicación (endpoint by-date).
CREATE TABLE IF NOT EXISTS measurements (
    id          INT             NOT NULL AUTO_INCREMENT,
    date        DATE            NOT NULL                    COMMENT 'Fecha de la medición (múltiples por día permitidas)',
    pm25        DECIMAL(8,2)    NULL                        COMMENT 'PM2.5 µg/m³',
    pm10        DECIMAL(8,2)    NULL                        COMMENT 'PM10 µg/m³',
    o3          DECIMAL(8,2)    NULL                        COMMENT 'Ozono O3 ppb',
    source      VARCHAR(100)    NULL DEFAULT 'US Embassy Guatemala City',
    created_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    PRIMARY KEY (id),
    INDEX idx_measurements_date   (date),
    INDEX idx_measurements_pm25   (pm25),
    INDEX idx_measurements_year   ((YEAR(date))),
    INDEX idx_measurements_month  ((MONTH(date)))
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci
  COMMENT='Mediciones de calidad del aire — Embajada EE.UU. Guatemala City';


-- ─── Migración desde esquema anterior (si ya existe la tabla) ────────────────
-- Ejecutar solo si se está migrando desde la versión anterior con UNIQUE en date:
--
-- ALTER TABLE measurements DROP INDEX uq_measurements_date;
