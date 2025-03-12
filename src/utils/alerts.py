# alerts.py
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import telegram
from discord_webhook import DiscordWebhook
from datetime import datetime
from src.config.config import (
    ALERTA_ACTIVADA,
    EMAIL_ALERTAS,
    TELEGRAM_ACTIVADO,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    DISCORD_ACTIVADO,
    DISCORD_WEBHOOK_URL,
    UMBRAL_PRECIO_PORCENTAJE
)
from src.database.database import obtener_historial_precios

def calcular_porcentaje_cambio(precio_actual, precio_anterior):
    """
    Calcula el porcentaje de cambio entre dos precios.
    
    Args:
        precio_actual (float): Precio actual del producto
        precio_anterior (float): Precio anterior del producto
        
    Returns:
        float: Porcentaje de cambio (negativo si el precio bajó)
    """
    if precio_anterior == 0:
        return 0
    
    return ((precio_actual - precio_anterior) / precio_anterior) * 100

def verificar_alerta(producto, precio_anterior=None):
    """
    Verifica si un producto debe generar una alerta de precio.
    
    Args:
        producto (dict): Información del producto
        precio_anterior (float, opcional): Precio anterior conocido
        
    Returns:
        bool: True si se debe enviar una alerta, False en caso contrario
    """
    if not ALERTA_ACTIVADA:
        return False
    
    # Si no se proporciona un precio anterior, obtenerlo del historial
    if precio_anterior is None:
        historial = obtener_historial_precios(producto['id_producto'], limite=2)
        
        # Si no hay suficiente historial, no hay alerta
        if len(historial) < 2:
            return False
        
        precio_anterior = historial[1]['precio']
    
    # Calcular el porcentaje de cambio
    porcentaje_cambio = calcular_porcentaje_cambio(producto['precio'], precio_anterior)
    
    # Generar alerta si el precio bajó más del umbral configurado
    return porcentaje_cambio <= -UMBRAL_PRECIO_PORCENTAJE

def enviar_alerta_email(producto, precio_anterior):
    """
    Envía una alerta por correo electrónico.
    
    Args:
        producto (dict): Información del producto
        precio_anterior (float): Precio anterior del producto
        
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    try:
        # Configuración del servidor SMTP (esto debería estar en un archivo de configuración)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_user = "tu_correo@gmail.com"  # Reemplazar con credenciales reales
        smtp_password = "tu_contraseña"    # Reemplazar con credenciales reales
        
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = EMAIL_ALERTAS
        msg['Subject'] = f"¡Alerta de precio! {producto['nombre']} ha bajado de precio"
        
        # Calcular porcentaje de cambio
        porcentaje_cambio = calcular_porcentaje_cambio(producto['precio'], precio_anterior)
        
        # Cuerpo del mensaje
        body = f"""
        <html>
        <body>
            <h2>¡Alerta de precio!</h2>
            <p>El producto <strong>{producto['nombre']}</strong> ha bajado de precio.</p>
            <p>Modelo: {producto['modelo']}</p>
            <p>Tienda: {producto['tienda']}</p>
            <p>Precio anterior: ${precio_anterior:.2f}</p>
            <p>Precio actual: ${producto['precio']:.2f}</p>
            <p>Cambio: {porcentaje_cambio:.2f}%</p>
            <p>Vendedor: {producto['vendedor']}</p>
            <p><a href="{producto['link']}">Ver producto</a></p>
            <img src="{producto['imagen']}" alt="Imagen del producto" style="max-width: 300px;">
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Conectar y enviar
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Alerta enviada por correo a {EMAIL_ALERTAS}")
        return True
    except Exception as e:
        print(f"❌ Error al enviar alerta por correo: {e}")
        return False

def enviar_alerta_telegram(producto, precio_anterior):
    """
    Envía una alerta a través de Telegram.
    
    Args:
        producto (dict): Información del producto
        precio_anterior (float): Precio anterior del producto
        
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    if not TELEGRAM_ACTIVADO:
        return False
    
    try:
        # Calcular porcentaje de cambio
        porcentaje_cambio = calcular_porcentaje_cambio(producto['precio'], precio_anterior)
        
        # Crear mensaje
        mensaje = f"""
🔔 *¡Alerta de precio!*
*{producto['nombre']}* ha bajado de precio.

*Modelo:* {producto['modelo']}
*Tienda:* {producto['tienda']}
*Precio anterior:* ${precio_anterior:.2f}
*Precio actual:* ${producto['precio']:.2f}
*Cambio:* {porcentaje_cambio:.2f}%
*Vendedor:* {producto['vendedor']}

[Ver producto]({producto['link']})
        """
        
        # Enviar mensaje
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensaje,
            "parse_mode": "Markdown"
        }
        
        response = requests.post(url, data=data)
        
        if response.status_code == 200:
            print("✅ Alerta enviada por Telegram")
            return True
        else:
            print(f"❌ Error al enviar alerta por Telegram: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error al enviar alerta por Telegram: {e}")
        return False

def enviar_alerta_discord(producto, precio_anterior):
    """
    Envía una alerta a través de Discord usando webhooks.
    
    Args:
        producto (dict): Información del producto
        precio_anterior (float): Precio anterior del producto
        
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    if not DISCORD_ACTIVADO:
        return False
    
    try:
        # Calcular porcentaje de cambio
        porcentaje_cambio = calcular_porcentaje_cambio(producto['precio'], precio_anterior)
        
        # Crear mensaje para Discord (usando embeds)
        data = {
            "username": "GPU Price Alert",
            "avatar_url": "https://i.imgur.com/4M34hi2.png",
            "embeds": [{
                "title": "¡Alerta de precio!",
                "description": f"**{producto['nombre']}** ha bajado de precio.",
                "color": 3066993,  # Color verde
                "fields": [
                    {"name": "Modelo", "value": producto['modelo'], "inline": True},
                    {"name": "Tienda", "value": producto['tienda'], "inline": True},
                    {"name": "Precio anterior", "value": f"${precio_anterior:.2f}", "inline": True},
                    {"name": "Precio actual", "value": f"${producto['precio']:.2f}", "inline": True},
                    {"name": "Cambio", "value": f"{porcentaje_cambio:.2f}%", "inline": True},
                    {"name": "Vendedor", "value": producto['vendedor'] or "No disponible", "inline": True},
                ],
                "image": {"url": producto['imagen']},
                "url": producto['link'],
                "timestamp": datetime.now().isoformat()
            }]
        }
        
        # Enviar mensaje
        response = requests.post(DISCORD_WEBHOOK_URL, json=data)
        
        if response.status_code == 204:
            print("✅ Alerta enviada por Discord")
            return True
        else:
            print(f"❌ Error al enviar alerta por Discord: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error al enviar alerta por Discord: {e}")
        return False

def enviar_alertas(producto, precio_anterior):
    """
    Envía alertas por todos los canales configurados.
    
    Args:
        producto (dict): Información del producto
        precio_anterior (float): Precio anterior del producto
        
    Returns:
        bool: True si al menos una alerta se envió correctamente
    """
    # Verificar si se debe enviar una alerta
    if not verificar_alerta(producto, precio_anterior):
        return False
    
    # Intentar enviar por todos los canales configurados
    email_ok = enviar_alerta_email(producto, precio_anterior)
    telegram_ok = enviar_alerta_telegram(producto, precio_anterior)
    discord_ok = enviar_alerta_discord(producto, precio_anterior)
    
    # Devolver True si al menos una alerta se envió correctamente
    return email_ok or telegram_ok or discord_ok 