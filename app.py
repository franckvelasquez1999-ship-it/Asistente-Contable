import streamlit as st
import random

# 1. Configuración de la página del juego
st.set_page_config(page_title="Yape Ninja!", layout="centered")

# 2. Estilos CSS para ambientar la aplicación con la marca
st.markdown("""
    <style>
    .stApp { background-color: #51135d !important; font-family: 'Inter', sans-serif; }
    h1, p { text-align: center; color: #ffffff !important; }
    .instrucciones {
        background-color: #742284;
        padding: 15px;
        border-radius: 12px;
        border: 2px solid #00e6b3;
        margin-bottom: 20px;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🥷 ¡YAPE NINJA!")
st.write("¡Protege tu cuenta de los ciberdelincuentes en tiempo real!")

# Caja de instrucciones para el jugador
st.markdown("""
<div class="instrucciones">
    <strong>¿Cómo jugar?</strong><br>
    🟢 Haz clic/toque en los <strong>Globos de Yape (S/)</strong> para sumar 10 puntos.<br>
    ❌ Evita hacer clic en los <strong>Mensajes de Estafa (SMS ⚠️)</strong> o perderás una vida.<br>
    🏆 ¡Consigue la mayor puntuación antes de perder tus 3 vidas!
</div>
""", unsafe_allow_html=True)

# 3. EL MOTOR DE JUEGO (HTML5 CANVAS + JAVASCRIPT) INYECTADO DIRECTAMENTE
html_juego = """
<div style="text-align: center;">
    <canvas id="gameCanvas" width="500" height="500" style="border: 4px solid #00e6b3; border-radius: 16px; background-color: #1e1b29; cursor: crosshair; max-width: 100%;"></canvas>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// Variables globales del estado del juego
let score = 0;
let lives = 3;
let gameOver = false;
let gameObjects = [];
let spawnTimer = 0;
let spawnInterval = 50; // Velocidad de aparición inicial

// Clase constructora para los objetos que caen (Globos y Estafas)
class FallingObject {
    constructor() {
        this.x = Math.random() * (canvas.width - 60) + 30;
        this.y = -40;
        this.radius = 24;
        this.speed = Math.random() * 2 + 2 + (score / 100); // Sube la velocidad conforme sumas puntos
        this.type = Math.random() > 0.4 ? 'yape' : 'estafa'; // 60% Globos, 40% Estafas
        this.sliced = false;
    }

    update() {
        this.y += this.speed;
    }

    draw() {
        ctx.save();
        if (this.type === 'yape') {
            // Dibujar Globo Yape (Verde Menta brillante)
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = "#00e6b3";
            ctx.fill();
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // Texto dentro del globo
            ctx.fillStyle = "#742284";
            ctx.font = "bold 16px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("S/", this.x, this.y + 6);
        } else {
            // Dibujar Mensaje de Estafa (Rectángulo Rojo de SMS)
            ctx.fillStyle = "#ff4a4a";
            ctx.fillRect(this.x - 25, this.y - 18, 50, 36);
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.strokeRect(this.x - 25, this.y - 18, 50, 36);
            
            // Icono de alerta
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 14px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("SMS ⚠️", this.x, this.y + 5);
        }
        ctx.restore();
    }
}

# Capturar los clics del mouse sobre el área del lienzo
canvas.addEventListener("mousedown", function(e) {
    if (gameOver) {
        // Reiniciar el juego si haces clic en la pantalla de Game Over
        score = 0;
        lives = 3;
        gameOver = false;
        gameObjects = [];
        spawnInterval = 50;
        return;
    }

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    // Detectar si el clic impactó algún objeto en movimiento
    for (let i = gameObjects.length - 1; i >= 0; i--) {
        let obj = gameObjects[i];
        let dist = Math.sqrt((mouseX - obj.x)**2 + (mouseY - obj.y)**2);
        
        if (dist < obj.radius + 10) {
            if (obj.type === 'yape') {
                score += 10; // Sumar puntos por recolectar el dinero
            } else {
                lives -= 1; // Restar vida por caer en la estafa
                if (lives <= 0) gameOver = true;
            }
            gameObjects.splice(i, 1);
            break;
        }
    }
});

// Bucle principal del juego (Game Loop a 60 FPS)
function gameLoop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!gameOver) {
        // Generar nuevos objetos periódicamente
        spawnTimer++;
        if (spawnTimer > spawnInterval) {
            gameObjects.push(new FallingObject());
            spawnTimer = 0;
            // Aumentar la dificultad gradualmente
            if (spawnInterval > 20) spawnInterval -= 0.5;
        }

        // Actualizar y pintar cada objeto en pantalla
        for (let i = gameObjects.length - 1; i >= 0; i--) {
            let obj = gameObjects[i];
            obj.update();
            obj.draw();

            // Si el objeto cae fuera de la pantalla sin ser tocado
            if (obj.y > canvas.height + 40) {
                if (obj.type === 'yape') {
                    lives -= 1; // Dejar ir dinero real te quita una vida
                    if (lives <= 0) gameOver = true;
                }
                gameObjects.splice(i, 1);
            }
        }

        // Dibujar el Marcador de Puntuación (Estilo Interfaz Yape)
        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 20px sans-serif";
        ctx.textAlign = "left";
        ctx.fillText("💰 Saldo Puntos: " + score, 20, 40);

        // Dibujar Corazones de Vidas restantes
        ctx.textAlign = "right";
        ctx.fillStyle = "#ff4a4a";
        ctx.fillText("❤️ Vidas: " + "⭐".repeat(lives), canvas.width - 20, 40);

    } else {
        // Pantalla de Fin de Juego (Game Over)
        ctx.fillStyle = "rgba(116, 34, 132, 0.85)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = "#00e6b3";
        ctx.font = "bold 40px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("¡CUENTA HACKEADA!", canvas.width / 2, canvas.height / 2 - 40);

        ctx.fillStyle = "#ffffff";
        ctx.font = "24px sans-serif";
        ctx.fillText("Puntuación Final: " + score + " pts", canvas.width / 2, canvas.height / 2 + 10);
        
        ctx.font = "bold 16px sans-serif";
        ctx.fillStyle = "#00e6b3";
        ctx.fillText("Haz clic en cualquier parte para REINICIAR", canvas.width / 2, canvas.height / 2 + 60);
    }

    requestAnimationFrame(gameLoop);
}

// Iniciar el juego
gameLoop();
</script>
"""

# Renderizar el juego completo de forma segura en Streamlit
st.components.v1.html(html_juego, height=530, scrolling=False)
