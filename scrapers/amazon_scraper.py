from bs4 import BeautifulSoup
from filters import filtrar_productos_irrelevantes
from scrapers.base_scraper import detectar_modelo, crear_producto_base, filtrar_productos_validos

def scrape_amazon_page(html_content):
    """
    Extrae la información relevante de cada producto de una página de resultados de Amazon.
    
    Para cada producto, se extraen:
      - Nombre, precio, link, imagen, vendedor (opcional) y ID del producto (ASIN).
      - Se detecta el modelo usando detectar_modelo.
      - Se asigna 'Amazon' como tienda.
      
    Solo se incluyen productos con precio mayor a 0 y cuyo modelo no sea 'Otro'.
    Finalmente se filtran productos irrelevantes usando una lista de palabras prohibidas.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    productos = []
    ids_vistos = set()  # Para evitar duplicados
     
    # Buscar los contenedores de productos
    items = soup.find_all('div', {'data-component-type': 's-search-result'})
    
    for item in items:
        try:
            # Extraer el ASIN (Amazon Standard Identification Number)
            asin = item.get('data-asin', "")
            
            if not asin or asin in ids_vistos:
                continue
                
            ids_vistos.add(asin)
            
            # Extraer nombre
            nombre_tag = item.find('h2')
            if not nombre_tag:
                continue
                
            nombre_link = nombre_tag.find('a')
            nombre = nombre_link.text.strip() if nombre_link else "Nombre no disponible"
            
            # Extraer precio
            precio_tag = item.find('span', class_='a-offscreen')
            precio_text = precio_tag.text.replace('$', '').replace(',', '').strip() if precio_tag else "0"
            
            # Convertir a float
            try:
                precio = float(precio_text)
            except ValueError:
                precio = 0.0
            
            # Extraer link
            link = ""
            if nombre_link and nombre_link.get('href'):
                link = nombre_link['href']
                if not link.startswith('http'):
                    link = f"https://www.amazon.com.mx{link}"
            
            # Extraer imagen
            imagen_tag = item.find('img', class_='s-image')
            imagen = imagen_tag['src'] if imagen_tag and imagen_tag.get('src') else ""
            
            # Extraer vendedor (si está disponible)
            vendedor_tag = item.find('div', class_='a-row a-size-base a-color-secondary')
            vendedor = vendedor_tag.text.strip() if vendedor_tag else "Amazon"
            
            # Crear producto usando la función base
            producto = crear_producto_base(
                tienda='Amazon',
                nombre=nombre,
                precio=precio,
                link=link,
                imagen=imagen,
                id_producto=asin,  # Usamos el ASIN como ID de producto
                vendedor=vendedor
            )
            
            productos.append(producto)
        except Exception as e:
            print(f"Error procesando producto de Amazon: {e}")
    
    # Filtrar productos con precio mayor a 0 y modelo reconocido
    productos = filtrar_productos_validos(productos)
    # Aplicar filtro para descartar productos irrelevantes
    productos = filtrar_productos_irrelevantes(productos)
    
    return productos 