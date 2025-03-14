import time
import random
from src.config.config import MODELOS_BUSQUEDA, SITIOS_HABILITADOS
from src.utils.utils import fetch_page, get_headers
from src.database.database import crear_tabla, guardar_en_db, obtener_historial_precios
from src.utils.alerts import enviar_alertas

# Importación de scrapers según configuración
from src.scrapers.amazon_scraper import scrape_amazon_page
from src.scrapers.mercadolibre_scraper import scrape_mercadolibre_page

def ejecutar_scraper():
    """
    Ejecuta el proceso de scraping y almacena los datos en la base de datos.
    Se puede llamar desde Flask o ejecutarlo manualmente.
    """
    crear_tabla()
    todos_productos = []

    # Mapa de funciones de scraping por sitio
    scrapers = {
        'amazon': {'func': scrape_amazon_page, 'url_template': "https://www.amazon.com.mx/s?k=rtx+{}"},
        'mercadolibre': {'func': scrape_mercadolibre_page, 'url_template': "https://listado.mercadolibre.com.mx/rtx-{}"}
    }
    
    for sitio in SITIOS_HABILITADOS:
        if sitio not in scrapers:
            print(f"⚠️ Sitio {sitio} no implementado. Omitiendo...")
            continue
            
        for modelo in MODELOS_BUSQUEDA:
            scraper_info = scrapers[sitio]
            print(f"🔍 Buscando RTX {modelo} en {sitio.capitalize()}...")
            
            url = scraper_info['url_template'].format(modelo)
            html_content = fetch_page(url)

            if html_content:
                productos = scraper_info['func'](html_content)
                
                for producto in productos:
                    try:
                        # Obtener historial de precios y desempaquetar la tupla
                        historial_precios, info_producto = obtener_historial_precios(producto['id_producto'], limite=2)
                        
                        # Verificar si hay suficiente historial
                        if historial_precios and len(historial_precios) >= 2:
                            precio_anterior = historial_precios[1]['precio']
                            # Enviar alertas si es necesario
                            enviar_alertas(producto, precio_anterior)
                        else:
                            print(f"ℹ️ Primer registro o sin historial para el producto {producto.get('nombre', 'Nombre desconocido')} ({producto.get('id_producto', 'ID desconocido')})")
                    except Exception as e:
                        print(f"❌ Error procesando historial del producto {producto.get('id_producto', 'ID desconocido')}: {str(e)}")
                        continue
                
                # Guardar productos en la base de datos
                guardar_en_db(productos)
                todos_productos.extend(productos)
                
                # Delay aleatorio entre peticiones
                time.sleep(random.uniform(2, 5))
                
    print("✅ Scraping completado y datos almacenados en la base de datos.")
    return todos_productos

# Si se ejecuta directamente este archivo, correrá el scraper
if __name__ == "__main__":
    ejecutar_scraper()
