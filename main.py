import time
import random
from config import MODELOS_BUSQUEDA
from utils import fetch_page, get_headers
from amazon_scraper import scrape_amazon_page
from database import crear_tabla, guardar_en_db

def ejecutar_scraper():
    """
    Ejecuta el proceso de scraping y almacena los datos en la base de datos.
    Se puede llamar desde Flask o ejecutarlo manualmente.
    """
    crear_tabla()
    todos_productos = []

    for modelo in MODELOS_BUSQUEDA:
        print(f"🔍 Buscando RTX {modelo} en Amazon...")
        url = f"https://www.amazon.com.mx/s?k=rtx+{modelo}"
        html_content = fetch_page(url)

        if html_content:
            productos = scrape_amazon_page(html_content)
            guardar_en_db(productos)
            todos_productos.extend(productos)
            time.sleep(random.uniform(2, 5))  # Delay aleatorio para evitar bloqueos

    print("✅ Scraping completado y datos almacenados en la base de datos.")

# Si se ejecuta directamente este archivo, correrá el scraper
if __name__ == "__main__":
    ejecutar_scraper()
