from bs4 import BeautifulSoup
from src.utils.filters import filtrar_productos_irrelevantes
from src.scrapers.base_scraper import detectar_modelo, crear_producto_base, filtrar_productos_validos

def scrape_newegg_page(html_content):
    """
    Extrae la información relevante de cada producto de una página de resultados de Newegg.
    
    Para cada producto, se extraen:
      - Nombre, precio, link, imagen, vendedor (opcional) y ID del producto.
      - Se detecta el modelo usando detectar_modelo.
      - Se asigna 'Newegg' como tienda.
      
    Solo se incluyen productos con precio mayor a 0 y cuyo modelo no sea 'Otro'.
    Finalmente se filtran productos irrelevantes usando una lista de palabras prohibidas.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    productos = []
    ids_vistos = set()  # Para evitar duplicados
    
    # Buscar los contenedores de productos
    items = soup.find_all('div', class_='item-cell')
    
    for item in items:
        try:
            # Extraer el link y obtener el ID del producto de la URL
            link_tag = item.find('a', class_='item-title')
            if not link_tag or not link_tag.get('href'):
                continue
                
            link = link_tag['href']
            
            # Extraer ID del producto de la URL
            # El formato típico es: https://www.newegg.com/p/N82E16814xxx
            producto_id = ""
            if "Item=" in link:
                producto_id = link.split("Item=")[1].split("&")[0]
            elif "/p/" in link:
                producto_id = link.split("/p/")[1].split("?")[0]
            
            if not producto_id or producto_id in ids_vistos:
                continue
                
            ids_vistos.add(producto_id)
            
            # Extraer nombre
            nombre = link_tag.text.strip() if link_tag else "Nombre no disponible"
            
            # Extraer precio
            precio_tag = item.find('li', class_='price-current')
            precio = 0.0
            
            if precio_tag:
                # Precio en formato: <strong>1,999</strong><sup>99</sup>
                precio_entero = precio_tag.find('strong')
                precio_decimal = precio_tag.find('sup')
                
                if precio_entero:
                    precio_text = precio_entero.text.replace(',', '')
                    
                    if precio_decimal:
                        precio_text += '.' + precio_decimal.text
                    
                    try:
                        precio = float(precio_text)
                    except ValueError:
                        precio = 0.0
            
            # Extraer imagen
            imagen_tag = item.find('img', class_='item-img')
            imagen = imagen_tag['src'] if imagen_tag and imagen_tag.get('src') else ""
            
            # Extraer vendedor (si está disponible)
            vendedor_tag = item.find('div', class_='item-branding')
            vendedor = ""
            
            if vendedor_tag:
                vendedor_link = vendedor_tag.find('a')
                if vendedor_link:
                    vendedor = vendedor_link.text.strip()
            
            # Si no hay vendedor especificado, asumimos que es Newegg
            if not vendedor:
                vendedor = "Newegg"
            
            # Crear producto usando la función base
            producto = crear_producto_base(
                tienda='Newegg',
                nombre=nombre,
                precio=precio,
                link=link,
                imagen=imagen,
                id_producto=producto_id,
                vendedor=vendedor
            )
            
            productos.append(producto)
        except Exception as e:
            print(f"Error procesando producto de Newegg: {e}")
    
    # Filtrar productos con precio mayor a 0 y modelo reconocido
    productos = filtrar_productos_validos(productos)
    # Aplicar filtro para descartar productos irrelevantes
    productos = filtrar_productos_irrelevantes(productos)
    
    return productos 