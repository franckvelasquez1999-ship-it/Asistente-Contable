import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from groq import Groq

# Configuración de la pestaña en la nube
st.set_page_config(page_title="Asistente Contable", layout="wide")

st.title("📊 Extractor de Facturas SUNAT ")
st.write("Sistema en la nube con cálculo automático de impuestos y clasificación inteligente de gastos.")

# Conexión segura con la IA en la nube (Groq)
# En la nube, la llave de seguridad se guarda de forma privada en los ajustes de Streamlit
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
        return chat_completion.choices[0].message.content.strip()
    except Exception:
        return "Por clasificar"

# Caja para subir archivos en la nube
archivos_xml = st.file_uploader("Sube tus archivos XML oficiales de la SUNAT", type=["xml"], accept_multiple_files=True)

if archivos_xml:
    datos_facturas = []
    barra_progreso = st.progress(0, text="Procesando archivos en la nube...")

    for i, archivo in enumerate(archivos_xml):
        try:
            tree = ET.parse(archivo)
            root = tree.getroot()
            
            # Extraer datos con comodines universales de SUNAT
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

            # Cálculos automáticos de impuestos peruanos
            total = float(monto_total_xml.text) if monto_total_xml is not None else 0.0
            base_imponible = round(total / 1.18, 2)
            igv = round(total - base_imponible, 2)
            
            # Consultar a la IA en la nube
            categoria_gasto = clasificar_gasto_con_ia_nube(proveedor)
            
            datos_facturas.append({
                "Fecha Emisión": fecha,
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
            barra_progreso.progress((i + 1) / len(archivos_xml), text=f"Procesando: {proveedor}")
        except Exception as e:
            st.error(f"Error: {e}")

    barra_progreso.empty()

    if datos_facturas:
        df = pd.DataFrame(datos_facturas)
        st.success(f"¡Se procesaron con éxito {len(datos_facturas)} facturas!")
        st.dataframe(df, use_container_width=True)
        
        # Resumen de tarjetas
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Base Imponible", f"S/ {df['Base Imponible S/'].sum():,.2f}")
        col2.metric("Total Crédito Fiscal (IGV)", f"S/ {df['IGV S/'].sum():,.2f}")
        col3.metric("Total Facturado", f"S/ {df['Total S/'].sum():,.2f}")
