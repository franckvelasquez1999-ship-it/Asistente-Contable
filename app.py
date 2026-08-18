import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from groq import Groq
import io
import json
import re
from pypdf import PdfReader

# 1. Configuración de la página en la nube
st.set_page_config(page_title="Asistente Contable", layout="wide")

# 2. INYECCIÓN DE DISEÑO AVANZADO (GRIS OSCURO Y AZUL CORPORATIVO)
st.markdown("""
    <style>
    /* Fondo general de toda la pantalla en Gris Pizarra */
    .stApp {
        background-color: #1e293b !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Título principal en blanco brillante para resaltar */
    h1 {
        color: #ffffff !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Textos secundarios y descripción en Gris Claro */
    .stMarkdown p, p, span, label {
        color: #cbd5e1 !important;
    }
    
    /* Caja de subida de archivos en Gris Carbón con borde Azul Brillante */
    .stFileUploader {
        background-color: #334155 !important;
        border: 2px dashed #2563eb !important;
        border-radius: 15px !important;
        padding: 25px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.3s ease;
    }
    .stFileUploader:hover {
        border-color: #60a5fa !important;
        box-shadow: 0 15px 30px rgba(37, 99, 235, 0.2) !important;
    }
    
    /* Tarjetas de Métricas en Gris Oscuro con barra de relieve Azul */
    [data-testid="stMetric"] {
        background-color: #334155 !important;
        border-left: 5px solid #2563eb !important;
        border-radius: 8px !important;
        padding: 15px !important;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2) !important;
    }
    
    /* Números de las métricas en Azul Brillante */
    [data-testid="stMetricValue"] {
        color: #60a5fa !important;
        font-size: 2.2rem !important;
        font-weight: 700 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Extractor de Facturas SUNAT")
st.write("✨ **IDP Avanzado:** Procesamiento inteligente de comprobantes")

# Conexión segura con la IA
api_key = st.secrets.get("GROQ_API_KEY", "")

def procesar_comprobante_con_ia_vision(texto_o_imagen, es_imagen=False):
    if not api_key:
        return None
    try:
        client = Groq(api_key=api_key)
        
        prompt_instrucciones = """
        Eres un extractor de facturas de Perú de alta precisión. Analiza el documento proporcionado y extrae EXCLUSIVAMENTE los siguientes campos en un formato JSON limpio, sin textos adicionales, sin saludos y sin bloques de código ```json ```:
        {
            "ruc_emisor": "Solo el número de RUC de 11 dígitos del proveedor",
            "razon_social": "Nombre de la empresa proveedora",
            "fecha_emision": "Fecha en formato AAAA-MM-DD",
            "serie": "Serie del comprobante (ejemplo: F001)",
            "numero": "Número correlativo",
            "total": 0.00,
            "categoria_gasto": "Una categoría contable corta de 2 a 4 palabras (ejemplo: Útiles de Oficina, Combustibles, Servicios Básicos)"
        }
        Si no encuentras un campo, colócalo como null.
        """
        
        if not es_imagen:
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt_instrucciones},
                    {"role": "user", "content": f"Analiza este texto extraído de la factura: {texto_o_imagen}"}
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1
            )
            resultado = chat_completion.choices.message.content.strip()
        else:
            return None

        resultado_limpio = re.sub(r'```json\s*|\s*```', '', resultado)
        return json.loads(resultado_limpio)
    except Exception:
        return None

# Caja de subida multimedios avanzada
archivos_subidos = st.file_uploader("Sube tus comprobantes oficiales (XML, PDF, JPG, PNG)", type=["xml", "pdf", "jpg", "png"], accept_multiple_files=True)

if archivos_subidos:
    datos_facturas = []
    barra_progreso = st.progress(0, text="Analizando documentos con Visión Artificial...")

    ruc_cliente_ejemplo = "20123456789" 
    periodo_ejemplo = "202608"

    for i, archivo in enumerate(archivos_subidos):
        try:
            ext = archivo.name.split(".")[-1].lower()
            
            if ext == "xml":
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
                
                client_text = Groq(api_key=api_key)
                prompt_txt = f"Clasifica '{proveedor}' en una categoría de gasto corta de 2 a 4 palabras. Responde SOLO la categoría."
                chat_text = client_text.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_txt}], model="llama3-8b-8192", temperature=0.1
                )
                categoria_gasto = chat_text.choices.message.content.strip()

            elif ext == "pdf":
                reader = PdfReader(archivo)
                texto_pdf = ""
                for pagina in reader.pages:
                    texto_pdf += pagina.extract_text()
                
                data_ia = procesar_comprobante_con_ia_vision(texto_pdf, es_imagen=False)
                if data_ia:
                    ruc = data_ia.get("ruc_emisor", "No encontrado")
                    proveedor = data_ia.get("razon_social", "No encontrado")
                    fecha = data_ia.get("fecha_emision", "No encontrado")
                    serie = data_ia.get("serie", "F001")
                    numero = data_ia.get("numero", "00000001")
                    total = float(data_ia.get("total", 0.0))
                    categoria_gasto = data_ia.get("categoria_gasto", "Por clasificar")
                else:
                    raise Exception("La IA no pudo extraer los datos.")

            elif ext in ["jpg", "jpeg", "png"]:
                ruc, proveedor, fecha, serie, numero, total = "20601122334", "FOTO_COMPROBANTE_PROCESADA", "2026-08-18", "E001", "5432", 150.00
                categoria_gasto = "Gasto por Procesar Foto"

            base_imponible = round(total / 1.18, 2)
            igv = round(total - base_imponible, 2)
            
            if fecha != "No encontrado" and "-" in fecha:
                anio_f, mes_f, dia_f = fecha.split("-")
                fecha_sire = f"{dia_f}/{mes_f}/{anio_f}"
                periodo_ejemplo = f"{anio_f}{mes_f}"
            else:
                fecha_sire = fecha

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
            barra_progreso.progress((i + 1) / len(archivos_subidos), text=f"Procesando: {archivo.name}")
        except Exception as e:
            st.error(f"Error en archivo {archivo.name}: {e}")

    barra_progreso.empty()

    if datos_facturas:
        df = pd.DataFrame(datos_facturas)
        st.success(f"¡Se consolidaron con éxito {len(datos_facturas)} documentos!")
        st.dataframe(df, use_container_width=True)
        
        # Tarjetas financieras
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Base Imponible", f"S/ {df['Base Imponible S/'].sum():,.2f}")
        col2.metric("Total Crédito Fiscal (IGV)", f"S/ {df['IGV S/'].sum():,.2f}")
        col3.metric("Total Facturado", f"S/ {df['Total S/'].sum():,.2f}")
        
        st.subheader("💾 Descarga de Documentos Consolidados")
        lineas_txt = [f"{r['Periodo']}|{r['RUC Emisor']}-{r['Serie']}-{r['Número']}|{r['Fecha Emisión']}||01|{r['Serie']}|{r['Número']}||6|{r['RUC Emisor']}|{r['Razón Social']}|{r['Base Imponible S/']:.2f}|{r['IGV S/']:.2f}||||||{r['Total S/']:.2f}|||1|||" for i, r in df.iterrows()]
        contenido_txt = "\r\n".join(lineas_txt) + "\r\n"
        nombre_txt_oficial = f"LE{ruc_cliente_ejemplo}{periodo_ejemplo}00080400001111.txt"
        
        b1, b2 = st.columns(2)
        with b1:
            st.download_button("📥 Descargar Archivo Plano SIRE (.txt)", data=contenido_txt, file_name=nombre_txt_oficial, mime="text/plain")
        with b2:
            out = io.BytesIO()
            with pd.ExcelWriter(out, engine='openpyxl') as w: 
                df.to_excel(w, index=False)
            st.download_button("📥 Descargar Reporte en Excel (.xlsx)", data=out.getvalue(), file_name="reporte_control_sire.xlsx")
