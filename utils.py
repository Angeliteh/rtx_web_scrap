# utils.py
import random
import requests
from config import USER_AGENTS

def get_random_user_agent():
    """Devuelve un User-Agent aleatorio."""
    return random.choice(USER_AGENTS)

def get_headers():
    """Genera los headers necesarios para la solicitud HTTP."""
    return {
        "User-Agent": get_random_user_agent(),
        "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.amazon.com.mx/",
        "Connection": "keep-alive",
    }

def fetch_page(url):
    """
    Realiza la solicitud HTTP a la URL dada y retorna el contenido HTML
    si la respuesta es exitosa.
    """
    headers = get_headers()
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        if "CAPTCHA" in response.text:
            print("¡Bloqueado por CAPTCHA!")
            return None
        return response.content
    else:
        print(f"Error: No se pudo acceder a la página. Código de estado: {response.status_code}")
        return None
