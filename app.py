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
    datos = sheet.get_all_values()
    if len(datos) <= 1:
        return "C001"
    try:
        ultimo = datos[-1][1]
        numero = int(ultimo.replace("C", ""))
        return f"C{numero+1:03d}"
    except:
        return "C001"

def clasificar(p):
    if p <= 46:
        return "Sin sobrecarga"
    elif p <= 55:
        return "Sobrecarga leve"
    return "Sobrecarga intensa"

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

    st.title("Test de Zarit - Bello")

    codigo = obtener_codigo()

    st.markdown(f"""
    <div style="background:#eef6ff;padding:15px;border-radius:10px">
    <b>Código asignado:</b> {codigo}
    </div>
    """, unsafe_allow_html=True)

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

    with st.form("form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            edad = st.number_input("Edad", 18, 120)
            sexo = st.selectbox("Sexo", ["Femenino", "Masculino", "Otro"])
            parentesco = st.selectbox(
                "Parentesco",
                ["Hija/o", "Esposa/o", "Madre/padre", "Hermana/o", "Otro", "No familiar"]
            )

        with col2:
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

        sheet.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            codigo,
            edad,
            sexo,
            parentesco,
            tiempo,
            horas,
            barrio,
            puntaje,
            clasif
        ])

        st.markdown(f"""
        <div style="background:#e3f2fd;border:3px solid #1565c0;
        padding:25px;border-radius:12px">

        <h2>Encuesta finalizada</h2>
        <h3>Código: {codigo}</h3>
        <h3>Puntaje: {puntaje}</h3>
        <h3>Clasificación: {clasif}</h3>

        <p>Puede continuar con el siguiente cuidador.</p>

        </div>
        """, unsafe_allow_html=True)

# =====================================
# ADMINISTRADOR
# =====================================
else:

    st.title("Panel de resultados")

    df = cargar_base()

    if df.empty:
        st.info("Sin datos")
    else:

        df["puntaje"] = pd.to_numeric(df["puntaje"], errors="coerce")

        col1, col2, col3 = st.columns(3)

        col1.metric("Registros", len(df))
        col2.metric("Promedio", round(df["puntaje"].mean(),2))
        col3.metric("Máximo", df["puntaje"].max())

        st.subheader("Clasificación")
        st.bar_chart(df["clasif"].value_counts())

        st.subheader("Puntajes")
        st.line_chart(df["puntaje"])

        st.subheader("Base de datos")
        st.dataframe(df)

        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Descargar CSV", csv, "zarit.csv")

        if st.button("Reiniciar base"):
            sheet.clear()
            sheet.append_row([
                "fecha","codigo","edad","sexo","parentesco",
                "tiempo","horas","barrio","puntaje","clasif"
            ])
            st.success("Base reiniciada")
