"""
Sistema de Información PECSA
Aplicación principal con Streamlit
"""

import streamlit as st
import sys
import os
from init_db import main as init_db_main

# Agregar el directorio al path
sys.path.append('/content/pecsa_system')

from auth import login_user, logout_user, is_admin, require_login, hash_password
from models import CollaboratorModel, UserModel, RoleModel, UserRoleModel
from datetime import datetime
import pandas as pd

# Inicializar la base de datos al iniciar
try:
    init_db_main()
except Exception as e:
    st.warning(f"⚠️ La inicialización de la BD falló o ya está realizada: {e}")

# ============================================
# CONFIGURACIÓN DE LA APLICACIÓN
# ============================================

st.set_page_config(
    page_title="Sistema PECSA",
    page_icon="⛽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar estado de sesión
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ============================================
# ESTILOS CSS PERSONALIZADOS
# ============================================

st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f4788;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #1f4788;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c5aa0;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #f0f4f8;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #1f4788;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid #dc3545;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# FUNCIONES DE INTERFAZ
# ============================================

def show_login_page():
    """Muestra la página de login"""
    st.markdown('<h1 class="main-header">⛽ Sistema PECSA</h1>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.markdown('<h2 class="sub-header">🔐 Inicio de Sesión</h2>', unsafe_allow_html=True)

        with st.form("login_form"):
            username = st.text_input("👤 Usuario", placeholder="Ingrese su usuario")
            password = st.text_input("🔑 Contraseña", type="password", placeholder="Ingrese su contraseña")
            submit = st.form_submit_button("Ingresar", use_container_width=True, type="primary")

            if submit:
                if username and password:
                    if login_user(username, password):
                        st.success("✅ Inicio de sesión exitoso!")
                        st.rerun()
                    else:
                        st.error("❌ Usuario o contraseña incorrectos")
                else:
                    st.warning("⚠️ Por favor complete todos los campos")

        # Información de usuarios de prueba
        with st.expander("ℹ️ Usuarios de Prueba"):
            st.markdown("""
            **Administrador:**
            - Usuario: `admin`
            - Contraseña: `Admin123!`

            **Ventas:**
            - Usuario: `ventas`
            - Contraseña: `Ventas123!`

            **Compras:**
            - Usuario: `compras`
            - Contraseña: `Compras123!`

            **Finanzas:**
            - Usuario: `finanzas`
            - Contraseña: `Finanzas123!`
            """)

def show_dashboard():
    """Muestra el dashboard principal"""
    user = st.session_state.user

    st.markdown(f"""
    <div class="info-box">
        <h2>👋 Bienvenido, {user['first_name']} {user['last_name']}</h2>
        <p><strong>Cargo:</strong> {user['position']}</p>
        <p><strong>Roles:</strong> {', '.join(user['roles']) if user['roles'] else 'Sin roles asignados'}</p>
        <p><strong>Último acceso:</strong> {user['last_login'].strftime('%d/%m/%Y %H:%M') if user['last_login'] else 'Primer acceso'}</p>
    </div>
    """, unsafe_allow_html=True)

    # Estadísticas del sistema (solo para admin)
    if is_admin():
        st.markdown('<h2 class="sub-header">📊 Estadísticas del Sistema</h2>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        # Obtener estadísticas
        collaborators = CollaboratorModel.get_all()
        users = UserModel.get_all()
        roles = RoleModel.get_all()

        active_collaborators = [c for c in collaborators if c['status'] == 'active']
        active_users = [u for u in users if u['is_active']]

        with col1:
            st.metric(
                label="👥 Colaboradores",
                value=len(collaborators),
                delta=f"{len(active_collaborators)} activos"
            )

        with col2:
            st.metric(
                label="👤 Usuarios",
                value=len(users),
                delta=f"{len(active_users)} activos"
            )

        with col3:
            st.metric(
                label="🎭 Roles",
                value=len(roles)
            )

        with col4:
            st.metric(
                label="✅ Estado del Sistema",
                value="Operativo",
                delta="100%"
            )

    # Información según el rol
    st.markdown('<h2 class="sub-header">🚀 Accesos Rápidos</h2>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        if is_admin():
            st.info("**Administración**\n\nGestiona usuarios, colaboradores y roles del sistema")

    with col2:
        if 'Ventas' in user['roles'] or is_admin():
            st.info("**Módulo de Ventas**\n\n(Próximamente)")

    with col3:
        if 'Compras' in user['roles'] or is_admin():
            st.info("**Módulo de Compras**\n\n(Próximamente)")

def show_collaborators_page():
    """Muestra la página de gestión de colaboradores"""
    st.markdown('<h1 class="main-header">👥 Gestión de Colaboradores</h1>', unsafe_allow_html=True)

    # Tabs para diferentes acciones
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Colaboradores", "➕ Nuevo Colaborador", "📊 Estadísticas"])

    with tab1:
        # Filtros
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            search = st.text_input("🔍 Buscar", placeholder="Nombre o documento...")
        with col2:
            status_filter = st.selectbox("Estado", ["Todos", "Activos", "Inactivos"])
        with col3:
            st.write("")
            if st.button("🔄 Actualizar", use_container_width=True):
                st.rerun()

        # Obtener colaboradores
        collaborators = CollaboratorModel.get_all()

        # Aplicar filtros
        if status_filter == "Activos":
            collaborators = [c for c in collaborators if c['status'] == 'active']
        elif status_filter == "Inactivos":
            collaborators = [c for c in collaborators if c['status'] == 'inactive']

        if search:
            search_lower = search.lower()
            collaborators = [
                c for c in collaborators
                if search_lower in c['first_name'].lower() or
                   search_lower in c['last_name'].lower() or
                   search_lower in c['document_number'].lower()
            ]

        # Mostrar tabla
        if collaborators:
            df = pd.DataFrame(collaborators)
            df['Nombre Completo'] = df['first_name'] + ' ' + df['last_name']
            df['Estado'] = df['status'].map({'active': '✅ Activo', 'inactive': '❌ Inactivo'})

            columns_to_show = ['id', 'document_number', 'Nombre Completo', 'position', 'phone', 'email', 'Estado']
            df_display = df[columns_to_show]
            df_display.columns = ['ID', 'Documento', 'Nombre', 'Cargo', 'Teléfono', 'Email', 'Estado']

            st.dataframe(df_display, use_container_width=True, hide_index=True)

            # Acciones
            st.markdown("### ⚙️ Acciones")
            col1, col2 = st.columns(2)

            with col1:
                selected_id = st.selectbox(
                    "Seleccionar colaborador",
                    options=[c['id'] for c in collaborators],
                    format_func=lambda x: next(f"{c['first_name']} {c['last_name']} ({c['document_number']})"
                                              for c in collaborators if c['id'] == x)
                )

            with col2:
                action = st.selectbox("Acción", ["Seleccionar...", "Editar", "Desactivar", "Activar"])

                if st.button("Ejecutar", type="primary", use_container_width=True):
                    if action == "Editar":
                        st.session_state.edit_collaborator_id = selected_id
                        st.rerun()
                    elif action == "Desactivar":
                        collaborator = CollaboratorModel.get_by_id(selected_id)
                        collaborator['status'] = 'inactive'
                        CollaboratorModel.update(selected_id, collaborator)
                        st.success("✅ Colaborador desactivado")
                        st.rerun()
                    elif action == "Activar":
                        collaborator = CollaboratorModel.get_by_id(selected_id)
                        collaborator['status'] = 'active'
                        CollaboratorModel.update(selected_id, collaborator)
                        st.success("✅ Colaborador activado")
                        st.rerun()
        else:
            st.info("No se encontraron colaboradores")

    with tab2:
        st.markdown("### 📝 Registro de Nuevo Colaborador")

        with st.form("new_collaborator_form"):
            col1, col2 = st.columns(2)

            with col1:
                document = st.text_input("Número de Documento*", max_chars=20)
                first_name = st.text_input("Nombres*", max_chars=100)
                last_name = st.text_input("Apellidos*", max_chars=100)

            with col2:
                position = st.text_input("Cargo*", max_chars=100)
                phone = st.text_input("Teléfono", max_chars=20)
                email = st.text_input("Email", max_chars=100)

            status = st.selectbox("Estado", ["active", "inactive"], format_func=lambda x: "Activo" if x == "active" else "Inactivo")

            submit = st.form_submit_button("💾 Guardar Colaborador", use_container_width=True, type="primary")

            if submit:
                if document and first_name and last_name and position:
                    # Verificar si el documento ya existe
                    existing = CollaboratorModel.get_by_document(document)
                    if existing:
                        st.error("❌ Ya existe un colaborador con ese número de documento")
                    else:
                        data = {
                            'document_number': document,
                            'first_name': first_name,
                            'last_name': last_name,
                            'position': position,
                            'phone': phone,
                            'email': email,
                            'status': status
                        }
                        CollaboratorModel.create(data)
                        st.success("✅ Colaborador registrado exitosamente")
                        st.rerun()
                else:
                    st.warning("⚠️ Complete todos los campos obligatorios")

    with tab3:
        st.markdown("### 📊 Estadísticas de Colaboradores")

        collaborators = CollaboratorModel.get_all()

        if collaborators:
            col1, col2 = st.columns(2)

            with col1:
                # Estado de colaboradores
                df_status = pd.DataFrame(collaborators)
                status_counts = df_status['status'].value_counts()
                st.metric("Total de Colaboradores", len(collaborators))
                st.bar_chart(status_counts)

            with col2:
                # Por cargo
                position_counts = df_status['position'].value_counts().head(5)
                st.metric("Cargos Únicos", df_status['position'].nunique())
                st.bar_chart(position_counts)

def show_users_page():
    """Muestra la página de gestión de usuarios"""
    st.markdown('<h1 class="main-header">👤 Gestión de Usuarios</h1>', unsafe_allow_html=True)

    # Tabs
    tab1, tab2 = st.tabs(["📋 Lista de Usuarios", "➕ Nuevo Usuario"])

    with tab1:
        # Obtener usuarios
        users = UserModel.get_all()

        if users:
            # Preparar datos para mostrar
            data_display = []
            for user in users:
                data_display.append({
                    'ID': user['id'],
                    'Usuario': user['username'],
                    'Colaborador': f"{user['first_name']} {user['last_name']}",
                    'Documento': user['document_number'],
                    'Cargo': user['position'],
                    'Roles': ', '.join(user['roles']) if user['roles'] else 'Sin roles',
                    'Estado': '✅ Activo' if user['is_active'] else '❌ Inactivo',
                    'Último acceso': user['last_login'].strftime('%d/%m/%Y %H:%M') if user['last_login'] else 'Nunca'
                })

            df = pd.DataFrame(data_display)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Acciones
            st.markdown("### ⚙️ Acciones")
            col1, col2, col3 = st.columns(3)

            with col1:
                selected_user = st.selectbox(
                    "Seleccionar usuario",
                    options=[u['id'] for u in users],
                    format_func=lambda x: next(f"{u['username']} - {u['first_name']} {u['last_name']}"
                                              for u in users if u['id'] == x)
                )

            with col2:
                action = st.selectbox("Acción", ["Seleccionar...", "Editar", "Cambiar Contraseña", "Desactivar", "Activar", "Eliminar"])

            with col3:
                st.write("")
                if st.button("Ejecutar Acción", type="primary", use_container_width=True):
                    user = UserModel.get_by_id(selected_user)

                    if action == "Desactivar":
                        UserModel.update(selected_user, {'username': user['username'], 'is_active': False})
                        st.success("✅ Usuario desactivado")
                        st.rerun()
                    elif action == "Activar":
                        UserModel.update(selected_user, {'username': user['username'], 'is_active': True})
                        st.success("✅ Usuario activado")
                        st.rerun()
                    elif action == "Eliminar":
                        if st.session_state.user['id'] != selected_user:
                            UserModel.delete(selected_user)
                            st.success("✅ Usuario eliminado")
                            st.rerun()
                        else:
                            st.error("❌ No puedes eliminar tu propio usuario")
                    elif action == "Cambiar Contraseña":
                        st.session_state.change_password_user = selected_user
                        st.rerun()
        else:
            st.info("No hay usuarios registrados")

    with tab2:
        st.markdown("### 📝 Registro de Nuevo Usuario")

        # Obtener colaboradores sin usuario
        all_collaborators = CollaboratorModel.get_all('active')
        users = UserModel.get_all()
        used_collaborator_ids = [u['collaborator_id'] for u in users if u['collaborator_id']]
        available_collaborators = [c for c in all_collaborators if c['id'] not in used_collaborator_ids]

        if available_collaborators:
            with st.form("new_user_form"):
                col1, col2 = st.columns(2)

                with col1:
                    selected_collaborator = st.selectbox(
                        "Colaborador*",
                        options=[c['id'] for c in available_collaborators],
                        format_func=lambda x: next(f"{c['first_name']} {c['last_name']} - {c['document_number']}"
                                                  for c in available_collaborators if c['id'] == x)
                    )
                    username = st.text_input("Nombre de Usuario*", max_chars=50)

                with col2:
                    password = st.text_input("Contraseña*", type="password", max_chars=255)
                    password_confirm = st.text_input("Confirmar Contraseña*", type="password", max_chars=255)

                is_active = st.checkbox("Usuario Activo", value=True)

                submit = st.form_submit_button("💾 Crear Usuario", use_container_width=True, type="primary")

                if submit:
                    if username and password and password_confirm:
                        if password == password_confirm:
                            # Verificar que el username no exista
                            existing = UserModel.get_by_username(username)
                            if existing:
                                st.error("❌ El nombre de usuario ya existe")
                            else:
                                data = {
                                    'username': username,
                                    'password': password,
                                    'collaborator_id': selected_collaborator,
                                    'is_active': is_active
                                }
                                UserModel.create(data)
                                st.success("✅ Usuario creado exitosamente")
                                st.rerun()
                        else:
                            st.error("❌ Las contraseñas no coinciden")
                    else:
                        st.warning("⚠️ Complete todos los campos obligatorios")
        else:
            st.info("No hay colaboradores disponibles para crear usuarios. Todos los colaboradores activos ya tienen usuario asignado.")

def show_roles_page():
    """Muestra la página de gestión de roles"""
    st.markdown('<h1 class="main-header">🎭 Gestión de Roles</h1>', unsafe_allow_html=True)

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 Lista de Roles", "➕ Nuevo Rol", "👥 Asignación de Roles"])

    with tab1:
        roles = RoleModel.get_all()

        if roles:
            data_display = []
            for role in roles:
                data_display.append({
                    'ID': role['id'],
                    'Nombre': role['name'],
                    'Descripción': role['description'] or 'Sin descripción',
                    'Permisos': role['permissions'] or 'Sin permisos definidos',
                    'Usuarios': role['user_count']
                })

            df = pd.DataFrame(data_display)
            st.dataframe(df, use_container_width=True, hide_index=True)

            # Acciones
            if len([r for r in roles if r['name'] != 'Administrador']) > 0:
                st.markdown("### ⚙️ Acciones")
                col1, col2, col3 = st.columns(3)

                with col1:
                    editable_roles = [r for r in roles if r['name'] != 'Administrador']
                    selected_role = st.selectbox(
                        "Seleccionar rol",
                        options=[r['id'] for r in editable_roles],
                        format_func=lambda x: next(r['name'] for r in editable_roles if r['id'] == x)
                    )

                with col2:
                    action = st.selectbox("Acción", ["Seleccionar...", "Editar", "Eliminar"])

                with col3:
                    st.write("")
                    if st.button("Ejecutar", type="primary", use_container_width=True):
                        if action == "Eliminar":
                            role = RoleModel.get_by_id(selected_role)
                            if role['user_count'] == 0:
                                RoleModel.delete(selected_role)
                                st.success("✅ Rol eliminado")
                                st.rerun()
                            else:
                                st.error(f"❌ No se puede eliminar. El rol tiene {role['user_count']} usuarios asignados")
        else:
            st.info("No hay roles registrados")

    with tab2:
        st.markdown("### 📝 Crear Nuevo Rol")

        with st.form("new_role_form"):
            name = st.text_input("Nombre del Rol*", max_chars=50)
            description = st.text_area("Descripción", max_chars=500)

            st.markdown("#### Permisos")
            col1, col2, col3 = st.columns(3)

            permissions = []
            with col1:
                st.markdown("**Ventas**")
                if st.checkbox("Lectura de ventas"):
                    permissions.append("sales_read")
                if st.checkbox("Escritura de ventas"):
                    permissions.append("sales_write")
                if st.checkbox("Gestión de clientes"):
                    permissions.append("customers_read")

            with col2:
                st.markdown("**Compras**")
                if st.checkbox("Lectura de compras"):
                    permissions.append("purchases_read")
                if st.checkbox("Escritura de compras"):
                    permissions.append("purchases_write")
                if st.checkbox("Gestión de proveedores"):
                    permissions.append("suppliers_read")

            with col3:
                st.markdown("**Finanzas**")
                if st.checkbox("Lectura de finanzas"):
                    permissions.append("finance_read")
                if st.checkbox("Escritura de finanzas"):
                    permissions.append("finance_write")
                if st.checkbox("Reportes"):
                    permissions.append("reports_read")

            submit = st.form_submit_button("💾 Crear Rol", use_container_width=True, type="primary")

            if submit:
                if name:
                    existing = RoleModel.get_by_name(name)
                    if existing:
                        st.error("❌ Ya existe un rol con ese nombre")
                    else:
                        data = {
                            'name': name,
                            'description': description,
                            'permissions': ','.join(permissions) if permissions else None
                        }
                        RoleModel.create(data)
                        st.success("✅ Rol creado exitosamente")
                        st.rerun()
                else:
                    st.warning("⚠️ El nombre del rol es obligatorio")

    with tab3:
        st.markdown("### 👥 Asignación de Roles a Usuarios")

        users = UserModel.get_all()
        roles = RoleModel.get_all()

        if users and roles:
            col1, col2 = st.columns(2)

            with col1:
                selected_user = st.selectbox(
                    "Seleccionar Usuario",
                    options=[u['id'] for u in users],
                    format_func=lambda x: next(f"{u['username']} - {u['first_name']} {u['last_name']}"
                                              for u in users if u['id'] == x)
                )

                if selected_user:
                    user_roles = UserRoleModel.get_user_roles(selected_user)
                    current_role_ids = [r['id'] for r in user_roles]

                    st.markdown("**Roles actuales:**")
                    if user_roles:
                        for role in user_roles:
                            st.write(f"• {role['name']}")
                    else:
                        st.write("Sin roles asignados")

            with col2:
                st.markdown("**Asignar/Modificar Roles:**")

                selected_roles = st.multiselect(
                    "Seleccionar roles",
                    options=[r['id'] for r in roles],
                    default=current_role_ids,
                    format_func=lambda x: next(r['name'] for r in roles if r['id'] == x)
                )

                if st.button("💾 Guardar Cambios", type="primary", use_container_width=True):
                    UserRoleModel.update_user_roles(selected_user, selected_roles)
                    st.success("✅ Roles actualizados exitosamente")
                    st.rerun()
        else:
            st.info("No hay usuarios o roles disponibles")

# ============================================
# APLICACIÓN PRINCIPAL
# ============================================

def main():
    """Función principal de la aplicación"""

    # Si no está logueado, mostrar login
    if not st.session_state.logged_in:
        show_login_page()
    else:
        # Sidebar con menú
        with st.sidebar:
            st.markdown("## ⛽ Sistema PECSA")
            st.markdown(f"**Usuario:** {st.session_state.username}")
            st.markdown(f"**Rol:** {', '.join(st.session_state.user_roles)}")
            st.markdown("---")

            # Menú de navegación
            menu_items = ["🏠 Dashboard"]

            if is_admin():
                menu_items.extend([
                    "👥 Colaboradores",
                    "👤 Usuarios",
                    "🎭 Roles"
                ])

            page = st.selectbox("Navegación", menu_items)

            st.markdown("---")

            if st.button("🚪 Cerrar Sesión", use_container_width=True):
                logout_user()
                st.rerun()

            # Footer
            st.markdown("---")
            st.markdown("### 📊 Estado del Sistema")
            st.success("✅ Operativo")
            st.caption("v1.0.0 - Sprint 1")

        # Contenido principal según la página seleccionada
        if page == "🏠 Dashboard":
            show_dashboard()
        elif page == "👥 Colaboradores":
            show_collaborators_page()
        elif page == "👤 Usuarios":
            show_users_page()
        elif page == "🎭 Roles":
            show_roles_page()

if __name__ == "__main__":
    main()
