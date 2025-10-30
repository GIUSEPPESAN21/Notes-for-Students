# -*- coding: utf-8 -*-
"""
Laboratorio #2: Gestión de Notas (Versión Streamlit Mejorada)

Fundamentación Arquitectónica (v2):
Esta versión abandona el panel lateral (sidebar) en favor de una
navegación principal por pestañas (`st.tabs`), similar a la UI de React.

1.  Manejo de Estado (st.session_state):
    Se mantiene como el pilar de la persistencia de datos,
    almacenando 'students' y 'modification_attempts'.

2.  Navegación en Página (st.tabs):
    Reemplaza `st.sidebar.radio` por `st.tabs`. Esto mueve
    la navegación al cuerpo principal, como solicitó el usuario,
    creando una experiencia de "Single Page Application" (SPA) más moderna.

3.  Estética Mejorada (CSS + Componentes Nativos):
    - Se inyecta CSS personalizado (`st.markdown(..., unsafe_allow_html=True)`)
      para dar a los formularios (`st.form`) un aspecto de "tarjeta"
      (sombra, bordes redondeados) y para estilizar los botones
      con gradientes y sombras, imitando el diseño de React.
    - Se usan `st.metric` para mostrar estadísticas clave (Promedio y Total)
      de forma visualmente atractiva.
    - Se usan `st.toast` para notificaciones no intrusivas, en lugar de
      los `st.success/error` estáticos.

4.  Funcionalidad Completa:
    Se añade la lógica para *Eliminar* estudiantes, una característica
    presente en la versión de React, para completar el CRUD
    (Create, Read, Update, Delete).
"""

import streamlit as st
import pandas as pd

# --- Configuración de la Página ---
# layout="wide" aprovecha mejor el espacio
st.set_page_config(
    page_title="Sistema de Gestión de Notas",
    page_icon="🎓",
    layout="centered"
)

# --- CSS Personalizado para un Look Moderno (Inspirado en React/Tailwind) ---
st.markdown("""
<style>
/* Estilo para el título principal */
h1 {
    /* Gradiente de texto similar al de React */
    background: -webkit-linear-gradient(45deg, #4F46E5, #7C3AED, #EC4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 700;
}

/* Contenedor del formulario (Tarjeta) */
div[data-testid="stForm"] {
    background-color: white;
    padding: 24px;
    border-radius: 16px; /* Bordes redondeados */
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05); /* Sombra */
    border: 1px solid #E5E7EB; /* Borde sutil */
}

/* Botones principales (dentro del formulario) */
div[data-testid="stForm"] button[kind="primary"] {
    background: linear-gradient(45deg, #4F46E5, #7C3AED); /* Gradiente */
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 20px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

div[data-testid="stForm"] button[kind="primary"]:hover {
    box-shadow: 0 10px 15px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
}

/* Botón de eliminar (tipo "primary" para rojo) */
button[kind="primary"].st-emotion-cache-s49nzw {
    background-color: #DC2626;
    border: none;
}
button[kind="primary"].st-emotion-cache-s49nzw:hover {
    background-color: #B91C1C;
}
</style>
""", unsafe_allow_html=True)


# --- Inicialización del Estado de la Sesión ---
if 'students' not in st.session_state:
    st.session_state.students = []
if 'modification_attempts' not in st.session_state:
    st.session_state.modification_attempts = {}

# Constante para el límite
MODIFICATION_LIMIT = 3

# --- Lógica de Negocio (Controladores) ---

def find_student_index(name):
    """Encuentra el índice de un estudiante. Retorna el índice o None."""
    for i, student in enumerate(st.session_state.students):
        if student['nombre'].lower() == name.lower():
            return i
    return None

def calculate_average():
    """Calcula el promedio. Retorna el promedio o 0 si está vacío."""
    if not st.session_state.students:
        return 0.0  # Requisito 3c: Manejar división por cero

    try:
        total = sum(student['nota'] for student in st.session_state.students)
        average = total / len(st.session_state.students)
        return average
    except ZeroDivisionError:
        # Doble chequeo por seguridad
        return 0.0

def delete_student(name):
    """Elimina un estudiante de la lista y sus intentos."""
    index_to_delete = find_student_index(name)
    if index_to_delete is not None:
        st.session_state.students.pop(index_to_delete)
        # Limpiar también el contador de intentos
        if name in st.session_state.modification_attempts:
            del st.session_state.modification_attempts[name]
        return True
    return False

# --- UI Principal ---
st.title("🎓 Sistema de Gestión de Notas")
st.write("Bienvenido al sistema. Navegue usando las pestañas a continuación.")

# --- Navegación por Pestañas (En lugar del Sidebar) ---
tab_display, tab_add, tab_modify, tab_delete = st.tabs([
    "📊 Mostrar Notas",
    "➕ Ingresar Nota",
    "✏️ Modificar Nota",
    "🗑️ Eliminar Estudiante"
])


# --- Pestaña 1: Mostrar Promedio y Notas (Actividad 3) ---
with tab_display:
    st.header("Actividad 3: Reporte de Notas")
    
    if not st.session_state.students:
        st.info("Aún no se han ingresado estudiantes. Agregue uno en la pestaña 'Ingresar Nota'.")
    else:
        # 3.b. Calcular el promedio
        average_grade = calculate_average()

        # Tarjetas de métricas (inspirado en React)
        col1, col2 = st.columns(2)
        col1.metric(label="Total Estudiantes", value=len(st.session_state.students))
        col2.metric(label="Promedio General", value=f"{average_grade:.2f}")

        st.divider()
        
        # 3.a. Mostrar todas las notas
        st.subheader("Listado de Estudiantes")
        
        # Usamos Pandas para un mejor formato de tabla
        df = pd.DataFrame(st.session_state.students)
        st.dataframe(df, use_container_width=True)

# --- Pestaña 2: Ingresar Notas (Actividad 1) ---
with tab_add:
    st.header("Actividad 1: Ingresar Nueva Nota")

    # Usamos st.form para agrupar entradas
    with st.form(key="add_student_form"):
        name = st.text_input("Nombre del Estudiante", placeholder="Ej. Ana Pérez")
        grade = st.number_input(
            "Nota (0.0 - 100.0)",
            min_value=0.0,
            max_value=100.0,
            step=0.1
        )
        # El botón dentro del form usará el CSS personalizado
        submitted = st.form_submit_button("Agregar Estudiante", type="primary")

    if submitted:
        # Validación de entradas
        if not name:
            st.error("El nombre del estudiante no puede estar vacío.")
        elif find_student_index(name) is not None:
            st.warning(f"El estudiante '{name}' ya existe en el sistema.")
        else:
            # Lógica de negocio
            new_student = {"nombre": name, "nota": grade}
            st.session_state.students.append(new_student)
            st.toast(f"¡Estudiante '{name}' agregado con nota {grade}!", icon="🎉")


# --- Pestaña 3: Modificar Notas (Actividad 2) ---
with tab_modify:
    st.header("Actividad 2: Modificar Nota")

    if not st.session_state.students:
        st.info("No hay estudiantes ingresados para modificar.")
    else:
        student_names = [student['nombre'] for student in st.session_state.students]
        selected_name = st.selectbox(
            "Seleccione el estudiante a modificar:",
            student_names,
            index=None,
            placeholder="Seleccionar estudiante..."
        )

        if selected_name:
            # Obtenemos el contador de intentos
            attempts = st.session_state.modification_attempts.get(selected_name, 0)
            st.info(f"Intentos de modificación para '{selected_name}': {attempts} / {MODIFICATION_LIMIT}")

            if attempts >= MODIFICATION_LIMIT:
                st.error(f"Se ha alcanzado el límite de {MODIFICATION_LIMIT} modificaciones para '{selected_name}'.")
            else:
                current_index = find_student_index(selected_name)
                current_grade = st.session_state.students[current_index]['nota']

                with st.form(key="modify_student_form"):
                    new_grade = st.number_input(
                        f"Nueva nota para {selected_name} (actual: {current_grade})",
                        min_value=0.0,
                        max_value=100.0,
                        step=0.1,
                        value=current_grade # Pre-llenamos
                    )
                    modify_submitted = st.form_submit_button("Actualizar Nota", type="primary")

                if modify_submitted:
                    if new_grade == current_grade:
                        st.warning("La nueva nota es igual a la actual. No se hicieron cambios.")
                    else:
                        st.session_state.students[current_index]['nota'] = new_grade
                        st.session_state.modification_attempts[selected_name] = attempts + 1
                        st.toast(f"Nota de '{selected_name}' actualizada.", icon="✅")
                        st.info(f"Intentos restantes para '{selected_name}': {MODIFICATION_LIMIT - (attempts + 1)}")

# --- Pestaña 4: Eliminar Estudiante (Funcionalidad Añadida) ---
with tab_delete:
    st.header("Eliminar Estudiante del Sistema")

    if not st.session_state.students:
        st.info("No hay estudiantes ingresados para eliminar.")
    else:
        delete_student_names = [student['nombre'] for student in st.session_state.students]
        delete_selected_name = st.selectbox(
            "Seleccione el estudiante a ELIMINAR:",
            delete_student_names,
            index=None,
            placeholder="Seleccionar estudiante..."
        )
        
        st.warning("⚠️ Esta acción es permanente y no se puede deshacer.", icon="🚨")

        if delete_selected_name:
            # Usamos type="primary" que nuestro CSS pintará de rojo
            if st.button(f"Eliminar permanentemente a {delete_selected_name}", type="primary"):
                if delete_student(delete_selected_name):
                    st.toast(f"¡Estudiante '{delete_selected_name}' eliminado!", icon="🗑️")
                    st.rerun() # Recargamos para actualizar los selectores
                else:
                    st.error("No se pudo eliminar al estudiante.")
