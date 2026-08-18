import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import io
import json
import re
import requests
import base64
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

# 1. Configuración de la página
st.set_page_config(page_title="Extractor SIRE - Estilo Yape", layout="wide")

# 2. INYECCIÓN DE DISEÑO ESTILO YAPE (MORADO + VERDE MENTA)
st.markdown("""
    <style>
    /* Fondo principal de la app en el clásico Morado Yape */
    .stApp { 
        background-color: #742284 !important; 
        font-family: 'Inter', sans-serif; 
    }
    
    /* Configuración de títulos principales */
    h1 { 
        color: #ffffff !important; 
        font-weight: 800 !important; 
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2); 
    }
    h2, h3, h4, .stMarkdown p, p, span, label { 
        color: #ffffff !important; 
    }
    
    /* Caja de carga de archivos (File Uploader) adaptada */
    .stFileUploader { 
        background-color: #8c339c !important; 
        border: 2px dashed #00e6b3 !important; 
        border-radius: 20px !important; 
        padding: 30px !important; 
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25) !important; 
    }
    
    /* Indicador de archivos cargados */
    .stFileUploader section {
        color: #ffffff !important;
    }

    /* Tarjetas de Métricas (Totales) en color Yape Profundo con borde Verde Menta */
    [data-testid="stMetric"] { 
        background-color: #5d196a !important; 
        border-left: 6px solid #00e6b3 !important; 
        border-radius: 12px !important; 
        padding: 20px !important; 
        box-shadow: 0 6px 15px rgba(0,0,0,0.15) !important;
    }
    
    /* Color de los montos económicos internos de las tarjetas (Verde Menta) */
    [data-testid="stMetricValue"] { 
        color: #00e6b3 !important; 
        font-weight: 800 !important; 
        font-size: 1.8rem !important;
    }
    
    /* Estilo para los botones de descarga */
    .stButton>button {
        background-color: #00e6b3 !important;
        color: #742284 !important;
        font-weight: bold !important;
        border-radius: 25px !important;
        border: none !important;
        padding: 10px 25px !important;
        transition: all 0.3s ease !important;
    }
    .stButton>button:hover {
        background-color: #ffffff !important;
        color: #742284 !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("💜 Extractor de Facturas Contable")
st.write("✨ **Interfaz Rediseñada:** Procesamiento paralelo de facturas con la potencia visual de tu billetera digital favorita.")

# ---- [El resto de tus funciones como analizar_un_archivo_con_ia y construir_diccionario permanecen exactamente igual] ----



