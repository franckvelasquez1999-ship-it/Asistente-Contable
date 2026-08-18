import streamlit as st
import random
from datetime import datetime

# 1. Configuración de la página del simulador
st.set_page_config(page_title="Simulador de Constancias Yape", layout="centered")

# Inicializar la memoria de sesión para el comprobante si no existe
if "html_actual" not in st.session_state:
    st.session_state.html_actual = None

# 2. INYECCIÓN DE DISEÑO INTERFAZ DE YAPE PREMIUM CLONADA AL 100%
st.markdown("""
    <style>
    @import url('https://googleapis.com');

    .stApp { 
        background-color: #69167c !important; 
        font-family: 'Inter', sans-serif; 
    }
    h1, h2, h3, p, span, label { 
        color: #ffffff !important; 
    }
    .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #7b258e !important;
        color: #ffffff !important;
        border: 1px solid #00e6b3 !important;
        border-radius: 10px !important;
    }
    
    /* VOUCHER COMPLETO CLONADO */
    .yape-voucher-real {
        max-width: 440px;
        background-color: #69167c;
        margin: 20px auto;
        padding-bottom: 20px;
        box-sizing: border-box;
    }

    /* CABECERA CON EL FORMATO EXACTO DE ARRIBA */
    .yape-cabecera-art {
        width: 100%;
        height: 200px;
        background-color: #69167c;
        background-image: 
            radial-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 0),
            radial-gradient(rgba(255, 255, 255, 0.08) 2px, transparent 0);
        background-size: 10px 10px, 20px 20px;
        background-position: 0 0, 5px 5px;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .yape-brand-group {
        position: absolute;
        left: 24px;
        top: 65px;
        text-align: left;
    }
    .yape-logo-bubble {
        width: 24px;
        height: 24px;
        background-color: #00e6b3;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        font-size: 0.65rem;
        color: #69167c;
        font-weight: 800;
        margin-bottom: 2px;
    }
    .yape-logo-txt-style {
        font-size: 1.7rem;
        color: #ffffff;
        font-weight: 800;
        font-style: italic;
        line-height: 1;
        letter-spacing: -1px;
    }
    .yape-avatar-circle {
        width: 125px;
        height: 125px;
        border-radius: 50%;
        border: 1px solid rgba(255,255,255,0.2);
        background: radial-gradient(circle, rgba(138,43,226,0.2) 0%, rgba(74,18,84,0.7) 100%);
    }
    .yape-txt-valdelomar {
        position: absolute;
        right: 24px;
        color: rgba(255,255,255,0.35) !important;
        font-family: 'Times New Roman', serif;
        font-size: 0.85rem;
        text-align: left;
        line-height: 1.1;
        letter-spacing: 0.5px;
    }

    /* CONTENEDOR TARJETA BLANCA */
    .yape-cuerpo-blanco {
        background-color: #ffffff !important;
        border-radius: 28px;
        padding: 35px 28px;
        margin: 0 16px;
        text-align: left;
    }
    .y_titulo {
        color: #69167c !important;
        font-size: 1.55rem !important;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .y_monto {
        color: #2c2536 !important;
        font-size: 3.6rem !important;
        font-weight: 700;
        margin-bottom: 10px;
        display: flex;
        align-items: baseline;
        line-height: 1;
    }
    .y_monto span {
        font-size: 2.1rem !important;
        font-weight: 600;
        margin-right: 6px;
        color: #2c2536 !important;
    }
    .y_usuario {
        color: #2c2536 !important;
        font-size: 1.55rem !important;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .y_fecha {
        color: #827e8c !important;
        font-size: 0.95rem !important;
        margin-bottom: 22px;
        padding-bottom: 18px;
        border-bottom: 1.5px solid #f0edf5;
    }

    /* CÓDIGO DE SEGURIDAD */
    .y_token_row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 22px;
        padding-bottom: 18px;
        border-bottom: 1.5px solid #f0edf5;
    }
    .y_token_label {
        color: #827e8c !important;
        font-size: 0.8rem !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .y_token_blocks {
        display: flex;
        gap: 4px;
    }
    .y_token_digit {
        background-color: #f4f1f7;
        color: #2c2536 !important;
        font-weight: 700;
        font-size: 1.15rem;
        width: 28px;
        height: 32px;
        display: flex;
        justify-content: center;
        align-items: center;
        border-radius: 6px;
        border: 1px solid #e1dae8;
    }

    /* FILAS METADATOS DE TRANSACCIÓN */
    .y_meta_title {
        color: #827e8c !important;
        font-size: 0.8rem !important;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 16px;
        letter-spacing: 0.5px;
    }
    .y_meta_line {
        display: flex;
        justify-content: space-between;
        margin-bottom: 14px;
        font-size: 1rem;
    }
    .y_meta_lbl {
        color: #827e8c !important;
        font-weight: 500;
    }
    .y_meta_val {
        color: #2c2536 !important;
        font-weight: 600;
        text-align: right;
    }

    /* BOTONES INTERFAZ STREAMLIT */
    .stButton>button {
        background-color: #00e6b3 !important;
        color: #69167c !important;
        font-weight: 700 !important;
        border-radius: 25px !important;
        border: none !important;
        padding: 12px 25px !important;
        width: 100%;
        font-size: 1.1rem !important;
    }
    .stButton>button:hover {
        background-color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔮 Simulador de Comprobantes Yape")
st.write("Genera constancias digitales exactas con códigos y tokens dinámicos en tiempo real.")

# 3. FORMULARIO DE ENTRADA DE DATOS
st.markdown("### 📝 Datos del Comprobante")
col1, col2 = st.columns(2)

with col1:
    nombre_destinatario = st.text_input("Nombre del Contacto", "Erick Vel*")
    monto_envio = st.number_input("Monto Enviado (S/)", min_value=0.10, value=50.00, step=5.00)

with col2:
    numero_celular = st.text_input("Número de Celular", "*** *** 614")
    banco_destino = st.selectbox("Banco Destino", ["Yape", "BCP", "Interbank", "BBVA", "Scotiabank"])

# 4. BOTONES DE CONTROL DE INTERFAZ
btn_col1, btn_col2 = st.columns(2)

with btn_col1:
    if st.button("🚀 Generar Nuevo Comprobante Único"):
        # Cálculo seguro de valores dinámicos
        t1, t2, t3 = str(random.randint(0, 9)), str(random.randint(0, 9)), str(random.randint(0, 9))
        nro_op = str(random.randint(10000000, 99999999))
        
        meses_es = {"Jan":"jul.", "Feb":"feb.", "Mar":"mar.", "Apr":"abr.", "May":"may.", "Jun":"jun.", "Jul":"jul.", "Aug":"ago.", "Sep":"set.", "Oct":"oct.", "Nov":"nov.", "Dec":"dic."}
        fecha_hoy = datetime.now()
        mes_corregido = meses_es.get(fecha_hoy.strftime("%b"), "jul.")
        fecha_actual_str = f"{fecha_hoy.strftime('%d')} {mes_corregido} {fecha_hoy.strftime('%Y')} | {fecha_hoy.strftime('%I:%M %p.').lower()}"
        monto_formateado = f"{monto_envio:,.2f}".replace(".00", "")

        # CONSTRUCCIÓN HTML PURO USANDO FORMATEO INDEXADO (EVITA CUALQUER ERROR SINTÁCTICO DE TRIPLES COMILLAS)
        st.session_state.html_actual = """
        <div class="yape-voucher-real">
            <div class="yape-cabecera-art">
                <div class="yape-brand-group">
                    <div class="yape-logo-bubble">S/</div>
                    <div class="yape-logo-text-style">yape</div>
                </div>
                <div class="yape-avatar-circle"></div>
                <div class="yape-txt-valdelomar">ABRAHAM<br>VALDELOMAR</div>
            </div>
            
            <div class="yape-cuerpo-blanco">
                <div class="y_titulo">¡Yapeaste!</div>
                <div class="y_monto"><span>S/</span>{monto}</div>
                <div class="y_usuario">{nombre}</div>
                <div class="y_fecha">📅 {fecha}</div>
                
                <div class="y_token_row">
                    <div class="y_token_label">Código de seguridad</div>
                    <div class="y_token_blocks">
                        <div class="y_token_digit">{tok1}</div>
                        <div class="y_token_digit">{tok2}</div>
                        <div class="y_token_digit">{tok3}</div>
                    </div>
                </div>
                
                <div class="y_meta_title">Datos de la transacción</div>
                <div class="y_meta_line">
                    <span class="y_meta_lbl">Nro. de celular</span>
                    <span class="y_meta_val">{celular}</span>
                </div>
                <div class="y_meta_line">
                    <span class="y_meta_lbl">Destino</span>
                    <span class="y_meta_val">{banco}</span>
                </div>
                <div class="y_meta_line">
                    <span class="y_meta_lbl">Nro. de operación</span>
                    <span class="y_meta_val">{operacion}</span>
                </div>
            </div>
        </div>
        """.format(
            monto=monto_formateado,
            nombre=nombre_destinatario,
            fecha=fecha_actual_str,
            tok1=t1, tok2=t2, tok3=t3,
            celular=numero_celular,
            banco=banco_destino,
            operacion=nro_op
        )
        st.rerun()

with btn_col2:
    if st.button("🗑️ Limpiar Pantalla"):
        st.session_state.html_actual = None
        st.rerun()

# 5. RENDERIZADO DEL COMPROBANTE BLOQUEADO EN SESIÓN
if st.session_state.html_actual:
