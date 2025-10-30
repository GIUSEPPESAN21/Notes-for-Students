# -*- coding: utf-8 -*-
"""
Laboratorio #2: Gestión de Notas (Versión Streamlit v3 - Funcionalidad Extendida)

Fundamentación Arquitectónica (v3):
Esta versión se basa en la v2 (navegación por pestañas) y añade
funcionalidades avanzadas de análisis, exportación y gestión.

1.  Manejo de Estado (st.session_state):
    Se mantiene como pilar, sin cambios en la estructura.

2.  Navegación en Página (st.tabs):
    Se renombra la pestaña "Mostrar Notas" a "Reporte General" y
    "Eliminar" a "Administración" para reflejar las nuevas
    funcionalidades.

3.  Estética Mejorada (CSS + Componentes Nativos):
    Se mantiene el CSS de la v2.

4.  Funcionalidad Extendida (Novedades):
    - Se añaden métricas de 'Nota Alta' y 'Nota Baja'.
    - Se calcula un 'Estado' (Aprobado/Reprobado) para cada estudiante
      en el DataFrame.
    - Se añade un `st.bar_chart` para visualizar la distribución de notas.
    - Se implementa un `st.text_input` para filtrar (buscar) estudiantes
      en el reporte.
    - Se añade un `st.download_button` para exportar los datos a CSV.
    - Se añade una "Zona de Peligro" para reiniciar (limpiar)
      todos los datos de la sesión con confirmación.
"""

import streamlit as st
import pandas as pd
import numpy as np # Necesario para algunas estadísticas

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Sistema de Gestión de Notas",
    page_icon="🎓",
    layout="centered"
)

# --- Constantes del Programa ---
MODIFICATION_LIMIT = 3
PASSING_GRADE = 3.0 # Nota mínima para aprobar (escala 1-5)

# --- CSS Personalizado (v2) ---
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
button[kind...].st-emotion-cache-s49nzw:hover {
    background-color: #B91C1C;
}
</style>
""", unsafe_allow_html=True)


# --- Inicialización del Estado de la Sesión ---
if 'students' not in st.session_state:
    st.session_state.students = []
if 'modification_attempts' not in st.session_state:
    st.session_state.modification_attempts = {}

# --- Lógica de Negocio (Controladores) ---

def find_student_index(name):
    """Encuentra el índice de un estudiante. Retorna el índice o None."""
    for i, student in enumerate(st.session_state.students):
        if student['nombre'].lower() == name.lower():
            return i
    return None

def get_stats():
    """
    Calcula todas las estadísticas: promedio, alta y baja.
    Retorna un diccionario con las estadísticas.
    """
    if not st.session_state.students:
        return {"average": 0.0, "high": 0.0, "low": 0.0}

    try:
        notes = [student['nota'] for student in st.session_state.students]
        average = np.mean(notes)
        high = np.max(notes)
        low = np.min(notes)
        return {"average": average, "high": high, "low": low}
    except Exception:
        return {"average": 0.0, "high": 0.0, "low": 0.0}

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

def reset_all_data():
    """Elimina todos los datos de la sesión."""
    st.session_state.students = []
    st.session_state.modification_attempts = {}


# --- UI Principal ---
st.title("🎓 Sistema de Gestión de Notas")
st.write("Bienvenido al sistema. Navegue usando las pestañas a continuación.")

# --- Navegación por Pestañas (En lugar del Sidebar) ---
tab_display, tab_add, tab_modify, tab_admin = st.tabs([
    "📊 Reporte General",
    "➕ Ingresar Nota",
    "✏️ Modificar Nota",
    "🗑️ Administración"
])


# --- Pestaña 1: Reporte General (Actividad 3 Mejorada) ---
with tab_display:
    st.header("Actividad 3: Reporte General y Análisis")
    
    if not st.session_state.students:
        st.info("Aún no se han ingresado estudiantes. Agregue uno en la pestaña 'Ingresar Nota'.")
    else:
        # 1. Obtener estadísticas
        stats = get_stats()

        # 2. Tarjetas de métricas (inspirado en React)
        st.subheader("Estadísticas del Curso")
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Promedio General", value=f"{stats['average']:.2f}")
        col2.metric(label="Nota Más Alta", value=f"{stats['high']:.2f}")
        col3.metric(label="Nota Más Baja", value=f"{stats['low']:.2f}")

        st.divider()

        # 3. Listado de Estudiantes (con búsqueda y estado)
        st.subheader("Listado de Estudiantes")
        
        # 3.a. Creación del DataFrame
        df = pd.DataFrame(st.session_state.students)
        # 3.b. Añadir columna de Estado
        df['Estado'] = df['nota'].apply(lambda nota: "Aprobado" if nota >= PASSING_GRADE else "Reprobado")
        
        # 3.c. Implementar Búsqueda
        search_term = st.text_input("Buscar Estudiante por nombre:", placeholder="Escriba un nombre para filtrar...")
        if search_term:
            filtered_df = df[df['nombre'].str.contains(search_term, case=False, na=False)]
        else:
            filtered_df = df
            
        # 3.d. Mostrar la tabla
        st.dataframe(filtered_df, use_container_width=True)

        # 4. Gráfico de Distribución
        st.subheader("Distribución de Notas")
        # Contamos cuántos estudiantes hay por cada nota
        note_counts = df['nota'].value_counts().sort_index()
        st.bar_chart(note_counts)

        st.divider()
        
        # 5. Exportar a CSV
        st.subheader("Exportar Datos")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Descargar Reporte en CSV",
            data=csv,
            file_name="reporte_estudiantes.csv",
            mime="text/csv",
        )


# --- Pestaña 2: Ingresar Notas (Actividad 1) ---
with tab_add:
    st.header("Actividad 1: Ingresar Nueva Nota")

    # Usamos st.form para agrupar entradas
    with st.form(key="add_student_form"):
        name = st.text_input("Nombre del Estudiante", placeholder="Ej. Ana Pérez")
        grade = st.number_input(
            "Nota (1.0 - 5.0)",
            min_value=1.0,
            max_value=5.0,
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
                        min_value=1.0,
                        max_value=5.0,
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

# --- Pestaña 4: Administración (Eliminar) ---
with tab_admin:
    st.header("Administración del Sistema")
    
    st.subheader("Eliminar un Estudiante")
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
        
        st.warning("⚠️ Esta acción es permanente.", icon="🚨")

        if delete_selected_name:
            # Usamos type="primary" que nuestro CSS pintará de rojo
            if st.button(f"Eliminar permanentemente a {delete_selected_name}", type="primary"):
                if delete_student(delete_selected_name):
                    st.toast(f"¡Estudiante '{delete_selected_name}' eliminado!", icon="🗑️")
                    st.rerun() # Recargamos para actualizar los selectores
                else:
                    st.error("No se pudo eliminar al estudiante.")

    st.divider()

    # Zona de Peligro (Nueva Funcionalidad)
    st.subheader("⚠️ Zona de Peligro")
    st.write("Estas acciones no se pueden deshacer.")
    
    if st.checkbox("Deseo reiniciar todo el sistema y eliminar TODOS los estudiantes."):
        if st.button("Eliminar TODOS los datos", type="primary"):
            reset_all_data()
            st.toast("Todos los datos han sido eliminados.", icon="🔥")
            st.rerun()

