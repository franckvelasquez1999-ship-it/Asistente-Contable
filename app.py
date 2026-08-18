import streamlit as st
import random

# 1. Configuración de la página del juego
st.set_page_config(page_title="Yape Ninja!", layout="centered")

# 2. Estilos CSS para ambientar la aplicación con la marca (Letras blancas y legibles)
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
        color: #ffffff !important;
    }
    .instrucciones strong, .instrucciones span {
        color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🥷 ¡YAPE NINJA!")
st.write("¡Protege tu cuenta de los ciberdelincuentes en tiempo real!")

# Caja de instrucciones corregida para máxima lectura
st.markdown("""
<div class="instrucciones">
    <strong style="color: #ffffff;">¿Cómo jugar?</strong><br>
    <span style="color: #ffffff;">🟢 Haz clic/toque en los <strong>Globos de Yape (S/)</strong> para sumar 10 puntos.</span><br>
    <span style="color: #ffffff;">❌ Evita hacer clic en los <strong>Mensajes de Estafa (SMS ⚠️)</strong> o perderás una vida.</span><br>
    <span style="color: #ffffff;">🏆 ¡Consigue la mayor puntuación antes de perder tus 3 vidas!</span>
</div>
""", unsafe_allow_html=True)

# 3. EL MOTOR DE JUEGO CORREGIDO (SIN COMENTARIOS INTERNOS QUE ROMPAN EL CANVAS)
html_juego = """
<div style="text-align: center;">
    <canvas id="gameCanvas" width="500" height="500" style="border: 4px solid #00e6b3; border-radius: 16px; background-color: #1e1b29; cursor: crosshair; max-width: 100%;"></canvas>
</div>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

let score = 0;
let lives = 3;
let gameOver = false;
let gameObjects = [];
let spawnTimer = 0;
let spawnInterval = 40; 

class FallingObject {
    constructor() {
        this.x = Math.random() * (canvas.width - 60) + 30;
        this.y = -40;
        this.radius = 24;
        this.speed = Math.random() * 2 + 2 + (score / 120); 
        this.type = Math.random() > 0.4 ? 'yape' : 'estafa'; 
        this.sliced = false;
    }

    update() {
        this.y += this.speed;
    }

    draw() {
        ctx.save();
        if (this.type === 'yape') {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = "#00e6b3";
            ctx.fill();
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.stroke();
            
            ctx.fillStyle = "#742284";
            ctx.font = "bold 16px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("S/", this.x, this.y + 6);
        } else {
            ctx.fillStyle = "#ff4a4a";
            ctx.fillRect(this.x - 28, this.y - 18, 56, 36);
            ctx.strokeStyle = "#ffffff";
            ctx.lineWidth = 2;
            ctx.strokeRect(this.x - 28, this.y - 18, 56, 36);
            
            ctx.fillStyle = "#ffffff";
            ctx.font = "bold 13px sans-serif";
            ctx.textAlign = "center";
            ctx.fillText("SMS ⚠️", this.x, this.y + 5);
        }
        ctx.restore();
    }
}

canvas.addEventListener("mousedown", function(e) {
    if (gameOver) {
        score = 0;
        lives = 3;
        gameOver = false;
        gameObjects = [];
        spawnInterval = 40;
        return;
    }

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    for (let i = gameObjects.length - 1; i >= 0; i--) {
        let obj = gameObjects[i];
        let dist = Math.sqrt((mouseX - obj.x)**2 + (mouseY - obj.y)**2);
        
        if (dist < obj.radius + 15) {
            if (obj.type === 'yape') {
                score += 10; 
            } else {
                lives -= 1; 
                if (lives <= 0) gameOver = true;
            }
            gameObjects.splice(i, 1);
            break;
        }
    }
});

function gameLoop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!gameOver) {
        spawnTimer++;
        if (spawnTimer > spawnInterval) {
            gameObjects.push(new FallingObject());
            spawnTimer = 0;
            if (spawnInterval > 15) spawnInterval -= 0.3;
        }

        for (let i = gameObjects.length - 1; i >= 0; i--) {
            let obj = gameObjects[i];
            obj.update();
            obj.draw();

            if (obj.y > canvas.height + 40) {
                if (obj.type === 'yape') {
                    lives -= 1; 
                    if (lives <= 0) gameOver = true;
                }
                gameObjects.splice(i, 1);
            }
        }

        ctx.fillStyle = "#ffffff";
        ctx.font = "bold 20px sans-serif";
        ctx.textAlign = "left";
        ctx.fillText("💰 Puntos: " + score, 20, 40);

        ctx.textAlign = "right";
        ctx.fillStyle = "#ff4a4a";
        let corazones = "";
        for(let c=0; c<lives; c++) { corazones += "❤️"; }
        ctx.fillText("Vidas: " + corazones, canvas.width - 20, 40);

    } else {
        ctx.fillStyle = "rgba(81, 19, 93, 0.95)";
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        ctx.fillStyle = "#00e6b3";
        ctx.font = "bold 36px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("¡CUENTA HACKEADA!", canvas.width / 2, canvas.height / 2 - 30);

        ctx.fillStyle = "#ffffff";
        ctx.font = "22px sans-serif";
        ctx.fillText("Puntuación Final: " + score + " pts", canvas.width / 2, canvas.height / 2 + 15);
        
        ctx.font = "bold 15px sans-serif";
        ctx.fillStyle = "#00e6b3";
        ctx.fillText("Haz clic aquí para REINICIAR", canvas.width / 2, canvas.height / 2 + 65);
    }

    requestAnimationFrame(gameLoop);
}

gameLoop();
</script>
"""

# Renderizar el canvas interactivo
st.components.v1.html(html_juego, height=530, scrolling=False)
