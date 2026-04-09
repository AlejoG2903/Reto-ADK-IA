-- 001_create_tables.sql
CREATE TABLE IF NOT EXISTS pacientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    documento VARCHAR(20) UNIQUE NOT NULL,
    fecha_nacimiento DATE,
    telefono VARCHAR(20),
    email VARCHAR(255),
    direccion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS diagnosticos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    codigo VARCHAR(10) UNIQUE NOT NULL,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consultas (
    id SERIAL PRIMARY KEY,
    paciente_id INTEGER NOT NULL REFERENCES pacientes(id),
    fecha_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    turno VARCHAR(50),
    motivo TEXT,
    notas TEXT,
    profesional VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consulta_diagnosticos (
    id SERIAL PRIMARY KEY,
    consulta_id INTEGER NOT NULL REFERENCES consultas(id),
    diagnostico_id INTEGER NOT NULL REFERENCES diagnosticos(id),
    principal BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS medicamentos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    presentacion VARCHAR(100),
    stock_actual INTEGER NOT NULL,
    stock_minimo INTEGER NOT NULL,
    precio DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS consumos (
    id SERIAL PRIMARY KEY,
    consulta_id INTEGER NOT NULL REFERENCES consultas(id),
    medicamento_id INTEGER NOT NULL REFERENCES medicamentos(id),
    cantidad INTEGER NOT NULL,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_consultas_paciente_id ON consultas(paciente_id);
CREATE INDEX IF NOT EXISTS idx_consultas_fecha ON consultas(fecha_consulta);
CREATE INDEX IF NOT EXISTS idx_consulta_diagnosticos_consulta ON consulta_diagnosticos(consulta_id);
CREATE INDEX IF NOT EXISTS idx_consumos_consulta ON consumos(consulta_id);
