-- ============================================================
-- ms-residentes | Datos de prueba para el avance del 50%
-- ============================================================
-- 16 filas legibles: 2 edificios, 6 unidades, 8 residentes.
-- Las 4 cuentas de usuario viven en el seed de ms-usuarios.
-- Postgres ejecuta este archivo despues de 01-schema.sql.
-- ============================================================

-- ---------- edificios (2) ----------
INSERT INTO edificios (nombre, direccion, num_pisos) VALUES
  ('Torre Norte', 'Av. Javier Prado Este 1234, San Isidro', 12),
  ('Torre Sur',   'Av. Javier Prado Este 1240, San Isidro', 10);

-- ---------- unidades (6) ----------
INSERT INTO unidades (edificio_id, codigo, piso, area_m2) VALUES
  (1, 'A-101', 1,  78.50),
  (1, 'A-502', 5,  92.00),
  (1, 'A-1201', 12, 145.75),
  (2, 'B-201', 2,  65.00),
  (2, 'B-305', 3,  88.25),
  (2, 'B-1001', 10, 130.00);

-- ---------- residentes (8) ----------
INSERT INTO residentes (unidad_id, nombres, apellidos, documento, email, telefono, tipo) VALUES
  (1, 'Lucia',   'Vargas Rojas',    '45781230', 'lucia.vargas@example.com',   '987654321', 'PROPIETARIO'),
  (1, 'Andres',  'Vargas Rojas',    '45781231', 'andres.vargas@example.com',  '987654322', 'PROPIETARIO'),
  (2, 'Marcela', 'Quispe Huaman',   '41023987', 'marcela.quispe@example.com', '987654323', 'INQUILINO'),
  (3, 'Ricardo', 'Salazar Pinto',   '09876543', 'ricardo.salazar@example.com','987654324', 'PROPIETARIO'),
  (4, 'Teresa',  'Ampuero Diaz',    '43219876', 'teresa.ampuero@example.com', '987654325', 'PROPIETARIO'),
  (5, 'Joaquin', 'Beltran Cordova', '47654321', 'joaquin.beltran@example.com','987654326', 'INQUILINO'),
  (5, 'Paula',   'Beltran Cordova', '47654322', 'paula.beltran@example.com',  '987654327', 'INQUILINO'),
  (6, 'Ernesto', 'Ferreyra Luna',   '10293847', 'ernesto.ferreyra@example.com','987654328','PROPIETARIO');
