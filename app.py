import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ---------------------------
# CONEXIÓN GOOGLE SHEETS
# ---------------------------
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"],
    scopes=scope
)

client = gspread.authorize(creds)
sheet = client.open("Zarit_Cuidadores_Bello").sheet1

# ---------------------------
# CONFIG
# ---------------------------
st.set_page_config(page_title="Test Zarit", layout="centered")

st.title("Test de Zarit")

# ---------------------------
# OPCIONES
# ---------------------------
OPCIONES = {
    "Nunca": 0,
    "Rara vez": 1,
    "Algunas veces": 2,
    "Bastantes veces": 3,
    "Casi siempre": 4,
}

ITEMS = [
    "¿Siente que su familiar solicita más ayuda de la que necesita?",
    "¿Siente que no tiene tiempo para usted?",
    "¿Se siente estresado por cuidar a su familiar?",
    "¿Se siente avergonzado por su familiar?",
    "¿Se siente enojado cerca de su familiar?",
    "¿Afecta su relación con otros?",
    "¿Teme por el futuro?",
    "¿Su familiar depende de usted?",
    "¿Se siente tenso?",
    "¿Su salud ha empeorado?",
    "¿No tiene privacidad?",
    "¿Su vida social se afectó?",
    "¿Evita invitar personas?",
    "¿Siente que solo usted puede cuidar?",
    "¿Problemas económicos?",
    "¿No podrá seguir cuidando?",
    "¿Perdió control de su vida?",
    "¿Quiere dejar el cuidado?",
    "¿Se siente indeciso?",
    "¿Debería hacer más?",
    "¿Podría hacerlo mejor?",
    "¿Se siente sobrecargado?"
]

# ---------------------------
# FORMULARIO
# ---------------------------
with st.form("form_zarit"):

    st.subheader("Datos")

    edad = st.number_input("Edad", 18, 100)
    sexo = st.selectbox("Sexo", ["Femenino", "Masculino", "Otro"])
    parentesco = st.text_input("Parentesco")
    tiempo = st.text_input("Tiempo de cuidado")
    horas = st.text_input("Horas al día")
    barrio = st.text_input("Barrio")
    comuna = st.text_input("Comuna")

    st.subheader("Preguntas")

    respuestas = []
    for i, item in enumerate(ITEMS):
        r = st.radio(item, list(OPCIONES.keys()), key=i)
        respuestas.append(OPCIONES[r])

    guardar = st.form_submit_button("Guardar")

# ---------------------------
# GUARDAR
# ---------------------------
if guardar:

    puntaje = sum(respuestas)

    if puntaje <= 46:
        clasificacion = "Sin sobrecarga"
    elif puntaje <= 55:
        clasificacion = "Sobrecarga leve"
    else:
        clasificacion = "Sobrecarga intensa"

    fila = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        edad,
        sexo,
        parentesco,
        tiempo,
        horas,
        barrio,
        comuna,
    ] + respuestas + [puntaje, clasificacion]

    sheet.append_row(fila)

    st.success("Guardado correctamente")
