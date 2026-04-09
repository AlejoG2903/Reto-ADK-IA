-- Pacientes
INSERT INTO pacientes (nombre, documento, fecha_nacimiento) VALUES
('Juan Perez', 'DOC001', '1990-05-10'),
('Maria Lopez', 'DOC002', '1985-08-22'),
('Carlos Gomez', 'DOC003', '2000-01-15')
ON CONFLICT DO NOTHING;

-- Diagnosticos
INSERT INTO diagnosticos (nombre, codigo) VALUES
('Gripe', 'J10'),
('COVID-19', 'U07.1'),
('Dengue', 'A90'),
('Migrana', 'G43')
ON CONFLICT DO NOTHING;

-- Medicamentos
INSERT INTO medicamentos (nombre, stock_actual, stock_minimo) VALUES
('Paracetamol', 100, 20),
('Ibuprofeno', 10, 20),
('Amoxicilina', 0, 15)
ON CONFLICT DO NOTHING;

-- Consultas de hoy
INSERT INTO consultas (paciente_id, fecha_consulta, turno, notas) VALUES
(1, NOW(), 'manana', 'Consulta general'),
(2, NOW(), 'tarde', 'Fiebre alta'),
(3, NOW(), 'noche', 'Dolor de cabeza'),
(1, NOW(), 'manana', 'Control'),
(2, NOW(), 'tarde', 'Seguimiento'),
(3, NOW(), 'noche', 'Sintomas virales'),
(1, NOW(), 'manana', 'Revision'),
(2, NOW(), 'tarde', 'Chequeo');

-- Relacion consulta-diagnosticos
INSERT INTO consulta_diagnosticos (consulta_id, diagnostico_id, principal) VALUES
(1, 1, TRUE), (2, 1, TRUE), (3, 1, TRUE), (4, 1, TRUE),
(5, 2, TRUE), (6, 2, TRUE),
(7, 3, TRUE),
(8, 4, TRUE);

-- Consumos de medicamentos en consultas
INSERT INTO consumos (consulta_id, medicamento_id, cantidad) VALUES
(1, 1, 2), (2, 1, 2), (3, 2, 1), (4, 1, 2),
(5, 3, 1), (6, 3, 1), (7, 2, 1), (8, 2, 1),
(1, 2, 1), (2, 2, 1)
ON CONFLICT DO NOTHING;