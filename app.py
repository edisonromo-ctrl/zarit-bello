import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# ---------------- CONFIG GOOGLE ----------------
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

# ---------------- FUNCIONES ----------------
def clasificar(puntaje):
    if puntaje <= 46:
        return "Sin sobrecarga"
    elif puntaje <= 55:
        return "Sobrecarga leve"
    else:
        return "Sobrecarga intensa"

# ---------------- UI ----------------
st.set_page_config(page_title="Zarit Bello", layout="centered")

st.title("Test de Zarit - Cuidadores")

st.markdown("Complete el formulario:")

# ---------------- FORMULARIO ----------------
with st.form("zarit_form", clear_on_submit=True):

    st.subheader("Datos del cuidador")

    edad = st.number_input("Edad", 18, 100)
    sexo = st.selectbox("Sexo", ["Femenino", "Masculino", "Otro"])

    parentesco = st.selectbox(
        "Parentesco",
        ["Hijo/a", "Esposo/a", "Padre/Madre", "Hermano/a", "Otro"]
    )

    tiempo = st.selectbox(
        "Tiempo de cuidado",
        ["<6 meses", "6-12 meses", "1-3 años", ">3 años"]
    )

    horas = st.selectbox(
        "Horas al día",
        ["<4", "4-8", "8-12", ">12"]
    )

    barrio = st.text_input("Barrio")

    st.subheader("Cuestionario")

    opciones = ["Nunca", "Rara vez", "A veces", "Frecuentemente", "Siempre"]
    valores = {"Nunca":0, "Rara vez":1, "A veces":2, "Frecuentemente":3, "Siempre":4}

    preguntas = [
        "¿Siente que su familiar solicita más ayuda de la que necesita?",
        "¿No tiene tiempo suficiente para usted?",
        "¿Se siente estresado?",
        "¿Se siente avergonzado?",
        "¿Se siente enojado?",
        "¿Afecta su relación con otros?",
        "¿Siente temor por el futuro?",
        "¿Siente dependencia del paciente?",
        "¿Se siente tenso?",
        "¿Ha empeorado su salud?",
        "¿Tiene menos privacidad?",
        "¿Afecta su vida social?",
        "¿Evita invitar personas?",
        "¿Siente que solo usted puede cuidarlo?",
        "¿Problemas económicos?",
        "¿No podrá continuar cuidando?",
        "¿Perdió el control de su vida?",
        "¿Desea delegar el cuidado?",
        "¿Se siente indeciso?",
        "¿Cree que debería hacer más?",
        "¿Cree que podría hacerlo mejor?",
        "¿Se siente sobrecargado?"
    ]

    respuestas = []

    for i, p in enumerate(preguntas, 1):
        r = st.radio(f"{i}. {p}", opciones, key=i)
        respuestas.append(valores[r])

    enviar = st.form_submit_button("Finalizar encuesta")

# ---------------- PROCESO ----------------
if enviar:

    puntaje = sum(respuestas)
    clasif = clasificar(puntaje)

    # Guardar en Google Sheets
    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        edad,
        sexo,
        parentesco,
        tiempo,
        horas,
        barrio,
        puntaje,
        clasif
    ])

    # MENSAJE VISUAL FUERTE
    st.markdown("---")
    st.markdown(
        f"""
        <div style="background:#e8f5e9;padding:20px;border-radius:10px">
        <h2 style="color:green;">Resultado guardado</h2>
        <h3>Puntaje: {puntaje}</h3>
        <h3>Clasificación: {clasif}</h3>
        <p>Puede continuar con el siguiente cuidador.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
