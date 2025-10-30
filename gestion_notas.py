# -*- coding: utf-8 -*-
"""
Laboratorio #2: Gestión de un Sistema de Notas con Python y Streamlit

Fundamentación Arquitectónica:
Esta aplicación transforma el script de consola del Laboratorio #2
en una aplicación web interactiva usando Streamlit.

La arquitectura se basa en los siguientes principios:

1.  Manejo de Estado (st.session_state):
    Streamlit re-ejecuta el script con cada interacción. Para persistir
    la lista de estudiantes, usamos `st.session_state`.
    `st.session_state.students` actúa como nuestra "base de datos" en memoria
    para la sesión del usuario.

2.  Diseño Controlado por Eventos:
    Se abandona el bucle `while` de la consola. La navegación se maneja
    con un `st.sidebar.radio`, que actúa como nuestro "menú interactivo".
    El contenido de la página se renderiza condicionalmente basado en la
    selección del menú.

3.  Separación de Lógica y Vista:
    La lógica de negocio (calcular, agregar, modificar) se encapsula
    en funciones. La interfaz de usuario (UI) se define en funciones
    de renderizado (ej. `render_add_page`).

4.  Validación Proactiva:
    En lugar de depender únicamente de `try-except` para la entrada del
    usuario (como se haría en consola), usamos widgets de Streamlit
    (`st.number_input`) que previenen la entrada incorrecta desde el
    principio. `try-except` se reserva para errores de lógica, como
    la división por cero.

5.  Retroalimentación de UI:
    Se usan `st.success`, `st.error`, y `st.warning` para dar
    retroalimentación clara al usuario, en lugar de `print()`.
"""

import streamlit as st

# --- Configuración de la Página ---
# Esto debe ser lo primero que se ejecuta en Streamlit
st.set_page_config(
    page_title="Sistema de Gestión de Notas",
    page_icon="🎓",
    layout="centered"
)

# --- Inicialización del Estado de la Sesión ---
# Esta es la parte MÁS CRÍTICA de la arquitectura.
# Si 'students' no está en st.session_state, lo inicializamos.
# Esto asegura que nuestra lista de estudiantes persista entre
# las interacciones del usuario.

if 'students' not in st.session_state:
    # Usamos una lista de diccionarios para mejor legibilidad
    st.session_state.students = []

if 'modification_attempts' not in st.session_state:
    # Requisito: Implementar un contador de intentos de modificación
    # Usamos un diccionario para rastrear intentos por nombre de estudiante
    st.session_state.modification_attempts = {}

# Constante para el límite de intentos de modificación
MODIFICATION_LIMIT = 3

# --- Lógica de Negocio (Controladores) ---

def find_student_index(name):
    """
    Encuentra el índice de un estudiante en la lista de session_state.
    Retorna el índice o None si no se encuentra.
    """
    for i, student in enumerate(st.session_state.students):
        if student['nombre'].lower() == name.lower():
            return i
    return None

def calculate_average():
    """
    Calcula el promedio de las notas.
    Maneja el error de división por cero como pide el laboratorio.
    Retorna el promedio o None si no hay estudiantes.
    """
    if not st.session_state.students:
        return None  # No hay estudiantes

    try:
        total = sum(student['nota'] for student in st.session_state.students)
        average = total / len(st.session_state.students)
        return average
    except ZeroDivisionError:
        # Aunque la comprobación anterior (if not) lo previene,
        # mantenemos esto para cumplir explícitamente con el requisito
        # del laboratorio de usar try-except para la división por cero.
        return None

# --- Vistas (Renderizado de Páginas) ---

def render_add_page():
    """Renderiza la página para 'Ingresar Notas' (Actividad 1)."""
    st.header("Actividad 1: Ingresar Notas de Estudiantes")

    # Usamos st.form para agrupar las entradas y enviarlas con un solo botón.
    # Esto evita que la página se recargue con cada tecla presionada.
    with st.form(key="add_student_form"):
        name = st.text_input("Nombre del Estudiante")
        # st.number_input previene errores de tipo (no se pueden letras)
        grade = st.number_input(
            "Nota del Estudiante",
            min_value=0.0,
            max_value=100.0,  # Asumimos una escala de 0-100
            step=0.1
        )
        submitted = st.form_submit_button("Agregar Estudiante")

    if submitted:
        # Validación de entradas
        if not name:
            st.error("El nombre del estudiante no puede estar vacío.")
        elif find_student_index(name) is not None:
            st.error(f"El estudiante '{name}' ya existe en el sistema.")
        else:
            # Lógica de negocio
            new_student = {"nombre": name, "nota": grade}
            st.session_state.students.append(new_student)
            st.success(f"¡Estudiante '{name}' agregado con nota {grade}!")

def render_modify_page():
    """Renderiza la página para 'Modificar Notas' (Actividad 2)."""
    st.header("Actividad 2: Modificar Nota de un Estudiante")

    if not st.session_state.students:
        st.warning("No hay estudiantes ingresados para modificar.")
        return  # Salimos de la función si no hay estudiantes

    # Creamos una lista de nombres para el selector
    student_names = [student['nombre'] for student in st.session_state.students]
    selected_name = st.selectbox("Seleccione el estudiante a modificar:", student_names)

    if selected_name:
        # Obtenemos el contador de intentos
        attempts = st.session_state.modification_attempts.get(selected_name, 0)
        st.info(f"Intentos de modificación para '{selected_name}': {attempts} / {MODIFICATION_LIMIT}")

        # Verificamos si el límite de intentos se ha alcanzado
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
                    value=current_grade # Pre-llenamos con la nota actual
                )
                modify_submitted = st.form_submit_button("Actualizar Nota")

            if modify_submitted:
                if new_grade == current_grade:
                    st.warning("La nueva nota es igual a la nota actual. No se realizaron cambios.")
                else:
                    # Lógica de negocio
                    st.session_state.students[current_index]['nota'] = new_grade
                    # Incrementamos el contador de intentos
                    st.session_state.modification_attempts[selected_name] = attempts + 1
                    st.success(f"Nota de '{selected_name}' actualizada a {new_grade}.")
                    st.info(f"Intentos restantes para '{selected_name}': {MODIFICATION_LIMIT - (attempts + 1)}")


def render_display_page():
    """Renderiza la página para 'Mostrar Promedio y Notas' (Actividad 3)."""
    st.header("Actividad 3: Mostrar Promedio y Notas")

    if not st.session_state.students:
        st.info("Aún no se han ingresado estudiantes.")
        return

    # 3.b. Calcular el promedio
    st.subheader("Promedio General")
    average_grade = calculate_average()

    if average_grade is not None:
        # st.metric es un widget de UI excelente para mostrar KPIs
        st.metric(label="Promedio de la clase", value=f"{average_grade:.2f}")
    else:
        # 3.c. Manejo de error (aunque ya cubierto por el 'if not')
        st.warning("No se puede calcular el promedio, no hay notas ingresadas.")

    # 3.a. Mostrar todas las notas
    st.subheader("Listado de Estudiantes")
    # st.dataframe es una forma limpia de mostrar listas de diccionarios
    st.dataframe(st.session_state.students, use_container_width=True)


# --- Aplicación Principal (Router) ---

st.title("🎓 Sistema de Gestión de Notas")
st.write("Bienvenido al sistema de gestión de notas. Use el menú de la izquierda para navegar.")

# El 'Menú Interactivo' del laboratorio, implementado con un radio button
# en la barra lateral (sidebar) de Streamlit.
menu_options = [
    "Ingresar Notas (Actividad 1)",
    "Modificar Nota (Actividad 2)",
    "Mostrar Promedio y Notas (Actividad 3)"
]
selection = st.sidebar.radio("Menú Principal", menu_options)

st.sidebar.info(
    "Esta es una aplicación web que implementa los requisitos del "
    "Laboratorio #2 usando Streamlit y una arquitectura basada en "
    "manejo de estado de sesión."
)

# Enrutador de vistas: Muestra la página según la selección del menú
if selection == menu_options[0]:
    render_add_page()
elif selection == menu_options[1]:
    render_modify_page()
elif selection == menu_options[2]:
    render_display_page()
