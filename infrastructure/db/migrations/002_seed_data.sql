-- Pacientes (Aseguramos que existan)
INSERT INTO pacientes (id, nombre, documento, fecha_nacimiento) VALUES
(1, 'Juan Perez', 'DOC001', '1990-05-10'),
(2, 'Maria Lopez', 'DOC002', '1985-08-22'),
(3, 'Carlos Gomez', 'DOC003', '2000-01-15'),
(4, 'Ana Martinez', 'DOC004', '1995-11-30')
ON CONFLICT (id) DO UPDATE SET nombre = EXCLUDED.nombre, documento = EXCLUDED.documento;

-- Diagnósticos (Aseguramos que existan)
INSERT INTO diagnosticos (id, nombre, codigo) VALUES
(1, 'Hipertensión Arterial', 'I10'),
(2, 'Diabetes Mellitus Tipo 2', 'E11'),
(3, 'Gripe Común', 'J00'),
(4, 'Migraña Crónica', 'G43.1')
ON CONFLICT (id) DO UPDATE SET nombre = EXCLUDED.nombre, codigo = EXCLUDED.codigo;

-- Medicamentos (Aseguramos que existan y reseteamos stock)
INSERT INTO medicamentos (id, nombre, stock_actual, stock_minimo) VALUES
(1, 'Losartán', 100, 30),
(2, 'Metformina', 50, 25),
(3, 'Ibuprofeno', 200, 50),
(4, 'Acetaminofén', 300, 50)
ON CONFLICT (id) DO UPDATE SET stock_actual = EXCLUDED.stock_actual, stock_minimo = EXCLUDED.stock_minimo;

-- BORRADO DE DATOS ANTERIORES PARA EVITAR CONFLICTOS DE ID
TRUNCATE TABLE consultas, consulta_diagnosticos, consumos RESTART IDENTITY;

-- DATOS DE PRUEBA PARA 2026-04-13

-- Turno Manana (2 pacientes)
INSERT INTO consultas (id, paciente_id, fecha_consulta, turno, notas) VALUES
(1, 1, '2026-04-13 08:30:00', 'Manana', 'Control de presión arterial.'),
(2, 2, '2026-04-13 10:15:00', 'Manana', 'Revisión de niveles de glucosa.');

INSERT INTO consulta_diagnosticos (consulta_id, diagnostico_id, principal) VALUES
(1, 1, TRUE), -- Juan Perez -> Hipertensión
(2, 2, TRUE); -- Maria Lopez -> Diabetes

INSERT INTO consumos (consulta_id, medicamento_id, cantidad) VALUES
(1, 1, 10), -- Juan Perez consume Losartán
(2, 2, 5);  -- Maria Lopez consume Metformina

-- Turno Tarde (3 pacientes)
INSERT INTO consultas (id, paciente_id, fecha_consulta, turno, notas) VALUES
(3, 3, '2026-04-13 15:00:00', 'Tarde', 'Paciente con síntomas de gripe.'),
(4, 1, '2026-04-13 16:45:00', 'Tarde', 'Seguimiento de hipertensión.'),
(5, 4, '2026-04-13 18:20:00', 'Tarde', 'Dolor de cabeza persistente.');

INSERT INTO consulta_diagnosticos (consulta_id, diagnostico_id, principal) VALUES
(3, 3, TRUE), -- Carlos Gomez -> Gripe
(4, 1, TRUE), -- Juan Perez -> Hipertensión
(5, 4, TRUE); -- Ana Martinez -> Migraña

INSERT INTO consumos (consulta_id, medicamento_id, cantidad) VALUES
(3, 4, 20), -- Carlos Gomez consume Acetaminofén
(5, 3, 15); -- Ana Martinez consume Ibuprofeno

-- Turno Noche (1 paciente)
INSERT INTO consultas (id, paciente_id, fecha_consulta, turno, notas) VALUES
(6, 2, '2026-04-13 21:00:00', 'Noche', 'Consulta de urgencia por malestar general.');

INSERT INTO consulta_diagnosticos (consulta_id, diagnostico_id, principal) VALUES
(6, 2, TRUE); -- Maria Lopez -> Diabetes

INSERT INTO consumos (consulta_id, medicamento_id, cantidad) VALUES
(6, 2, 5); -- Maria Lopez consume Metformina