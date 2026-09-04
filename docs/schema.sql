-- ============================================================
-- ms-residentes | Esquema inicial (MySQL)
-- ANDAMIAJE: columnas orientativas, ajustar en la fase de diseno.
-- ============================================================

CREATE DATABASE IF NOT EXISTS condominio_residentes
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE condominio_residentes;

-- ------------------------------------------------------------
-- Tabla: edificios
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS edificios (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    nombre      VARCHAR(120)  NOT NULL,
    direccion   VARCHAR(255)  NOT NULL,
    num_pisos   INT           NOT NULL DEFAULT 1,
    creado_en   TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla: unidades  (departamentos)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS unidades (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    edificio_id  BIGINT        NOT NULL,
    codigo       VARCHAR(20)   NOT NULL,   -- ej. "A-501"
    piso         INT           NOT NULL,
    area_m2      DECIMAL(8,2)  NOT NULL,
    creado_en    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_unidades_edificio
        FOREIGN KEY (edificio_id) REFERENCES edificios(id),
    CONSTRAINT uq_unidades_codigo UNIQUE (edificio_id, codigo)
) ENGINE=InnoDB;

-- ------------------------------------------------------------
-- Tabla: residentes  (relacionada con unidades)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS residentes (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    unidad_id   BIGINT       NOT NULL,
    nombres     VARCHAR(120) NOT NULL,
    apellidos   VARCHAR(120) NOT NULL,
    documento   VARCHAR(20)  NOT NULL,
    email       VARCHAR(160),
    telefono    VARCHAR(30),
    tipo        ENUM('PROPIETARIO','INQUILINO') NOT NULL DEFAULT 'PROPIETARIO',
    activo      BOOLEAN      NOT NULL DEFAULT TRUE,
    creado_en   TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_residentes_unidad
        FOREIGN KEY (unidad_id) REFERENCES unidades(id),
    CONSTRAINT uq_residentes_documento UNIQUE (documento)
) ENGINE=InnoDB;

CREATE INDEX idx_unidades_edificio  ON unidades(edificio_id);
CREATE INDEX idx_residentes_unidad  ON residentes(unidad_id);
