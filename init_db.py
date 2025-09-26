"""
Inicialización de la base de datos PECSA en Render
Crea tablas y carga datos iniciales (roles, colaboradores, usuarios).
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

# Obtener conexión desde variable de entorno DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("❌ No se encontró DATABASE_URL en las variables de entorno.")

schema_sql = """
-- CREACIÓN DE ESQUEMA
DROP TABLE IF EXISTS user_roles CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS collaborators CASCADE;
DROP TABLE IF EXISTS roles CASCADE;

CREATE TABLE collaborators (
    id SERIAL PRIMARY KEY,
    document_number VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    position VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    collaborator_id INTEGER UNIQUE REFERENCES collaborators(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, role_id)
);
"""

data_sql = """
-- ROLES
INSERT INTO roles (name, description, permissions) VALUES
('Administrador', 'Control total del sistema', 'all'),
('Ventas', 'Gestión de ventas y clientes', 'sales_read,sales_write,customers_read'),
('Compras', 'Gestión de compras y proveedores', 'purchases_read,purchases_write,suppliers_read,suppliers_write'),
('Finanzas', 'Gestión contable y financiera', 'finance_read,finance_write,reports_read');

-- COLABORADORES
INSERT INTO collaborators (document_number, first_name, last_name, position, phone, email) VALUES
('12345678', 'Carlos', 'Rodríguez', 'Gerente General', '999888777', 'carlos@pecsa.com'),
('87654321', 'María', 'López', 'Jefe de Ventas', '999777666', 'maria@pecsa.com'),
('11223344', 'Juan', 'Pérez', 'Jefe de Compras', '999666555', 'juan@pecsa.com'),
('44332211', 'Ana', 'García', 'Contador', '999555444', 'ana@pecsa.com');

-- USUARIOS CON HASHES BCRYPT (ya generados)
INSERT INTO users (username, password_hash, collaborator_id) VALUES
('admin',    '$2b$12$6kpU2tLRiLoP7FcPyf6a9O5MTTjONp4pwaAXtx4iSOqC27Zpuggeq', (SELECT id FROM collaborators WHERE document_number='12345678')),
('ventas',   '$2b$12$coSUq62S5WnI74ZlgoLaF.eUgq43OHhwDzWlH5MiFKa3T27TkPy8i', (SELECT id FROM collaborators WHERE document_number='87654321')),
('compras',  '$2b$12$4h8G6DQiLZhlJp3cYZxH9OJwHvnQw7R8UMql1dpJUKMClFDU53LCS', (SELECT id FROM collaborators WHERE document_number='11223344')),
('finanzas', '$2b$12$RSBBZhZ6UyxEGtA5umTfEuB09ceSGCfhJdN0Jd85nbopLpuuUklAi', (SELECT id FROM collaborators WHERE document_number='44332211'));

-- RELACIÓN USUARIO-ROLES
INSERT INTO user_roles (user_id, role_id) VALUES
((SELECT id FROM users WHERE username='admin'), (SELECT id FROM roles WHERE name='Administrador')),
((SELECT id FROM users WHERE username='ventas'), (SELECT id FROM roles WHERE name='Ventas')),
((SELECT id FROM users WHERE username='compras'), (SELECT id FROM roles WHERE name='Compras')),
((SELECT id FROM users WHERE username='finanzas'), (SELECT id FROM roles WHERE name='Finanzas'));
"""

def run_sql(conn, sql):
    with conn.cursor() as cursor:
        cursor.execute(sql)
    conn.commit()

def main():
    print("🗄️ Iniciando base de datos en Render...")
    conn = psycopg2.connect(DATABASE_URL)
    try:
        run_sql(conn, schema_sql)
        run_sql(conn, data_sql)
        print("✅ Tablas y datos iniciales creados correctamente")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
