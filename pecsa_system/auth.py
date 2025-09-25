"""
Módulo de autenticación y autorización
Sistema de Información PECSA
"""

import bcrypt
import streamlit as st
from datetime import datetime
from database import execute_query

def hash_password(password):
    """
    Genera un hash seguro para la contraseña
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, password_hash):
    """
    Verifica si la contraseña coincide con el hash
    """
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

def authenticate_user(username, password):
    """
    Autentica un usuario y retorna sus datos si es válido
    """
    query = """
        SELECT u.*, c.first_name, c.last_name, c.position, c.email,
               array_agg(r.name) as roles, array_agg(r.permissions) as permissions
        FROM users u
        JOIN collaborators c ON u.collaborator_id = c.id
        LEFT JOIN user_roles ur ON u.id = ur.user_id
        LEFT JOIN roles r ON ur.role_id = r.id
        WHERE u.username = %s AND u.is_active = true
        GROUP BY u.id, c.first_name, c.last_name, c.position, c.email
    """

    user = execute_query(query, (username,), fetch_one=True)

    if user and verify_password(password, user['password_hash']):
        # Actualizar último login
        update_query = "UPDATE users SET last_login = %s WHERE id = %s"
        execute_query(update_query, (datetime.now(), user['id']))
        return user

    return None

def login_user(username, password):
    """
    Realiza el proceso de login y maneja la sesión
    """
    user = authenticate_user(username, password)
    if user:
        st.session_state.logged_in = True
        st.session_state.user = user
        st.session_state.username = username
        st.session_state.user_roles = user['roles'] or []
        st.session_state.permissions = user['permissions'] or []
        return True
    return False

def logout_user():
    """
    Cierra la sesión del usuario
    """
    keys_to_remove = ['logged_in', 'user', 'username', 'user_roles', 'permissions']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]

def is_admin():
    """
    Verifica si el usuario actual es administrador
    """
    return 'Administrador' in st.session_state.get('user_roles', [])

def has_permission(permission):
    """
    Verifica si el usuario tiene un permiso específico
    """
    if is_admin():
        return True

    permissions = st.session_state.get('permissions', [])
    for perm_list in permissions:
        if perm_list and permission in perm_list:
            return True
    return False

def require_login():
    """
    Decorator para requerir login en páginas
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not st.session_state.get('logged_in', False):
                st.warning("⚠️ Debes iniciar sesión para acceder a esta página")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator

def require_admin():
    """
    Decorator para requerir permisos de administrador
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not is_admin():
                st.error("🚫 No tienes permisos para acceder a esta función")
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator
