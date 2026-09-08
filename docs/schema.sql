-- ============================================================
-- ms-residentes | Esquema inicial (PostgreSQL 16)
-- ANDAMIAJE: columnas orientativas, ajustar en la fase de diseno.
-- ============================================================

-- CREATE DATABASE condominio_residentes;
-- \c condominio_residentes

-- ------------------------------------------------------------
-- Tabla: edificios
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS edificios (
    id          BIGSERIAL PRIMARY KEY,
    nombre      VARCHAR(120)  NOT NULL,
    direccion   VARCHAR(255)  NOT NULL,
    num_pisos   INT           NOT NULL DEFAULT 1,
    creado_en   TIMESTAMP     NOT NULL DEFAULT NOW()
);

-- ------------------------------------------------------------
-- Tabla: unidades  (departamentos)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS unidades (
    id           BIGSERIAL PRIMARY KEY,
    edificio_id  BIGINT        NOT NULL,
    codigo       VARCHAR(20)   NOT NULL,   -- ej. 'A-501'
    piso         INT           NOT NULL,
    area_m2      NUMERIC(8,2)  NOT NULL,
    creado_en    TIMESTAMP     NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_unidades_edificio
        FOREIGN KEY (edificio_id) REFERENCES edificios(id),
    CONSTRAINT uq_unidades_codigo UNIQUE (edificio_id, codigo)
);

-- ------------------------------------------------------------
-- Tabla: residentes  (relacionada con unidades)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS residentes (
    id          BIGSERIAL PRIMARY KEY,
    unidad_id   BIGINT       NOT NULL,
    nombres     VARCHAR(120) NOT NULL,
    apellidos   VARCHAR(120) NOT NULL,
    documento   VARCHAR(20)  NOT NULL,
    email       VARCHAR(160),
    telefono    VARCHAR(30),
    tipo        VARCHAR(20)  NOT NULL DEFAULT 'PROPIETARIO',
    activo      BOOLEAN      NOT NULL DEFAULT TRUE,
    creado_en   TIMESTAMP    NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_residentes_unidad
        FOREIGN KEY (unidad_id) REFERENCES unidades(id),
    CONSTRAINT uq_residentes_documento UNIQUE (documento),
    CONSTRAINT ck_residentes_tipo CHECK (tipo IN ('PROPIETARIO', 'INQUILINO'))
);

-- ------------------------------------------------------------
-- NOTA: la tabla `usuarios` ya no vive aca.
-- Las cuentas de acceso (register / login) son del microservicio ms-usuarios,
-- que tiene su propia base `condominio_usuarios`. Alla, `residente_id` apunta
-- a los ids de esta tabla `residentes` como identificador logico.
-- ------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_unidades_edificio   ON unidades(edificio_id);
CREATE INDEX IF NOT EXISTS idx_residentes_unidad   ON residentes(unidad_id);
