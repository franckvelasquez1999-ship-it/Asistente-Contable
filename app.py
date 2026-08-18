import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from groq import Groq
import io

# 1. Configuración de la página en la nube
st.set_page_config(page_title="Asistente Contable", layout="wide")

# 2. INYECCIÓN DE DISEÑO PREMIUM (CSS)
st.markdown("""
    <style>
    /* Estilo para el fondo general y tipografía */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Estilo para los títulos principales */
    h1 {
        color: #1e293b !important;
        font-weight: 800 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    /* Estilización del cuadro de subida de archivos */
    .stFileUploader {
        background-color: #ffffff !important;
        border: 2px dashed #3b82f6 !important;
        border-radius: 15px !important;
        padding: 25px !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.3s ease;
    }
    .stFileUploader:hover {
        border-color: #1d4ed8 !important;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1) !important;
    }
    /* Estilo para las métricas y tarjetas de impuestos */
    [data-testid="stMetricValue"] {
        color: #1e3a8a !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetric"] {
        background-color: #ffffff !important;
        border-left: 5px solid #3b82f6 !important;
        border-radius: 8px !important;
        padding: 15px !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Contenido de la interfaz
st.title("📊 Extractor de Facturas SUNAT")
st.write("✨ **Plataforma Corporativa de Gestión Fiscal:** Procesamiento automatizado para el SIRE - SUNAT.")

# Conexión segura con la IA en la nube (Groq)
api_key = st.secrets.get("GROQ_API_KEY", "")

def clasificar_gasto_con_ia_nube(razon_social):
    if not api_key:
        return "Configurar API Key"
    try:
        client = Groq(api_key=api_key)
        prompt = f"Clasifica el proveedor '{razon_social}' en una categoría de gasto corta de 2 a 4 palabras (Ejemplos: Útiles de Oficina, Servicios Básicos, Combustibles). Responde ÚNICAMENTE la categoría."
        
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.1
        )
        return chat_completion.choices.message.content.strip()
    except Exception:
        return "Por clasificar"

# Caja para subir archivos
archivos_xml = st.file_uploader("Sube tus archivos XML oficiales de la SUNAT", type=["xml"], accept_multiple_files=True)

if archivos_xml:
    datos_facturas = []
    barra_progreso = st.progress(0, text="Procesando archivos y estructurando formato SIRE...")

    ruc_cliente_ejemplo = "20123456789" 
    periodo_ejemplo = "202608" 

    for i, archivo in enumerate(archivos_xml):
        try:
            tree = ET.parse(archivo)
            root = tree.getroot()
            
            serie_num = root.find(".//{*}ID")
            fecha_emision = root.find(".//{*}IssueDate")
            ruc_emisor = root.find(".//{*}AccountingSupplierParty//{*}CustomerAssignedAccountID")
            nombre_emisor = root.find(".//{*}AccountingSupplierParty//{*}RegistrationName")
            monto_total_xml = root.find(".//{*}LegalMonetaryTotal//{*}PayableAmount")
            
            ruc = ruc_emisor.text if ruc_emisor is not None else "No encontrado"
            proveedor = nombre_emisor.text if nombre_emisor is not None else "No encontrado"
            fecha = fecha_emision.text if fecha_emision is not None else "No encontrado"
            
            id_comprobante = serie_num.text if serie_num is not None else "F001-00000001"
            serie, numero = id_comprobante.split("-", 1) if "-" in id_comprobante else (id_comprobante[:4], id_comprobante[4:])

            total = float(monto_total_xml.text) if monto_total_xml is not None else 0.0
            base_imponible = round(total / 1.18, 2)
            igv = round(total - base_imponible, 2)
            
            if fecha != "No encontrado" and "-" in fecha:
                anio_f, mes_f, dia_f = fecha.split("-")
                fecha_sire = f"{dia_f}/{mes_f}/{anio_f}"
                periodo_ejemplo = f"{anio_f}{mes_f}"
            else:
                fecha_sire = fecha

            categoria_gasto = clasificar_gasto_con_ia_nube(proveedor)
            
            datos_facturas.append({
                "Periodo": periodo_ejemplo,
                "Fecha Emisión": fecha_sire,
                "Tipo Comp.": "01",
                "Serie": serie,
                "Número": numero,
                "Tipo Doc Identidad": "6",
                "RUC Emisor": ruc,
                "Razón Social": proveedor,
                "Base Imponible S/": base_imponible,
                "IGV S/": igv,
                "Total S/": total,
                "Categoría IA (Gasto)": categoria_gasto
            })
            barra_progreso.progress((i + 1) / len(archivos_xml), text=f"Estructurando: {proveedor}")
        except Exception as e:
            st.error(f"Error: {e}")

    barra_progreso.empty()

    if datos_facturas:
        df = pd.DataFrame(datos_facturas)
        st.success(f"¡Se estructuraron con éxito {len(datos_facturas)} facturas para el SIRE!")
        st.dataframe(df, use_container_width=True)
        
        # Resumen de tarjetas tributarias estilizadas por CSS
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Base Imponible", f"S/ {df['Base Imponible S/'].sum():,.2f}")
        col2.metric("Total Crédito Fiscal (IGV)", f"S/ {df['IGV S/'].sum():,.2f}")
        col3.metric("Total Facturado", f"S/ {df['Total S/'].sum():,.2f}")
        
        st.subheader("💾 Descarga de Archivos de Declaración")
        
        lineas_txt = []
        for index, row in df.iterrows():
            linea = f"{row['Periodo']}|{row['RUC Emisor']}-{row['Serie']}-{row['Número']}|{row['Fecha Emisión']}||{row['Tipo Comp.']}|{row['Serie']}|{row['Número']}||{row['Tipo Doc Identidad']}|{row['RUC Emisor']}|{row['Razón Social']}|{row['Base Imponible S/']:.2f}|{row['IGV S/']:.2f}||||||{row['Total S/']:.2f}|||1|||"
            lineas_txt.append(linea)
        
        contenido_txt = "\r\n".join(lineas_txt) + "\r\n"
        nombre_txt_oficial = f"LE{ruc_cliente_ejemplo}{periodo_ejemplo}00080400001111.txt"
        
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            st.download_button(
                label="📥 Descargar Archivo Plano SIRE (.txt)",
                data=contenido_txt,
                file_name=nombre_txt_oficial,
                mime="text/plain"
            )
            st.caption("Usa este archivo para subirlo directamente a la plataforma SIRE de la SUNAT.")
            
        with btn_col2:
            output_excel = io.BytesIO()
            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Reporte SIRE')
            data_excel = output_excel.getvalue()
            
            st.download_button(
                label="📥 Descargar Reporte en Excel (.xlsx)",
                data=data_excel,
                file_name="reporte_control_sire.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

