# utils.py
"""
Utilidades para el scraping de datos, como funciones para realizar peticiones HTTP,
obtener User-Agents aleatorios, etc.
"""

import random
import requests
import time
from config import DELAY_ENTRE_PETICIONES, TIMEOUT_PETICIONES, REINTENTOS_PETICIONES

# Lista de User-Agents para simular diferentes navegadores
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36 OPR/78.0.4093.147'
]

def get_random_user_agent():
    """
    Retorna un User-Agent aleatorio de la lista.
    
    Returns:
        str: User-Agent aleatorio
    """
    return random.choice(USER_AGENTS)

def get_headers():
    """
    Genera headers para las peticiones HTTP con un User-Agent aleatorio.
    
    Returns:
        dict: Headers para la petición HTTP
    """
    return {
        'User-Agent': get_random_user_agent(),
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }

def fetch_page(url, use_selenium=False, use_playwright=False):
    """
    Realiza una petición HTTP a la URL especificada y devuelve el contenido HTML.
    
    Args:
        url (str): URL a la que se realizará la petición
        use_selenium (bool): Si es True, utiliza Selenium para cargar la página (útil para contenido dinámico)
        use_playwright (bool): Si es True, utiliza Playwright para cargar la página (alternativa a Selenium)
        
    Returns:
        str: Contenido HTML de la página
    """
    # Usar Selenium por defecto para MercadoLibre
    if 'mercadolibre' in url.lower() and not use_playwright:
        use_selenium = True
        
    try:
        if use_selenium:
            return fetch_with_selenium(url)
        elif use_playwright:
            return fetch_with_playwright(url)
        else:
            return fetch_with_requests(url)
    except Exception as e:
        print(f"⚠️ Error al obtener la página {url}: {e}")
        return ""

def fetch_with_requests(url):
    """
    Realiza una petición HTTP usando la biblioteca requests.
    
    Args:
        url (str): URL a la que realizar la petición
        
    Returns:
        str: Contenido HTML de la página, o None si hubo un error
    """
    headers = get_headers()
    
    for intento in range(REINTENTOS_PETICIONES):
        try:
            response = requests.get(url, headers=headers, timeout=TIMEOUT_PETICIONES)
            
            if response.status_code == 200:
                return response.text
            else:
                print(f"⚠️ Error al obtener la página {url}: Código {response.status_code}")
                
        except requests.RequestException as e:
            print(f"⚠️ Error al realizar la petición a {url}: {e}")
        
        # Esperar antes de reintentar
        if intento < REINTENTOS_PETICIONES - 1:
            time.sleep(DELAY_ENTRE_PETICIONES * (intento + 1))  # Backoff exponencial
    
    return None

def fetch_with_selenium(url):
    """
    Realiza una petición HTTP usando Selenium para cargar páginas dinámicas.
    
    Args:
        url (str): URL a la que realizar la petición
        
    Returns:
        str: Contenido HTML de la página, o None si hubo un error
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Configurar opciones de Chrome
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={get_random_user_agent()}")
        
        # Iniciar el navegador
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Cargar la página
        driver.get(url)
        
        # Esperar a que la página cargue completamente
        time.sleep(5)
        
        # Obtener el HTML
        html_content = driver.page_source
        
        # Cerrar el navegador
        driver.quit()
        
        return html_content
    
    except Exception as e:
        print(f"⚠️ Error al usar Selenium para {url}: {e}")
        return None

def fetch_with_playwright(url):
    """
    Realiza una petición HTTP usando Playwright para cargar páginas dinámicas.
    
    Args:
        url (str): URL a la que realizar la petición
        
    Returns:
        str: Contenido HTML de la página, o None si hubo un error
    """
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            # Lanzar navegador
            browser = p.chromium.launch(headless=True)
            
            # Crear contexto con User-Agent personalizado
            context = browser.new_context(
                user_agent=get_random_user_agent(),
                viewport={"width": 1920, "height": 1080}
            )
            
            # Crear página
            page = context.new_page()
            
            # Navegar a la URL
            page.goto(url, wait_until="networkidle")
            
            # Obtener el HTML
            html_content = page.content()
            
            # Cerrar navegador
            browser.close()
            
            return html_content
    
    except Exception as e:
        print(f"⚠️ Error al usar Playwright para {url}: {e}")
        return None
