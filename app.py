import streamlit as st
import random
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import io

# FUNCIÓN INFALIBLE PARA DIBUJAR LOS TEXTOS DINÁMICOS SOBRE LA IMAGEN BASE
def generar_comprobante_imagen(nombre, monto, celular, banco, operacion):
    # 1. Carga la imagen de fondo que clonaste (debes subirla a tu GitHub como 'fondo_yape.png')
    try:
        imagen = Image.open("fondo_yape.png").convert("RGB")
    except FileNotFoundError:
        # Si no encuentra el fondo, crea un lienzo morado temporal de respaldo para evitar caídas
        imagen = Image.new("RGB", (440, 880), color="#69167c")
    
    draw = ImageDraw.Draw(imagen)
    
    # 2. Cargar fuentes tipográficas (asegúrate de que estén en tu repositorio)
    try:
        font_monto = ImageFont.truetype("Inter-Bold.ttf", 48)
        font_textos = ImageFont.truetype("Inter-Regular.ttf", 16)
        font_bold = ImageFont.truetype("Inter-SemiBold.ttf", 18)
    except IOError:
        font_monto = font_textos = font_bold = ImageFont.load_default()

    # 3. Coordenadas matemáticas exactas para pintar encima (Ajustable según tu fondo)
    draw.text((60, 260), f"S/ {monto}", fill="#2c2536", font=font_monto)
    draw.text((60, 330), nombre, fill="#2c2536", font=font_bold)
    
    # Código de seguridad dinámico (Pintado celda por celda)
    t1, t2, t3 = str(random.randint(0,9)), str(random.randint(0,9)), str(random.randint(0,9))
    draw.text((320, 422), t1, fill="#2c2536", font=font_bold)
    draw.text((350, 422), t2, fill="#2c2536", font=font_bold)
    draw.text((380, 422), t3, fill="#2c2536", font=font_bold)
    
    # Metadatos del bloque inferior
    draw.text((280, 560), celular, fill="#2c2536", font=font_textos)
    draw.text((280, 600), banco, fill="#2c2536", font=font_textos)
    draw.text((280, 640), operacion, fill="#2c2536", font=font_bold)
    
    # Convertir a bytes para que Streamlit lo procese
    byte_io = io.BytesIO()
    imagen.save(byte_io, format="PNG")
    return byte_io.getvalue()

# BLOQUE DE EJECUCIÓN EN TU INTERFAZ DE STREAMLIT
if st.button("🚀 Generar Comprobante Fotográfico"):
    nro_op = str(random.randint(10000000, 99999999))
    
    # Generar el binario de la imagen procesada
    imagen_final_bytes = generar_comprobante_imagen(
        nombre="Erick Vel*",
        monto="495",
        celular="*** *** 614",
        banco="Interbank",
        operacion=nro_op
    )
    
    # Desplegar la imagen renderizada directamente en la pantalla de la nube sin HTML roto
    st.image(imagen_final_bytes, caption="Constancia oficial generada en tiempo real", use_container_width=True)
