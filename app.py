import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pandas as pd

# =====================================
# CONFIG
# =====================================
st.set_page_config(page_title="Zarit Bello", layout="wide")

# =====================================
# GOOGLE SHEETS
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
# FUNCIONES
# =====================================
def obtener_codigo():
    data = sheet.col_values(2)
    if len(data) <= 1:
        return "C001"
    try:
        numero = int(data[-1].replace("C", ""))
        return f"C{numero+1:03d}"
    except:
        return "C001"

def clasificar(p):
    if p <= 46:
        return "Sin sobrecarga"
    elif p <= 55:
        return "Sobrecarga leve"
    return "Sobrecarga intensa"

def generar_alerta(puntaje, horas_dia, tiempo_cuidado):
    alerta = "🟢 Baja"
    color = "#2e7d32"
    mensaje = "Sin riesgo clínico relevante."

    if puntaje >= 56:
        alerta = "🔴 Alta"
        color = "#c62828"
        mensaje = "Sobrecarga intensa. Requiere intervención."
    elif puntaje >= 47:
        alerta = "🟡 Media"
        color = "#f9a825"
        mensaje = "Riesgo de sobrecarga."

    if horas_dia == "Más de 12":
        alerta = "🔴 Alta"
        color = "#c62828"
        mensaje = "Sobrecarga crítica por tiempo de cuidado."

    if tiempo_cuidado == "Más de 3 años":
        alerta = "🔴 Alta"
        color = "#c62828"
        mensaje = "Fatiga del cuidador a largo plazo."

    return alerta, color, mensaje

def cargar_base():
    data = sheet.get_all_values()
    if len(data) <= 1:
        return pd.DataFrame()
    return pd.DataFrame(data[1:], columns=data[0])

# =====================================
# SIDEBAR
# =====================================
modo = st.sidebar.radio("Modo", ["Aplicación", "Administrador"])

# =====================================
# APLICACIÓN
# =====================================
if modo == "Aplicación":

    st.title("Test de Zarit")

    codigo = obtener_codigo()
    st.info(f"Código asignado: {codigo}")

    OPCIONES = {
        "Nunca": 0,
        "Rara vez": 1,
        "Algunas veces": 2,
        "Bastantes veces": 3,
        "Casi siempre": 4
    }

    ITEMS = [
        "Solicita más ayuda de la necesaria",
        "No tiene tiempo para usted",
        "Se siente estresado",
        "Se siente avergonzado",
        "Se siente enojado",
        "Afecta relaciones",
        "Temor por el futuro",
        "Dependencia del paciente",
        "Se siente tenso",
        "Salud ha empeorado",
        "Falta de privacidad",
        "Afecta vida social",
        "Evita visitas",
        "Solo usted puede cuidar",
        "Problemas económicos",
        "No podrá continuar",
        "Perdió control",
        "Desea delegar",
        "Indecisión",
        "Debe hacer más",
        "Podría hacerlo mejor",
        "Sobrecarga general"
    ]

    with st.form("formulario", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            edad = st.number_input("Edad", 18, 120)
            sexo = st.selectbox("Sexo", ["Femenino", "Masculino", "Otro"])
            parentesco = st.selectbox("Parentesco",
                ["Hija/o","Esposa/o","Madre/padre","Hermana/o","Otro","No familiar"]
            )

        with col2:
            tiempo = st.selectbox("Tiempo de cuidado",
                ["Menos de 6 meses","6 meses a 1 año","1 a 3 años","Más de 3 años"]
            )
            horas = st.selectbox("Horas al día",
                ["Menos de 4","4 a 8","8 a 12","Más de 12"]
            )
            barrio = st.text_input("Barrio")

        st.subheader("Cuestionario")

        respuestas = []
        for i, item in enumerate(ITEMS, 1):
            r = st.radio(f"{i}. {item}", list(OPCIONES.keys()), key=i)
            respuestas.append(OPCIONES[r])

        enviar = st.form_submit_button("Finalizar encuesta")

    if enviar:

        if not barrio.strip():
            st.error("Debe ingresar el barrio")
            st.stop()

        puntaje = sum(respuestas)
        clasif = clasificar(puntaje)

        alerta, color_alerta, mensaje_alerta = generar_alerta(
            puntaje,
            horas,
            tiempo
        )

        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            codigo,
            edad,
            sexo,
            parentesco,
            tiempo,
            horas,
            barrio,
            *respuestas,
            puntaje,
            clasif,
            alerta
        ])

        st.markdown(f"""
        <div style='padding:20px;border-radius:10px;background:{color_alerta};color:white'>
        <h2>Encuesta finalizada</h2>
        <b>Código:</b> {codigo}<br>
        <b>Puntaje:</b> {puntaje}<br>
        <b>Clasificación:</b> {clasif}<br>
        <b>Alerta:</b> {alerta}<br><br>
        {mensaje_alerta}
        </div>
        """, unsafe_allow_html=True)

# =====================================
# ADMINISTRADOR
# =====================================
else:

    st.title("Panel clínico")

    df = cargar_base()

    if df.empty:
        st.warning("Sin datos")
    else:

        df["puntaje"] = pd.to_numeric(df["puntaje"], errors="coerce")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total", len(df))
        col2.metric("Promedio", round(df["puntaje"].mean(),2))
        col3.metric("Alto riesgo %",
            round((df["clasif"]=="Sobrecarga intensa").mean()*100,1)
        )

        st.subheader("Clasificación")
        st.bar_chart(df["clasif"].value_counts())

        st.subheader("Alertas")
        st.bar_chart(df["alerta"].value_counts())

        st.subheader("Puntajes")
        st.line_chart(df["puntaje"])

        st.subheader("Base de datos")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar CSV", csv, "zarit.csv")
