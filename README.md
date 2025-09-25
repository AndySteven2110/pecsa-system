# Sistema de Información PECSA - Grifo

## 📋 Descripción
Sistema de gestión integral para el grifo PECSA, desarrollado con Streamlit y PostgreSQL.
Este es el Sprint 1 que incluye la gestión de usuarios, colaboradores, roles y control de accesos.

## 🚀 Instalación en Google Colab

### Paso 1: Ejecutar las celdas en orden
1. **Celda 1**: Instalación de dependencias y PostgreSQL
2. **Celda 2**: Creación del esquema de base de datos
3. **Celda 3**: Inserción de datos iniciales
4. **Celda 4**: Creación de módulos del sistema
5. **Celda 5**: Creación de la aplicación Streamlit
6. **Celda 6**: Archivos de configuración
7. **Celda 7**: Configuración de ngrok
8. **Celda 8**: Iniciar la aplicación

## 👤 Usuarios de Prueba

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| admin | Admin123! | Administrador |
| ventas | Ventas123! | Ventas |
| compras | Compras123! | Compras |
| finanzas | Finanzas123! | Finanzas |

## 🛠️ Funcionalidades Implementadas

### Módulo de Administración
- **Gestión de Colaboradores**: CRUD completo
- **Gestión de Usuarios**: Crear, modificar, desactivar usuarios
- **Gestión de Roles**: Definir roles y permisos
- **Asignación de Roles**: Asignar múltiples roles a usuarios

### Seguridad
- Autenticación con bcrypt
- Control de accesos basado en roles
- Validación de formularios
- Manejo de sesiones

## 📁 Estructura del Proyecto
/content/pecsa_system/
├── app.py           # Aplicación principal Streamlit
├── database.py      # Conexión y gestión de BD
├── auth.py         # Autenticación y autorización
└── models.py       # Modelos CRUD


## 🔧 Tecnologías Utilizadas
- **Frontend**: Streamlit
- **Backend**: Python 3
- **Base de Datos**: PostgreSQL
- **Seguridad**: bcrypt
- **Exposición**: ngrok

## 📊 Base de Datos
- **collaborators**: Información de colaboradores
- **users**: Usuarios del sistema
- **roles**: Roles disponibles
- **user_roles**: Relación usuarios-roles

## 🚦 Estado del Proyecto
✅ Sprint 1 - Completado
- Gestión de usuarios y accesos
- Sistema base funcionando

## 📝 Notas de Desarrollo
- Código modular y comentado en español
- Cumple con PEP8
- Manejo de errores implementado
- Interfaz responsiva y amigable

## 👨‍💻 Autor
Sistema desarrollado para PECSA - 2024
