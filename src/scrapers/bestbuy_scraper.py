from bs4 import BeautifulSoup
from src.utils.filters import filtrar_productos_irrelevantes
from src.scrapers.base_scraper import detectar_modelo, crear_producto_base, filtrar_productos_validos

def scrape_bestbuy_page(html_content):
    """
    Extrae la información relevante de cada producto de una página de resultados de BestBuy.
    
    Para cada producto, se extraen:
      - Nombre, precio, link, imagen, vendedor (opcional) y ID del producto.
      - Se detecta el modelo usando detectar_modelo.
      - Se asigna 'BestBuy' como tienda.
      
    Solo se incluyen productos con precio mayor a 0 y cuyo modelo no sea 'Otro'.
    Finalmente se filtran productos irrelevantes usando una lista de palabras prohibidas.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    productos = []
    ids_vistos = set()  # Para evitar duplicados
    
    # Buscar los contenedores de productos
    items = soup.find_all('div', class_='sku-item')
    
    for item in items:
        try:
            # Extraer el ID del producto
            sku_id = item.get('data-sku-id', "")
            
            if not sku_id or sku_id in ids_vistos:
                continue
                
            ids_vistos.add(sku_id)
            
            # Extraer nombre
            nombre_tag = item.find('h4', class_='sku-title')
            nombre = nombre_tag.text.strip() if nombre_tag else "Nombre no disponible"
            
            # Extraer precio
            precio_tag = item.find('div', class_='priceView-customer-price')
            precio_text = ""
            if precio_tag:
                precio_span = precio_tag.find('span')
                if precio_span:
                    precio_text = precio_span.text.replace('$', '').replace(',', '').strip()
            
            # Convertir a float
            try:
                precio = float(precio_text)
            except (ValueError, TypeError):
                precio = 0.0
            
            # Extraer link
            link = ""
            link_tag = item.find('a', class_='image-link')
            if link_tag and link_tag.get('href'):
                link = link_tag['href']
                if not link.startswith('http'):
                    link = f"https://www.bestbuy.com.mx{link}"
            
            # Extraer imagen
            imagen = ""
            img_tag = item.find('img', class_='product-image')
            if img_tag and img_tag.get('src'):
                imagen = img_tag['src']
            
            # Extraer vendedor (si está disponible)
            vendedor = "BestBuy"  # Por defecto, BestBuy es el vendedor
            vendedor_tag = item.find('div', class_='partner-name')
            if vendedor_tag:
                vendedor = vendedor_tag.text.strip()
            
            # Crear producto usando la función base
            producto = crear_producto_base(
                tienda='BestBuy',
                nombre=nombre,
                precio=precio,
                link=link,
                imagen=imagen,
                id_producto=sku_id,
                vendedor=vendedor
            )
            
            productos.append(producto)
        except Exception as e:
            print(f"Error procesando producto de BestBuy: {e}")
    
    # Filtrar productos con precio mayor a 0 y modelo reconocido
    productos = filtrar_productos_validos(productos)
    # Aplicar filtro para descartar productos irrelevantes
    productos = filtrar_productos_irrelevantes(productos)
    
    return productos 