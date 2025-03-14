from bs4 import BeautifulSoup
import re
from src.utils.filters import filtrar_productos_irrelevantes
from src.scrapers.base_scraper import detectar_modelo, crear_producto_base, filtrar_productos_validos

def extraer_precio_mercadolibre(precio_tag):
    """
    Extrae el precio de un elemento de MercadoLibre.
    """
    try:
        if not precio_tag:
            return 0.0
            
        precio_text = precio_tag.text.strip()
        # Extraer solo números y punto decimal
        precio_limpio = re.sub(r'[^\d]', '', precio_text)
        if precio_limpio:
            return float(precio_limpio)
        return 0.0
    except (ValueError, AttributeError) as e:
        print(f"Error extrayendo precio de MercadoLibre: {e}")
        return 0.0

def transformar_url_imagen(url_original):
    """
    Transforma la URL de la imagen de MercadoLibre para obtener la versión de mejor calidad.
    
    Patrones de transformación:
    - D_Q_NP -> D_NQ_NP (mejor calidad)
    - -V.webp -> -F.webp (imagen completa)
    - -O.webp -> -F.webp (sin optimización)
    """
    if not url_original or 'http2.mlstatic.com' not in url_original:
        return url_original

    url_transformada = url_original

    # Transformaciones principales
    transformaciones = [
        ('D_Q_NP', 'D_NQ_NP'),      # Mejora la calidad
        ('D_Q_NP_2X', 'D_NQ_NP_2X'),  # Mejora la calidad en imágenes 2X
        ('-V.webp', '-F.webp'),      # Cambia a versión completa
        ('-O.webp', '-F.webp'),      # Cambia optimizada a completa
        ('.jpg', '-F.webp'),         # Cambia JPG a WebP
    ]

    for viejo, nuevo in transformaciones:
        url_transformada = url_transformada.replace(viejo, nuevo)

    print(f"URL original: {url_original}")
    print(f"URL transformada: {url_transformada}")
    
    return url_transformada

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
    
    print(f"Analizando página de MercadoLibre. Longitud HTML: {len(html_content)}")
    
    # Buscar los contenedores de productos - actualizado para incluir la nueva clase
    items = soup.find_all('li', class_=lambda c: c and ('ui-search-layout__item' in c))
    
    # Si no se encuentran con el selector anterior, probar con el nuevo formato
    if not items:
        items = soup.find_all('div', class_=lambda c: c and ('poly-card' in c))
        print(f"Usando selector alternativo (poly-card). Encontrados: {len(items)} items")
    
    print(f"Total de items encontrados: {len(items)}")
    
    for item in items:
        try:
            # Buscar el enlace del producto - actualizado para la nueva estructura
            link = ""
            
            # Buscar en la nueva estructura (poly-component__title)
            titulo_tag = item.find('a', class_='poly-component__title')
            if titulo_tag and titulo_tag.get('href'):
                link = titulo_tag['href']
                nombre = titulo_tag.text.strip()
            else:
                # Mantener la búsqueda anterior como fallback
                link_tag = item.find('a', class_='ui-search-item__group__element')
                if link_tag and link_tag.get('href'):
                    link = link_tag['href']
                    nombre_tag = item.find('h2', class_='ui-search-item__title')
                    nombre = nombre_tag.text.strip() if nombre_tag else "Nombre no disponible"
                else:
                    continue
            
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
            
            # Extraer precio - actualizado para la nueva estructura
            precio = 0.0
            
            # Buscar el precio en el formato del nuevo HTML (poly-component)
            precio_tag = item.find('span', class_='andes-money-amount__fraction')
            if precio_tag:
                precio = extraer_precio_mercadolibre(precio_tag)
            else:
                # Fallback al método anterior
                precio_tag = item.find('span', class_='price-tag-fraction')
                if precio_tag:
                    precio = extraer_precio_mercadolibre(precio_tag)
            
            if precio <= 0:
                continue
            
            # Extraer imagen - actualizado para la nueva estructura
            imagen = ""
            img_tag = item.find('img', class_='poly-component__picture')
            if not img_tag:
                img_tag = item.find('img', class_='ui-search-result-image__element')
            
            if img_tag:
                # Intentar obtener la URL de la imagen
                imagen = img_tag.get('data-src') or img_tag.get('src', '')
                # Transformar la URL
                imagen = transformar_url_imagen(imagen)
            
            # Imprimir la URL final de la imagen para depuración
            print(f"URL final de imagen: {imagen}")
            
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
            
            print(f"Producto encontrado: {nombre[:50]}... - ${precio}")
            productos.append(producto)
        except Exception as e:
            print(f"Error procesando producto de MercadoLibre: {e}")
    
    # Filtrar productos con precio mayor a 0 y modelo reconocido
    productos_validos = filtrar_productos_validos(productos)
    # Aplicar filtro para descartar productos irrelevantes
    productos_filtrados = filtrar_productos_irrelevantes(productos_validos)
    
    print(f"Total de productos encontrados: {len(productos)}")
    print(f"Total de productos con modelo reconocido: {len(productos_validos)}")
    print(f"Total de productos válidos después de filtrar: {len(productos_filtrados)}")
    
    # Si no hay productos válidos pero sí hay productos, incluir algunos aunque no tengan modelo reconocido
    if len(productos_filtrados) == 0 and len(productos) > 0:
        print("No se encontraron productos válidos, incluyendo algunos sin modelo reconocido...")
        # Filtrar solo por precio y palabras prohibidas
        productos_filtrados = [p for p in productos if p['precio'] > 0]
        productos_filtrados = filtrar_productos_irrelevantes(productos_filtrados)
        print(f"Total de productos incluidos sin filtro de modelo: {len(productos_filtrados)}")
    
    return productos_filtrados 