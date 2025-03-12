from bs4 import BeautifulSoup
from src.utils.filters import filtrar_productos_irrelevantes
from src.scrapers.base_scraper import detectar_modelo, crear_producto_base, filtrar_productos_validos
import re

def extraer_precio_amazon(precio_tag):
    """
    Extrae el precio de un elemento de Amazon.
    """
    try:
        if not precio_tag:
            return 0.0
            
        precio_text = precio_tag.text.strip()
        # Extraer solo números y punto decimal
        precio_limpio = re.sub(r'[^\d.]', '', precio_text)
        if precio_limpio:
            return float(precio_limpio)
        return 0.0
    except (ValueError, AttributeError) as e:
        print(f"Error extrayendo precio de Amazon: {e}")
        return 0.0

def scrape_amazon_page(html_content):
    """
    Extrae la información relevante de cada producto de una página de resultados de Amazon.
    
    Para cada producto, se extraen:
      - Nombre, precio, link, imagen, vendedor (opcional) y ID del producto.
      - Se detecta el modelo usando detectar_modelo.
      - Se asigna 'Amazon' como tienda.
      
    Solo se incluyen productos con precio mayor a 0 y cuyo modelo no sea 'Otro'.
    Finalmente se filtran productos irrelevantes usando una lista de palabras prohibidas.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    productos = []
    ids_vistos = set()  # Para evitar duplicados
    
    print(f"Analizando página de Amazon. Longitud HTML: {len(html_content)}")
    
    # Buscar los contenedores de productos - probamos múltiples selectores
    items = soup.find_all('div', {'data-component-type': 's-search-result'})
    
    # Si no se encuentran con el selector anterior, probar con otros selectores
    if not items:
        items = soup.find_all('div', class_=lambda c: c and ('s-result-item' in c))
        print(f"Usando selector alternativo (s-result-item). Encontrados: {len(items)} items")
    
    if not items:
        items = soup.find_all('div', class_=lambda c: c and ('sg-col-4-of-12' in c))
        print(f"Usando selector alternativo (sg-col). Encontrados: {len(items)} items")
    
    print(f"Total de items encontrados: {len(items)}")
    
    for item in items:
        try:
            # Extraer ID del producto
            producto_id = ""
            data_asin = item.get('data-asin')
            if data_asin:
                producto_id = data_asin
            else:
                # Intentar extraer de otras formas
                asin_tag = item.find('div', {'data-asin': True})
                if asin_tag:
                    producto_id = asin_tag.get('data-asin')
            
            if not producto_id:
                continue
                
            if producto_id in ids_vistos:
                continue
                
            ids_vistos.add(producto_id)
            
            # Extraer nombre del producto - probamos múltiples selectores
            nombre = None
            
            # 1. Buscar en el span dentro del h2
            h2_tag = item.find('h2', class_='a-size-mini')
            if h2_tag:
                span_tag = h2_tag.find('span')
                if span_tag:
                    nombre = span_tag.text.strip()
            
            # 2. Si no se encuentra, buscar en el span con clase a-text-normal
            if not nombre:
                nombre_tag = item.find('span', class_='a-text-normal')
                if nombre_tag:
                    nombre = nombre_tag.text.strip()
            
            # 3. Buscar en el título del enlace
            if not nombre:
                link_tag = item.find('a', class_='a-link-normal')
                if link_tag:
                    title_tag = link_tag.find('span', class_='a-text-normal')
                    if title_tag:
                        nombre = title_tag.text.strip()
            
            # 4. Buscar en cualquier h2
            if not nombre:
                h2_tag = item.find('h2')
                if h2_tag:
                    nombre = h2_tag.text.strip()
            
            # 5. Buscar en el atributo alt de la imagen
            if not nombre:
                img_tag = item.find('img', class_='s-image')
                if img_tag and img_tag.get('alt'):
                    nombre = img_tag['alt'].strip()
            
            # Si aún no tenemos nombre, usar un valor por defecto
            if not nombre:
                nombre = "Nombre no disponible"
            
            # Extraer link
            link = ""
            a_tag = item.find('a', class_=lambda c: c and ('a-link-normal' in c))
            if a_tag and a_tag.get('href'):
                link = a_tag['href']
                if not link.startswith('http'):
                    link = f"https://www.amazon.com.mx{link}"
            
            # Extraer precio
            precio = 0.0
            precio_tag = item.find('span', class_=lambda c: c and ('a-price-whole' in c))
            if precio_tag:
                precio = extraer_precio_amazon(precio_tag)
            
            # Si no se encuentra, buscar en otros formatos
            if precio <= 0:
                precio_tag = item.find('span', class_=lambda c: c and ('a-offscreen' in c))
                if precio_tag:
                    precio = extraer_precio_amazon(precio_tag)
            
            if precio <= 0:
                continue
            
            # Extraer imagen
            imagen = ""
            img_tag = item.find('img', class_=lambda c: c and ('s-image' in c))
            if img_tag and img_tag.get('src'):
                imagen = img_tag['src']
                # Intentar obtener imagen de mayor resolución
                if '_AC_UL320_' in imagen:
                    imagen = imagen.replace('_AC_UL320_', '_AC_SL1500_')
                elif '_AC_UL640_' in imagen:
                    imagen = imagen.replace('_AC_UL640_', '_AC_SL1500_')
                elif '_SR' in imagen:
                    # Extraer el ID base de la imagen
                    base_id_match = re.search(r'I\/([^._]+)', imagen)
                    if base_id_match:
                        base_id = base_id_match.group(1)
                        # Crear URL de alta calidad
                        imagen = f"https://m.media-amazon.com/images/I/{base_id}_AC_SL1500_.jpg"
            
            # Imprimir la URL de la imagen para depuración
            print(f"URL de imagen Amazon: {imagen}")
            
            # Extraer vendedor (si está disponible)
            vendedor = ""
            vendedor_tag = item.find('span', class_=lambda c: c and ('a-size-small' in c) and ('a-color-base' in c))
            if vendedor_tag:
                vendedor_text = vendedor_tag.text.strip()
                if "por " in vendedor_text.lower():
                    vendedor = vendedor_text.split("por ")[1].strip()
            
            # Crear producto usando la función base
            producto = crear_producto_base(
                tienda='Amazon',
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
            print(f"Error procesando producto de Amazon: {e}")
    
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