import streamlit as st
import random
from datetime import datetime

# 1. Configuración de la página del simulador
st.set_page_config(page_title="Simulador de Constancias Yape", layout="centered")

# 2. INYECCIÓN DE DISEÑO INTERFAZ DE YAPE PREMIUM
st.markdown("""
    <style>
    /* Fondo morado Yape de la aplicación completa */
    .stApp { 
        background-color: #69167c !important; 
        font-family: 'Inter', -apple-system, sans-serif; 
    }
    
    h1, h2, h3, p, span, label { 
        color: #ffffff !important; 
    }
    
    /* Estilos para el formulario de entrada */
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #7b258e !important;
        color: #ffffff !important;
        border: 1px solid #00e6b3 !important;
        border-radius: 10px !important;
    }

    /* CONTENEDOR VOUCHER PRINCIPAL */
    .yape-voucher-completo {
        max-width: 440px;
        background-color: #69167c;
        margin: 20px auto;
        text-align: center;
        padding-bottom: 20px;
    }

    /* CABECERA: Fondo de líneas del billete y Abraham Valdelomar */
    .yape-banner-valdelomar {
        width: 100%;
        height: 220px;
        background-color: #69167c;
        background-image: 
            radial-gradient(rgba(255, 255, 255, 0.15) 1px, transparent 0),
            radial-gradient(rgba(255, 255, 255, 0.1) 2px, transparent 0);
        background-size: 8px 8px, 16px 16px;
        background-position: 0 0, 4px 4px;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Logo Redondo Yape Izquierda */
    .yape-logo-top {
        position: absolute;
        left: 25px;
        top: 60px;
        width: 65px;
        height: 65px;
    }
    .yape-logo-circle {
        width: 26px;
        height: 26px;
        background-color: #00e6b3;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 0.6rem;
        color: #69167c;
        font-weight: 800;
        margin-bottom: 4px;
    }
    .yape-logo-text {
        font-size: 1.6rem;
        color: #ffffff;
        font-weight: 800;
        font-style: italic;
        line-height: 1;
        letter-spacing: -1px;
    }

    /* Grabado del Rostro Central */
    .avatar-valdelomar {
        width: 130px;
        height: 130px;
        border-radius: 50%;
        border: 1px solid rgba(255,255,255,0.25);
        background: radial-gradient(circle, rgba(138,43,226,0.3) 0%, rgba(74,18,84,0.8) 100%);
        box-shadow: 0 0 30px rgba(0,0,0,0.4);
    }
    
    /* Texto Derecha Grabado */
    .txt-valdelomar {
        position: absolute;
        right: 25px;
        color: rgba(255,255,255,0.4) !important;
        font-family: 'Times New Roman', serif;
        font-size: 0.85rem;
        text-align: left;
        line-height: 1.1;
        letter-spacing: 1px;
        font-weight: 400;
    }

    /* VOUCHER TARJETA BLANCA */
    .yape-card-blanca {
        background-color: #ffffff !important;
        border-radius: 32px;
        padding: 35px 30px;
        margin: 0 15px;
        text-align: left;
        box-shadow: 0 15px 35px rgba(0,0,0,0.3);
    }

    .yape-header-title {
        color: #69167c !important;
        font-size: 1.6rem !important;
        font-weight: 700;
        margin-bottom: 12px;
    }

    .yape-monto-grande {
        color: #383344 !important;
        font-size: 3.8rem !important;
        font-weight: 700;
        margin-bottom: 15px;
        display: flex;
        align-items: baseline;
        line-height: 1;
    }
    .yape-monto-grande span {
        font-size: 2.2rem !important;
        font-weight: 600;
        margin-right: 6px;
        color: #383344 !important;
    }

    .yape-destinatario {
        color: #2c2536 !important;
        font-size: 1.55rem !important;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .yape-timestamp {
        color: #827e8c !important;
        font-size: 1rem !important;
        margin-bottom: 25px;
        padding-bottom: 20px;
        border-bottom: 1.5px solid #f0edf5;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* SECCIÓN TOKEN DE SEGURIDAD */
    .yape-token-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 25px;
        padding-bottom: 20px;
        border-bottom: 1.5px solid #f0edf5;
    }
    .yape-token-title {
        color: #827e8c !important;
        font-size: 0.85rem !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .yape-token-blocks {
        display: flex;
        gap: 4px;
    }
    .yape-block-num {
        background-color: #f4f1f7;
        color: #2c2536 !important;
        font-weight: 700;
        font-size: 1.15rem;
        width: 30px;
        height: 34px;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 6px;
        border: 1px solid #e1dae8;
    }

    /* SECCIÓN METADATOS */
    .yape-info-section-title {
        color: #827e8c !important;
        font-size: 0.85rem !important;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 18px;
        letter-spacing: 0.5px;
    }
    .yape-meta-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 16px;
        font-size: 1.05rem;
        line-height: 1.2;
    }
    .yape-meta-label {
        color: #827e8c !important;
        font-weight: 500;
    }
    .yape-meta-value {
        color: #2c2536 !important;
        font-weight: 600;
        text-align: right;
    }

    /* BOTÓN GENERAR */
    .stButton>button {
        background-color: #00e6b3 !important;
        color: #69167c !important;
        font-weight: 700 !important;
        border-radius: 25px !important;
        border: none !important;
        padding: 12px 25px !important;
        width: 100%;
        font-size: 1.1rem !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    .stButton>button:hover {
        background-color: #ffffff !important;
        color: #69167c !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔮 Simulador de Comprobantes Yape")
st.write("Genera constancias digitales con códigos y tokens dinámicos en tiempo real.")

# 3. FORMULARIO DE RECOPILACIÓN DE DATOS (Panel Superior)
st.markdown("### 📝 Datos del Comprobante")
col1, col2 = st.columns(2)

with col1:
    nombre_destinatario = st.text_input("Nombre del Contacto", "Erick Vel*")
    monto_envio = st.number_input("Monto Enviado (S/)", min_value=0.10, value=50.00, step=5.00)

with col2:
    numero_celular = st.text_input("Número de Celular", "*** *** 614")
    banco_destino = st.selectbox("Banco Destino", ["Yape", "BCP", "Interbank", "BBVA", "Scotiabank"])

# 4. PROCESAMIENTO LINEAL DE GENERACIÓN
if st.button("🚀 Generar Nuevo Comprobante Único"):
    
    # Generación matemática aleatoria de códigos independientes por clic
    cod_seguridad_1 = str(random.randint(0, 9))
    cod_seguridad_2 = str(random.randint(0, 9))
    cod_seguridad_3 = str(random.randint(0, 9))
    numero_operacion_dinamico = str(random.randint(10000000, 99999999))
    
    # Cálculo y traducción de la fecha en tiempo real estilo app móvil
    meses_es = {
        "Jan": "ene.", "Feb": "feb.", "Mar": "mar.", "Apr": "abr.", 
        "May": "may.", "Jun": "jun.", "Jul": "jul.", "Aug": "ago.", 
        "Sep": "set.", "Oct": "oct.", "Nov": "nov.", "Dec": "dic."
    }
    fecha_actual = datetime.now()
    mes_formateado = meses_es.get(fecha_actual.strftime("%b"), "ago.")
    timestamp_yape = f"{fecha_actual.strftime('%d')} {mes_formateado} {fecha_actual.strftime('%Y')} | {fecha_actual.strftime('%I:%M %p.').lower()}"

    # ESTRUCTURA HTML DE LA CONSTANCIA REQUERIDA
    html_constancia = f"""
    <div class="yape-voucher-completo">
        <!-- BANNER DE SEGURIDAD (BILLETE ABRAHAM VALDELOMAR) -->
        <div class="yape-banner-valdelomar">
            <div class="yape-logo-top">
                <div class="yape-logo-circle">S/</div>
                <div class="yape-logo-text">yape</div>
            </div>
            <div class="avatar-valdelomar"></div>
            <div class="txt-valdelomar">ABRAHAM<br>VALDELOMAR</div>
        </div>
        
        <!-- CUERPO DEL COMPROBANTE BLANCO -->
        <div class="yape-card-blanca">
            <div class="yape-header-title">¡Yapeaste!</div>
            <div class="yape-monto-grande"><span>S/</span>{monto_envio:,.2f}</div>
            <div class="yape-destinatario">{nombre_destinatario}</div>
            <div class="yape-timestamp">📅 {timestamp_yape}</div>
            
            <!-- BLOQUE DE CÓDIGO DE SEGURIDAD DINÁMICO -->
            <div class="yape-token-row">
                <div class="yape-token-title">Código de seguridad</div>
                <div class="yape-token-blocks">
                    <div class="yape-block-num">{cod_seguridad_1}</div>
                    <div class="yape-block-num">{cod_seguridad_2}</div>
                    <div class="yape-block-num">{cod_seguridad_3}</div>
                </div>
            </div>
            
            <!-- SECCIÓN METADATOS DE TRANSACCIÓN -->
            <div class="yape-info-section-title">Datos de la transacción</div>
            <div class="yape-meta-row">
                <span class="yape-meta-label">Nro. de celular</span>
                <span class="yape-meta-value">{numero_celular}</span>
            </div>
            <div class="yape-meta-row">
                <span class="yape-meta-label">Destino</span>
                <span class="yape-meta-value">{banco_destino}</span>
            </div>
            <div class="yape-meta-row">


# Renderizar el canvas interactivo
st.components.v1.html(html_juego, height=530, scrolling=False)
