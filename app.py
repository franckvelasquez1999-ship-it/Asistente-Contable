import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import google.generativeai as genai
import io
import json
import re
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

# 1. Configuración de la página en la nube
st.set_page_config(page_title="Asistente Contable", layout="wide")

# 2. INYECCIÓN DE DISEÑO AVANZADO CORPORATIVO
st.markdown("""
    <style>
    .stApp { background-color: #1e293b !important; font-family: sans-serif; }
    h1 { color: #ffffff !important; font-weight: 800 !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
    .stMarkdown p, p, span, label { color: #cbd5e1 !important; }
    .stFileUploader { background-color: #334155 !important; border: 2px dashed #2563eb !important; border-radius: 15px !important; padding: 25px !important; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3) !important; }
    [data-testid="stMetric"] { background-color: #334155 !important; border-left: 5px solid #2563eb !important; border-radius: 8px !important; padding: 15px !important; }
    [data-testid="stMetricValue"] { color: #60a5fa !important; font-weight: 700 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Extractor de Facturas SUNAT")
st.write("✨ **Motor de Alta Velocidad (Paralelo):** Procesamiento instantáneo de XML, PDF e imágenes con compresión automática e IA Google Gemini.")

# Configurar la conexión con Gemini
api_key = st.secrets.get("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

# FUNCIÓN PARA NORMALIZAR EXTRACTOS DE FECHA DE MANERA SEGURA
def normalizar_fecha(texto_fecha):
    if not texto_fecha or texto_fecha == "No encontrado":
        return "No encontrado"
    # Extraer los dígitos numéricos encontrados en la cadena
    numeros = re.findall(r'\d+', texto_fecha)
    if len(numeros) >= 3:
        # Si viene como YYYY, MM, DD
        if len(numeros[0]) == 4:
            return f"{numeros[0]}-{numeros[1].zfill(2)}-{numeros[2].zfill(2)}"
        # Si viene como DD, MM, YYYY
        elif len(numeros[2]) == 4:
            return f"{numeros[2]}-{numeros[1].zfill(2)}-{numeros[0].zfill(2)}"
    return "No encontrado"

# FUNCIÓN INDEPENDIENTE PARA PROCESAR CON LA IA
def analizar_un_archivo_con_ia(archivo):
    try:
        ext = archivo.name.split(".")[-1].lower()
        bytes_archivo = archivo.read()
        
        if ext == "xml":
            archivo.seek(0)
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
            
            model_text = genai.GenerativeModel('gemini-1.5-flash')
            res_txt = model_text.generate_content(f"Clasifica '{proveedor}' en una categoría de gasto contable empresarial de 2 a 4 palabras. Responde SOLO la categoría sin puntuación.")
            categoria_gasto = res_txt.text.strip()
            
            return construir_diccionario_factura(fecha, serie, numero, ruc, proveedor, total, categoria_gasto, archivo.name)

        # PROMPT ULTRA-ESTRICTO CORREGIDO PARA EVITAR EL "NO ENCONTRADO"
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = """
        Analiza este documento contable de Perú de forma exhaustiva y extrae la información requerida.
        Entrega la respuesta EXCLUSIVAMENTE en un formato JSON plano, válido, sin textos alternativos ni bloques markdown de código.
        
        Reglas obligatorias de extracción:
        1. 'ruc_emisor': Busca el número de 11 dígitos que empieza por 10 o 20 (RUC del Proveedor). No te confundas con el RUC del cliente.
        2. 'razon_social': Nombre de la empresa emisora que vende el servicio/producto.
        3. 'fecha_emision': Devuélvela estrictamente en formato AAAA-MM-DD.
        4. 'serie': Código alfa-numérico de 4 caracteres (Ej: F001, E001).
        5. 'numero': El número correlativo de la factura (omite ceros a la izquierda sobrantes si lo deseas, pero mantén consistencia).
        6. 'total': Monto total final cobrado como número flotante (remueve símbolos S/ o comas).
        7. 'categoria_gasto': Analiza el nombre de la empresa emisora y asígnale una categoría de gasto (Ej: 'Gastos de Alimentos', 'Servicios Básicos', 'Útiles de Oficina', 'Software').

        Formato de salida esperado:
        {"ruc_emisor": "11_digitos", "razon_social": "TEXTO", "fecha_emision": "AAAA-MM-DD", "serie": "TEXTO", "numero": "TEXTO", "total": 0.00, "categoria_gasto": "TEXTO"}
        """
        
        if ext in ["jpg", "jpeg", "png"]:
            img = Image.open(io.BytesIO(bytes_archivo))
            img = img.convert("RGB")
            out_img = io.BytesIO()
            img.save(out_img, format="JPEG", quality=50) # Subimos a 50 la calidad para asegurar lectura del texto del RUC
            documento_data = {'mime_type': 'image/jpeg', 'data': out_img.getvalue()}
        else:
            documento_data = {'mime_type': 'application/pdf', 'data': bytes_archivo}
            
        response = model.generate_content([prompt, documento_data])
        
        # Limpieza de cualquier bloque de código devuelto por error
        texto_respuesta = response.text.strip()
        texto_respuesta = re.sub(r'```json\s*|\s*```', '', texto_respuesta)
        
        data_ia = json.loads(texto_respuesta)
        
        fecha_normalizada = normalizar_fecha(data_ia.get("fecha_emision"))
        
        return construir_diccionario_factura(
            fecha_normalizada, data_ia.get("serie"), data_ia.get("numero"),
            data_ia.get("ruc_emisor"), data_ia.get("razon_social"), float(data_ia.get("total", 0.0)),
            data_ia.get("categoria_gasto"), archivo.name
        )
    except Exception as e:
        # Devolver una fila indicando el error de lectura sin romper el flujo paralelo
        return construir_diccionario_factura("No encontrado", "Error", "Error", "No encontrado", f"Error parseo archivo ({archivo.name})", 0.0, "Por clasificar", archivo.name)

def construir_diccionario_factura(fecha, serie, numero, ruc, proveedor, total, categoria_gasto, nombre_archivo):
    base_imponible = round(total / 1.18, 2)
    igv = round(total - base_imponible, 2)
    
    periodo_ejemplo = "202608"
    if fecha and fecha != "No encontrado" and "-" in fecha:
        try:
            partes = fecha.split("-")
            if len(partes) == 3:
                anio_f, mes_f, dia_f = partes
                fecha_sire = f"{dia_f}/{mes_f}/{anio_f}"
                periodo_ejemplo = f"{anio_f}{mes_f}"
            else:
                fecha_sire = fecha
        except Exception:
            fecha_sire = fecha
    else:
        fecha_sire = fecha if fecha else "No encontrado"
        
    return {
        "Periodo": periodo_ejemplo, "Fecha Emisión": fecha_sire, "Tipo Comp.": "01",
        "Serie": str(serie) if serie else "F001", "Número": str(numero) if numero else "00000001",
        "Tipo Doc Identidad": "6", "RUC Emisor": str(ruc) if ruc else "No encontrado",
        "Razón Social": proveedor if proveedor else "No encontrado",
        "Base Imponible S/": base_imponible, "IGV S/": igv, "Total S/": total,
        "Categoría IA (Gasto)": categoria_gasto if categoria_gasto else "Por clasificar",
        "Archivo Original": nombre_archivo
    }

archivos_subidos = st.file_uploader("Sube tus comprobantes masivos (XML, PDF, JPG, PNG)", type=["xml", "pdf", "jpg", "png"], accept_multiple_files=True)

if archivos_subidos:
    datos_facturas = []
    st.info("🚀 **Motor de procesamiento asíncrono activado:** Consultando múltiples archivos en paralelo con los servidores de Google...")
    
    with ThreadPoolExecutor() as executor:
        resultados = executor.map(analizar_un_archivo_con_ia, archivos_subidos)
        datos_facturas = list(resultados)

    if datos_facturas:
        df = pd.DataFrame(datos_facturas)
        st.success(f"¡Se consolidaron con éxito {len(datos_facturas)} documentos!")
        st.dataframe(df.drop(columns=["Archivo Original"]), use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Base Imponible", f"S/ {df['Base Imponible S/'].sum():,.2f}")
        col2.metric("Total Crédito Fiscal (IGV)", f"S/ {df['IGV S/'].sum():,.2f}")
        col3.metric("Total Facturado", f"S/ {df['Total S/'].sum():,.2f}")
        
        st.subheader("💾 Descarga de Documentos Consolidados")
        
        # Corrección de formato para evitar fallas de conversión a cadenas de texto
        lineas_txt = [f"{r['Periodo']}|{r['RUC Emisor']}-{r['Serie']}-{r['Número']}|{r['Fecha Emisión']}||01|{r['Serie']}|{r['Número']}||6|{r['RUC Emisor']}|{r['Razón Social']}|{r['Base Imponible S/']:.2f}|{r['IGV S/']:.2f}||||||{r['Total S/']:.2f}|||1|||" for i, r in df.iterrows()]
        contenido_txt = "\r\n".join(lineas_txt) + "\r\n"
        
        # Dinamizamos el nombre oficial del archivo TXT usando el primer periodo detectado
        periodo_detectado = df.iloc[0]["Periodo"] if not df.empty else "202608"
        ruc_cliente_ejemplo = "20123456789"


