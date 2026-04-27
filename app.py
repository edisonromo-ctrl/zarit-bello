import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# =====================================
# CONEXIÓN GOOGLE SHEETS
# =====================================
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

# =====================================
# CONFIG
# =====================================
st.set_page_config(
    page_title="Test de Zarit",
    page_icon="🩺",
    layout="centered"
)

# =====================================
# ESTILOS
# =====================================
st.markdown("""
<style>
.resultado {
    background: #e8f5e9;
    border: 2px solid #2e7d32;
    border-radius: 12px;
    padding: 20px;
    margin-top: 20px;
}
.resultado h2 {
    color: #1b5e20;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# ITEMS
# =====================================
ITEMS_ZARIT = [
    "¿Siente que su familiar solicita más ayuda de la que realmente necesita?",
    "¿Siente que no tiene tiempo para usted?",
    "¿Se siente estresado(a)?",
    "¿Se siente avergonzado(a)?",
    "¿Se siente enojado(a)?",
    "¿Afecta su relación con otros?",
    "¿Siente temor por el futuro?",
    "¿Siente dependencia del paciente?",
    "¿Se siente tenso(a)?",
    "¿Ha empeorado su salud?",
    "¿No tiene privacidad?",
    "¿Su vida social se afectó?",
    "¿Evita invitar personas?",
    "¿Siente que solo usted puede cuidar?",
    "¿Problemas económicos?",
    "¿No podrá continuar cuidando?",
    "¿Perdió el control de su vida?",
    "¿Desea delegar el cuidado?",
    "¿Se siente indeciso?",
    "¿Debería hacer más?",
    "¿Podría hacerlo mejor?",
    "¿Se siente sobrecargado?"
]

OPCIONES = {
    "Nunca": 0,
    "Rara vez": 1,
    "Algunas veces": 2,
    "Bastantes veces": 3,
    "Casi siempre": 4
}

# =====================================
# CLASIFICACIÓN
# =====================================
def clasificar(p):
    if p <= 46:
        return "Sin sobrecarga"
    elif p <= 55:
        return "Sobrecarga leve"
    return "Sobrecarga intensa"

# =====================================
# UI
# =====================================
st.title("Test de Zarit")

with st.form("form_zarit", clear_on_submit=True):

    st.subheader("Datos del cuidador")

    col1, col2 = st.columns(2)

    with col1:
        edad = st.number_input("Edad", 18, 120)
        sexo = st.selectbox("Sexo", ["Femenino", "Masculino", "Otro"])
        parentesco = st.selectbox(
            "Parentesco",
            ["Hija/o", "Esposa/o", "Madre/padre", "Hermana/o", "Otro familiar", "Cuidador no familiar"]
        )

    with col2:
        tiempo = st.selectbox(
            "Tiempo de cuidado",
            ["Menos de 6 meses", "6 meses a 1 año", "1 a 3 años", "Más de 3 años"]
        )
        horas = st.selectbox(
            "Horas al día",
            ["Menos de 4", "4 a 8", "8 a 12", "Más de 12"]
        )
        barrio = st.text_input("Barrio")

    st.subheader("Cuestionario")

    respuestas = []
    for i, item in enumerate(ITEMS_ZARIT, 1):
        r = st.radio(f"{i}. {item}", list(OPCIONES.keys()), key=i)
        respuestas.append(OPCIONES[r])

    enviar = st.form_submit_button("Finalizar encuesta")

# =====================================
# PROCESO
# =====================================
if enviar:

    if not barrio.strip():
        st.error("Debe ingresar el barrio")
    else:
        puntaje = sum(respuestas)
        clasif = clasificar(puntaje)

        # GUARDAR EN GOOGLE SHEETS
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

        # RESULTADO VISUAL
        st.markdown(f"""
        <div class="resultado">
            <h2>Resultado registrado</h2>
            <h3>Puntaje total: {puntaje}</h3>
            <h3>Clasificación: {clasif}</h3>
            <p>Puede continuar con el siguiente cuidador.</p>
        </div>
        """, unsafe_allow_html=True)
