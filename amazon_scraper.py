# amazon_scraper.py
from bs4 import BeautifulSoup
from filters import filtrar_productos_irrelevantes
from config import MODELOS_BUSQUEDA

def detectar_modelo(nombre_producto):
    """
    Detecta el modelo de la GPU a partir del nombre del producto.
    Retorna 'RTX <modelo>' si se encuentra alguno de los modelos en MODELOS_BUSQUEDA;
    de lo contrario retorna 'Otro'.
    """
    for modelo in MODELOS_BUSQUEDA:
        if modelo in nombre_producto:
            return f"RTX {modelo}"
    return "Otro"

def scrape_amazon_page(html_content):
    """
    Extrae la información relevante de cada producto de una página de resultados de Amazon.
    
    Para cada producto, se extraen:
      - Nombre, precio, link, imagen, y vendedor (opcional).
      - Se detecta el modelo usando detectar_modelo.
      - Se asigna 'Amazon' como tienda.
      
    Solo se incluyen productos con precio mayor a 0 y cuyo modelo no sea 'Otro'.
    Finalmente se filtran productos irrelevantes (ej.: cables, stands, etc.) usando una lista de palabras prohibidas.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    productos = []
    
    for item in soup.find_all('div', {'data-component-type': 's-search-result'}):
        try:
            nombre_tag = item.find('h2')
            nombre = nombre_tag.text.strip() if nombre_tag else "Nombre no disponible"
            
            # Extraer precio
            precio_tag = item.find('span', class_='a-offscreen')
            precio_text = precio_tag.text.replace('$', '').replace(',', '').strip() if precio_tag else ""
            precio = float(precio_text) if precio_text and precio_text.replace('.', '', 1).isdigit() else 0.0
            
            # Extraer link de compra
            link_tag = item.find('a', class_='a-link-normal')
            link = ""
            if link_tag and link_tag.get('href'):
                href = link_tag['href']
                link = href if href.startswith("http") else "https://www.amazon.com.mx" + href
            
            # Extraer imagen del producto
            imagen_tag = item.find('img', class_='s-image')
            imagen = imagen_tag['src'] if imagen_tag and imagen_tag.get('src') else ""
            
            # Extraer vendedor (opcional)
            vendedor_tag = item.find('div', class_='a-row a-size-base a-color-secondary')
            vendedor = vendedor_tag.text.split('|')[-1].strip() if vendedor_tag else ""
            
            producto = {
                'tienda': 'Amazon',
                'modelo': detectar_modelo(nombre),
                'nombre': nombre,
                'precio': precio,
                'vendedor': vendedor,
                'link': link,
                'imagen': imagen
            }
            
            productos.append(producto)
        except Exception as e:
            print(f"Error procesando producto: {e}")
    
    # Filtrar productos con precio mayor a 0 y modelo reconocido
    productos = [p for p in productos if p['precio'] > 0 and p['modelo'] != "Otro"]
    # Aplicar filtro para descartar productos irrelevantes (ej.: cables, stands, etc.)
    productos = filtrar_productos_irrelevantes(productos)
    
    return productos
