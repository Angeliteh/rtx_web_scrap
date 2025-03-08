from bs4 import BeautifulSoup
import re
from filters import filtrar_productos_irrelevantes
from scrapers.base_scraper import crear_producto_base, filtrar_productos_validos

def scrape_mercadolibre_page(html_content):
    """
    Extrae la información relevante de cada producto de una página de resultados de MercadoLibre.
    
    Para cada producto, se extraen:
      - Nombre, precio, link, imagen, vendedor (opcional) y ID del producto.
      - Se detecta el modelo usando detectar_modelo.
      - Se asigna 'MercadoLibre' como tienda.
      
    Solo se incluyen productos con precio mayor a 0 y cuyo modelo no sea 'Otro'.
    Finalmente se filtran productos irrelevantes usando una lista de palabras prohibidas.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    productos = []
    ids_vistos = set()  # Para evitar duplicados
    
    # Buscar los contenedores de productos - actualizado para incluir la nueva clase
    items = soup.find_all('li', class_=lambda c: c and ('ui-search-layout__item' in c))
    
    for item in items:
        try:
            # Buscar el enlace del producto - actualizado para la nueva estructura
            link_tag = None
            
            # Buscar en la nueva estructura (poly-component__title)
            titulo_tag = item.find('a', class_='poly-component__title')
            if titulo_tag and titulo_tag.get('href'):
                link_tag = titulo_tag
            else:
                # Mantener la búsqueda anterior como fallback
                link_tag = item.find('a', class_='ui-search-item__group__element')
            
            if not link_tag or not link_tag.get('href'):
                continue
                
            link = link_tag['href']
            
            # Extraer ID del producto de la URL con una expresión regular más robusta
            # Buscamos patrones como /p/MLM12345678, /MLM-12345678, etc.
            producto_id = ""
            mlm_pattern = re.search(r'\/(?:p\/|)(?:MLM|MLA|MCO|MEC)[-]?(\d+)', link)
            
            if mlm_pattern:
                producto_id = f"MLM{mlm_pattern.group(1)}"
            
            # Si no se pudo extraer un ID, generamos uno a partir de la URL
            if not producto_id:
                # Usar los últimos 10 caracteres de la URL como ID
                producto_id = f"ML-{link[-10:]}"
            
            if producto_id in ids_vistos:
                continue
                
            ids_vistos.add(producto_id)
            
            # Extraer nombre - actualizado para la nueva estructura
            nombre = "Nombre no disponible"
            nombre_tag = item.find('a', class_='poly-component__title')
            if nombre_tag:
                nombre = nombre_tag.text.strip()
            else:
                # Fallback al método anterior
                nombre_tag = item.find('h2', class_='ui-search-item__title')
                if nombre_tag:
                    nombre = nombre_tag.text.strip()
            
            # Extraer precio - actualizado para la nueva estructura
            precio = 0.0
            
            # Buscar el precio en el formato del nuevo HTML
            precio_tag = item.find('span', class_='andes-money-amount__fraction')
            if precio_tag:
                precio_text = precio_tag.text.replace('.', '').replace(',', '').strip()
                
                try:
                    precio = float(precio_text)
                except ValueError:
                    precio = 0.0
            else:
                # Fallback al método anterior
                precio_tag = item.find('span', class_='price-tag-fraction')
                if precio_tag:
                    precio_text = precio_tag.text.replace('.', '').strip()
                    
                    # Manejar decimales si existen
                    decimales_tag = item.find('span', class_='price-tag-cents')
                    decimales = decimales_tag.text.strip() if decimales_tag else "00"
                    
                    try:
                        precio = float(f"{precio_text}.{decimales}")
                    except ValueError:
                        precio = 0.0
            
            # Extraer imagen - actualizado para la nueva estructura
            imagen = ""
            img_tag = item.find('img', class_='poly-component__picture')
            if img_tag and img_tag.get('src'):
                imagen = img_tag['src']
            else:
                # Fallback al método anterior
                img_tag = item.find('img', class_='ui-search-result-image__element')
                if img_tag:
                    if img_tag.get('data-src'):
                        imagen = img_tag['data-src']
                    elif img_tag.get('src'):
                        imagen = img_tag['src']
            
            # Extraer vendedor - actualizado para la nueva estructura
            vendedor = ""
            vendedor_tag = item.find('span', class_='poly-component__seller')
            if vendedor_tag:
                vendedor = vendedor_tag.text.strip().replace('Por ', '')
            else:
                # Fallback al método anterior
                vendedor_tag = item.find('p', class_='ui-search-official-store-label')
                if vendedor_tag:
                    vendedor = vendedor_tag.text.strip()
            
            # Crear producto usando la función base
            producto = crear_producto_base(
                tienda='MercadoLibre',
                nombre=nombre,
                precio=precio,
                link=link,
                imagen=imagen,
                id_producto=producto_id,
                vendedor=vendedor
            )
            
            productos.append(producto)
        except Exception as e:
            print(f"Error procesando producto de MercadoLibre: {e}")
    
    # Filtrar productos con precio mayor a 0 y modelo reconocido
    productos = filtrar_productos_validos(productos)
    # Aplicar filtro para descartar productos irrelevantes
    productos = filtrar_productos_irrelevantes(productos)
    
    return productos 