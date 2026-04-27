import os
from datetime import datetime

import pandas as pd
import streamlit as st


# =====================================
# CONFIGURACIÓN GENERAL
# =====================================
st.set_page_config(
    page_title="Test de Zarit - Comuna 1 de Bello",
    page_icon="🩺",
    layout="centered"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
ARCHIVO_CSV = os.path.join(DATA_DIR, "respuestas_zarit.csv")
ARCHIVO_XLSX = os.path.join(DATA_DIR, "respuestas_zarit.xlsx")

os.makedirs(DATA_DIR, exist_ok=True)

st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }

    .main-header {
        background: linear-gradient(135deg, #1f4e79 0%, #2f6da3 100%);
        padding: 1.4rem 1.5rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 1rem;
        box-shadow: 0 6px 18px rgba(31, 78, 121, 0.18);
    }

    .main-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }

    .main-subtitle {
        font-size: 1rem;
        opacity: 0.95;
    }

    .info-card {
        background: #f7fbff;
        border: 1px solid #d9eaf7;
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
    }

    .code-card {
        background: #eef7ff;
        border: 1px solid #bddcf6;
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        font-size: 1.05rem;
        font-weight: 600;
        color: #1f4e79;
    }

    .success-card {
        background: #eefaf1;
        border: 1px solid #b9e0c4;
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin-bottom: 1rem;
        color: #185c2d;
    }

    .section-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-top: 0.7rem;
        margin-bottom: 0.6rem;
        color: #1f1f1f;
    }

    .small-note {
        color: #5a5a5a;
        font-size: 0.95rem;
        margin-bottom: 0.6rem;
    }

    div[data-testid="stForm"] {
        background: white;
        border: 1px solid #e9eef3;
        border-radius: 18px;
        padding: 1.2rem 1.2rem 0.8rem 1.2rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
    }

    div[data-testid="stMetric"] {
        background: #fafcff;
        border: 1px solid #e4edf5;
        border-radius: 14px;
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# =====================================
# ÍTEMS DEL TEST DE ZARIT
# =====================================
ITEMS_ZARIT = [
    "¿Siente que su familiar solicita más ayuda de la que realmente necesita?",
    "¿Siente que por el tiempo que dedica a su familiar no tiene suficiente tiempo para usted?",
    "¿Se siente estresado(a) al tener que cuidar a su familiar y atender además otras responsabilidades?",
    "¿Se siente avergonzado(a) por la conducta de su familiar?",
    "¿Se siente enojado(a) cuando está cerca de su familiar?",
    "¿Cree que la situación actual afecta negativamente su relación con amigos u otros familiares?",
    "¿Siente temor por el futuro que le espera a su familiar?",
    "¿Siente que su familiar depende de usted?",
    "¿Se siente tenso(a) cuando está cerca de su familiar?",
    "¿Siente que su salud ha empeorado por tener que cuidar a su familiar?",
    "¿Siente que no tiene tanta privacidad como le gustaría por cuidar a su familiar?",
    "¿Cree que su vida social se ha visto afectada negativamente por cuidar a su familiar?",
    "¿Se siente incómodo(a) por invitar amigos a casa, debido a su familiar?",
    "¿Cree que su familiar espera que usted lo cuide como si fuera la única persona con quien puede contar?",
    "¿Cree que no tiene suficiente dinero para cuidar a su familiar además de sus otros gastos?",
    "¿Siente que no podrá seguir cuidando a su familiar por mucho más tiempo?",
    "¿Siente que ha perdido el control de su vida desde que comenzó la enfermedad de su familiar?",
    "¿Desearía poder dejar el cuidado de su familiar a otra persona?",
    "¿Se siente indeciso(a) sobre qué hacer con su familiar?",
    "¿Siente que debería hacer más por su familiar?",
    "¿Cree que podría cuidar mejor a su familiar?",
    "En general, ¿se siente muy sobrecargado(a) por tener que cuidar a su familiar?"
]

OPCIONES = {
    "Nunca": 0,
    "Rara vez": 1,
    "Algunas veces": 2,
    "Bastantes veces": 3,
    "Casi siempre": 4
}


# =====================================
# FUNCIONES
# =====================================
def clasificar_sobrecarga(puntaje: int) -> str:
    if puntaje <= 46:
        return "Sin sobrecarga"
    elif puntaje <= 55:
        return "Sobrecarga leve"
    return "Sobrecarga intensa"


def cargar_base() -> pd.DataFrame:
    if os.path.exists(ARCHIVO_CSV):
        try:
            return pd.read_csv(ARCHIVO_CSV)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()


def siguiente_codigo(df: pd.DataFrame) -> str:
    if df.empty or "codigo" not in df.columns:
        return "C001"

    codigos = df["codigo"].dropna().astype(str).tolist()
    numeros = []

    for codigo in codigos:
        codigo = codigo.strip().upper()
        if codigo.startswith("C"):
            parte = codigo[1:]
            if parte.isdigit():
                numeros.append(int(parte))

    if not numeros:
        return "C001"

    return f"C{max(numeros) + 1:03d}"


def guardar_respuesta(registro: dict) -> None:
    df_actual = cargar_base()
    nuevo = pd.DataFrame([registro])
    df_final = pd.concat([df_actual, nuevo], ignore_index=True)

    df_final.to_csv(ARCHIVO_CSV, index=False, encoding="utf-8-sig")
    df_final.to_excel(ARCHIVO_XLSX, index=False)


def obtener_resumen(df: pd.DataFrame) -> dict:
    if df.empty:
        return {"n_respuestas": 0, "promedio": 0, "minimo": 0, "maximo": 0}

    return {
        "n_respuestas": len(df),
        "promedio": round(df["puntaje_total"].mean(), 2),
        "minimo": int(df["puntaje_total"].min()),
        "maximo": int(df["puntaje_total"].max())
    }


# =====================================
# ESTADO DE SESIÓN
# =====================================
if "ultimo_registro" not in st.session_state:
    st.session_state.ultimo_registro = None

if "reset_form_counter" not in st.session_state:
    st.session_state.reset_form_counter = 0


# =====================================
# CABECERA
# =====================================
st.markdown("""
<div class="main-header">
    <div class="main-title">Test de Zarit</div>
    <div class="main-subtitle">Cuidadores de pacientes crónicos · Comuna 1 de Bello</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="info-card">
Esta herramienta hace parte del proyecto académico orientado a identificar la sobrecarga
en cuidadores de pacientes crónicos de la comuna 1 de Bello.
</div>
""", unsafe_allow_html=True)

df_base = cargar_base()
codigo_auto = siguiente_codigo(df_base)

st.markdown(
    f'<div class="code-card">Código asignado automáticamente: {codigo_auto}</div>',
    unsafe_allow_html=True
)

if st.session_state.ultimo_registro:
    ultimo = st.session_state.ultimo_registro
    st.markdown(
        f"""
        <div class="success-card">
        <b>Respuesta guardada correctamente.</b><br><br>
        Código asignado: {ultimo['codigo']}<br>
        Puntaje total Zarit: {ultimo['puntaje_total']}<br>
        Clasificación: {ultimo['clasificacion']}<br><br>
        El formulario ya quedó listo automáticamente para el siguiente cuidador.
        </div>
        """,
        unsafe_allow_html=True
    )


# =====================================
# FORMULARIO
# =====================================
with st.form(f"formulario_zarit_{st.session_state.reset_form_counter}", clear_on_submit=True):
    st.markdown('<div class="section-title">1. Consentimiento</div>', unsafe_allow_html=True)
    consentimiento = st.radio(
        "¿Acepta participar voluntariamente en este formulario?",
        ["Sí", "No"],
        horizontal=True
    )

    st.markdown('<div class="section-title">2. Datos del cuidador</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        edad = st.number_input("Edad", min_value=18, max_value=120, step=1)
        sexo = st.selectbox("Sexo", ["Femenino", "Masculino", "Otro"])
        parentesco = st.selectbox(
            "Parentesco con el paciente",
            ["Hija/o", "Esposa/o", "Madre/padre", "Hermana/o", "Otro familiar", "Cuidador no familiar"]
        )
    with col2:
        tiempo_cuidado = st.selectbox(
            "Tiempo ejerciendo el cuidado",
            ["Menos de 6 meses", "6 meses a 1 año", "1 a 3 años", "Más de 3 años"]
        )
        horas_dia = st.selectbox(
            "Horas al día dedicadas al cuidado",
            ["Menos de 4 horas", "4 a 8 horas", "8 a 12 horas", "Más de 12 horas"]
        )
        barrio = st.text_input("Barrio o sector")
        comuna = st.text_input("Comuna", value="Comuna 1")

    st.markdown('<div class="section-title">3. Cuestionario Zarit</div>', unsafe_allow_html=True)
    st.markdown('<div class="small-note">Seleccione la frecuencia con la que ha sentido cada situación.</div>', unsafe_allow_html=True)

    respuestas = {}
    for i, item in enumerate(ITEMS_ZARIT, start=1):
        respuesta_texto = st.radio(
            f"{i}. {item}",
            list(OPCIONES.keys()),
            key=f"item_{i}_{st.session_state.reset_form_counter}"
        )
        respuestas[f"item_{i}"] = OPCIONES[respuesta_texto]

    enviar = st.form_submit_button("Guardar respuesta", type="primary", use_container_width=True)


# =====================================
# PROCESAMIENTO
# =====================================
if enviar:
    if consentimiento != "Sí":
        st.error("No se puede continuar sin consentimiento.")
    elif not barrio.strip():
        st.error("Debe ingresar el barrio o sector.")
    else:
        puntaje_total = sum(respuestas.values())
        clasificacion = clasificar_sobrecarga(puntaje_total)

        registro = {
            "fecha_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "codigo": codigo_auto,
            "edad": edad,
            "sexo": sexo,
            "parentesco": parentesco,
            "tiempo_cuidado": tiempo_cuidado,
            "horas_dia": horas_dia,
            "barrio": barrio.strip(),
            "comuna": comuna.strip(),
            **respuestas,
            "puntaje_total": puntaje_total,
            "clasificacion": clasificacion
        }

        guardar_respuesta(registro)

        st.session_state.ultimo_registro = {
            "codigo": codigo_auto,
            "puntaje_total": puntaje_total,
            "clasificacion": clasificacion
        }

        st.session_state.reset_form_counter += 1
        st.rerun()


# =====================================
# PANEL TÉCNICO
# =====================================
st.markdown("---")

with st.expander("Ver base consolidada y resumen técnico"):
    df_base = cargar_base()

    if not df_base.empty:
        resumen = obtener_resumen(df_base)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Respuestas", resumen["n_respuestas"])
        col2.metric("Promedio", resumen["promedio"])
        col3.metric("Mínimo", resumen["minimo"])
        col4.metric("Máximo", resumen["maximo"])

        st.dataframe(df_base, use_container_width=True)

        csv_bytes = df_base.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            label="Descargar CSV",
            data=csv_bytes,
            file_name="respuestas_zarit.csv",
            mime="text/csv",
            use_container_width=True
        )

        with open(ARCHIVO_XLSX, "rb") as f:
            st.download_button(
                label="Descargar Excel",
                data=f,
                file_name="respuestas_zarit.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
    else:
        st.caption("Aún no hay respuestas registradas.")
