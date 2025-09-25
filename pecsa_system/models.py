"""
Módulo de modelos y operaciones CRUD
Sistema de Información PECSA
"""

from database import execute_query, get_db_cursor
from auth import hash_password
from datetime import datetime

# ============================================
# MODELO: Colaboradores
# ============================================

class CollaboratorModel:
    @staticmethod
    def get_all(status=None):
        """Obtiene todos los colaboradores"""
        query = "SELECT * FROM collaborators"
        params = []
        if status:
            query += " WHERE status = %s"
            params.append(status)
        query += " ORDER BY last_name, first_name"
        return execute_query(query, params if params else None, fetch_all=True)

    @staticmethod
    def get_by_id(collaborator_id):
        """Obtiene un colaborador por ID"""
        query = "SELECT * FROM collaborators WHERE id = %s"
        return execute_query(query, (collaborator_id,), fetch_one=True)

    @staticmethod
    def get_by_document(document_number):
        """Obtiene un colaborador por número de documento"""
        query = "SELECT * FROM collaborators WHERE document_number = %s"
        return execute_query(query, (document_number,), fetch_one=True)

    @staticmethod
    def create(data):
        """Crea un nuevo colaborador"""
        query = """
            INSERT INTO collaborators (document_number, first_name, last_name,
                                     position, phone, email, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        params = (
            data['document_number'], data['first_name'], data['last_name'],
            data['position'], data.get('phone'), data.get('email'),
            data.get('status', 'active')
        )
        return execute_query(query, params, fetch_one=True)

    @staticmethod
    def update(collaborator_id, data):
        """Actualiza un colaborador"""
        query = """
            UPDATE collaborators
            SET first_name = %s, last_name = %s, position = %s,
                phone = %s, email = %s, status = %s, updated_at = %s
            WHERE id = %s
        """
        params = (
            data['first_name'], data['last_name'], data['position'],
            data.get('phone'), data.get('email'), data.get('status', 'active'),
            datetime.now(), collaborator_id
        )
        execute_query(query, params)
        return True

    @staticmethod
    def delete(collaborator_id):
        """Elimina un colaborador (cambio de estado)"""
        query = "UPDATE collaborators SET status = 'inactive', updated_at = %s WHERE id = %s"
        execute_query(query, (datetime.now(), collaborator_id))
        return True

# ============================================
# MODELO: Usuarios
# ============================================

class UserModel:
    @staticmethod
    def get_all():
        """Obtiene todos los usuarios con información del colaborador"""
        query = """
            SELECT u.*, c.first_name, c.last_name, c.document_number, c.position,
                   array_agg(r.name) as roles
            FROM users u
            JOIN collaborators c ON u.collaborator_id = c.id
            LEFT JOIN user_roles ur ON u.id = ur.user_id
            LEFT JOIN roles r ON ur.role_id = r.id
            GROUP BY u.id, c.first_name, c.last_name, c.document_number, c.position
            ORDER BY c.last_name, c.first_name
        """
        return execute_query(query, fetch_all=True)

    @staticmethod
    def get_by_id(user_id):
        """Obtiene un usuario por ID"""
        query = """
            SELECT u.*, c.first_name, c.last_name, c.document_number, c.position
            FROM users u
            JOIN collaborators c ON u.collaborator_id = c.id
            WHERE u.id = %s
        """
        return execute_query(query, (user_id,), fetch_one=True)

    @staticmethod
    def get_by_username(username):
        """Obtiene un usuario por nombre de usuario"""
        query = "SELECT * FROM users WHERE username = %s"
        return execute_query(query, (username,), fetch_one=True)

    @staticmethod
    def create(data):
        """Crea un nuevo usuario"""
        query = """
            INSERT INTO users (username, password_hash, collaborator_id, is_active)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        password_hash = hash_password(data['password'])
        params = (
            data['username'], password_hash, data['collaborator_id'],
            data.get('is_active', True)
        )
        return execute_query(query, params, fetch_one=True)

    @staticmethod
    def update(user_id, data):
        """Actualiza un usuario"""
        with get_db_cursor() as cursor:
            if 'password' in data and data['password']:
                query = """
                    UPDATE users
                    SET username = %s, password_hash = %s, is_active = %s, updated_at = %s
                    WHERE id = %s
                """
                params = (
                    data['username'], hash_password(data['password']),
                    data.get('is_active', True), datetime.now(), user_id
                )
            else:
                query = """
                    UPDATE users
                    SET username = %s, is_active = %s, updated_at = %s
                    WHERE id = %s
                """
                params = (
                    data['username'], data.get('is_active', True),
                    datetime.now(), user_id
                )

            cursor.execute(query, params)
        return True

    @staticmethod
    def delete(user_id):
        """Elimina un usuario"""
        query = "DELETE FROM users WHERE id = %s"
        execute_query(query, (user_id,))
        return True

    @staticmethod
    def deactivate(user_id):
        """Desactiva un usuario"""
        query = "UPDATE users SET is_active = false, updated_at = %s WHERE id = %s"
        execute_query(query, (datetime.now(), user_id))
        return True

# ============================================
# MODELO: Roles
# ============================================

class RoleModel:
    @staticmethod
    def get_all():
        """Obtiene todos los roles"""
        query = """
            SELECT r.*, COUNT(ur.user_id) as user_count
            FROM roles r
            LEFT JOIN user_roles ur ON r.id = ur.role_id
            GROUP BY r.id
            ORDER BY r.name
        """
        return execute_query(query, fetch_all=True)

    @staticmethod
    def get_by_id(role_id):
        """Obtiene un rol por ID"""
        query = "SELECT * FROM roles WHERE id = %s"
        return execute_query(query, (role_id,), fetch_one=True)

    @staticmethod
    def get_by_name(name):
        """Obtiene un rol por nombre"""
        query = "SELECT * FROM roles WHERE name = %s"
        return execute_query(query, (name,), fetch_one=True)

    @staticmethod
    def create(data):
        """Crea un nuevo rol"""
        query = """
            INSERT INTO roles (name, description, permissions)
            VALUES (%s, %s, %s)
            RETURNING id
        """
        params = (
            data['name'], data.get('description'), data.get('permissions')
        )
        return execute_query(query, params, fetch_one=True)

    @staticmethod
    def update(role_id, data):
        """Actualiza un rol"""
        query = """
            UPDATE roles
            SET name = %s, description = %s, permissions = %s, updated_at = %s
            WHERE id = %s
        """
        params = (
            data['name'], data.get('description'), data.get('permissions'),
            datetime.now(), role_id
        )
        execute_query(query, params)
        return True

    @staticmethod
    def delete(role_id):
        """Elimina un rol"""
        query = "DELETE FROM roles WHERE id = %s"
        execute_query(query, (role_id,))
        return True

# ============================================
# MODELO: Asignación de Roles
# ============================================

class UserRoleModel:
    @staticmethod
    def get_user_roles(user_id):
        """Obtiene los roles de un usuario"""
        query = """
            SELECT r.*, ur.assigned_at
            FROM roles r
            JOIN user_roles ur ON r.id = ur.role_id
            WHERE ur.user_id = %s
            ORDER BY r.name
        """
        return execute_query(query, (user_id,), fetch_all=True)

    @staticmethod
    def assign_role(user_id, role_id):
        """Asigna un rol a un usuario"""
        query = """
            INSERT INTO user_roles (user_id, role_id)
            VALUES (%s, %s)
            ON CONFLICT (user_id, role_id) DO NOTHING
        """
        execute_query(query, (user_id, role_id))
        return True

    @staticmethod
    def remove_role(user_id, role_id):
        """Remueve un rol de un usuario"""
        query = "DELETE FROM user_roles WHERE user_id = %s AND role_id = %s"
        execute_query(query, (user_id, role_id))
        return True

    @staticmethod
    def update_user_roles(user_id, role_ids):
        """Actualiza todos los roles de un usuario"""
        with get_db_cursor() as cursor:
            # Eliminar roles actuales
            cursor.execute("DELETE FROM user_roles WHERE user_id = %s", (user_id,))

            # Asignar nuevos roles
            for role_id in role_ids:
                cursor.execute(
                    "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
                    (user_id, role_id)
                )
        return True
