import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

st.title("Prueba conexión Google Sheets")

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

if st.button("Guardar prueba"):
    sheet.append_row([
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Edison",
        "Prueba OK"
    ])
    st.success("Dato guardado")
