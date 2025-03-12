from bs4 import BeautifulSoup
from src.utils.filters import filtrar_productos_irrelevantes
from src.scrapers.base_scraper import detectar_modelo, crear_producto_base, filtrar_productos_validos

def scrape_aliexpress_page(html_content):
    """
    Extrae la información relevante de cada producto de una página de resultados de AliExpress.
    
    Para cada producto, se extraen:
      - Nombre, precio, link, imagen, vendedor (opcional) y ID del producto.
      - Se detecta el modelo usando detectar_modelo.
      - Se asigna 'AliExpress' como tienda.
      
    Solo se incluyen productos con precio mayor a 0 y cuyo modelo no sea 'Otro'.
    Finalmente se filtran productos irrelevantes usando una lista de palabras prohibidas.
    
    Nota: AliExpress utiliza JavaScript para cargar los productos, por lo que es posible
    que sea necesario utilizar Selenium o Playwright para obtener el HTML completo.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    productos = []
    ids_vistos = set()  # Para evitar duplicados
    
    # Buscar los contenedores de productos
    items = soup.find_all('div', class_='_3t7zg')  # Clase de los items de producto
    
    for item in items:
        try:
            # Extraer el ID del producto (de la URL o del elemento)
            link_tag = item.find('a')
            if not link_tag or not link_tag.get('href'):
                continue
                
            link = link_tag['href']
            if not link.startswith('http'):
                link = f"https:{link}"
                
            # Extraer ID del producto de la URL
            producto_id = ""
            if "item/" in link:
                producto_id = link.split("item/")[1].split(".")[0]
            
            if not producto_id or producto_id in ids_vistos:
                continue
                
            ids_vistos.add(producto_id)
            
            # Extraer nombre
            nombre_tag = item.find('h1', class_='_18_85')  # Clase del título
            nombre = nombre_tag.text.strip() if nombre_tag else "Nombre no disponible"
            
            # Extraer precio
            precio_tag = item.find('div', class_='_12A8D')  # Clase del precio
            precio_text = ""
            if precio_tag:
                precio_text = precio_tag.text.replace('US $', '').replace(',', '').strip()
            
            # Convertir a float (y convertir de USD a MXN aproximadamente)
            try:
                precio = float(precio_text) * 17.5  # Factor de conversión aproximado USD a MXN
            except (ValueError, TypeError):
                precio = 0.0
            
            # Extraer imagen
            imagen = ""
            img_tag = item.find('img')
            if img_tag:
                if img_tag.get('src'):
                    imagen = img_tag['src']
                elif img_tag.get('data-src'):
                    imagen = img_tag['data-src']
                
                if imagen and not imagen.startswith('http'):
                    imagen = f"https:{imagen}"
            
            # Extraer vendedor (si está disponible)
            vendedor_tag = item.find('a', class_='_3Yugq')  # Clase del vendedor
            vendedor = vendedor_tag.text.strip() if vendedor_tag else "Vendedor no disponible"
            
            # Crear producto usando la función base
            producto = crear_producto_base(
                tienda='AliExpress',
                nombre=nombre,
                precio=precio,
                link=link,
                imagen=imagen,
                id_producto=producto_id,
                vendedor=vendedor
            )
            
            productos.append(producto)
        except Exception as e:
            print(f"Error procesando producto de AliExpress: {e}")
    
    # Filtrar productos con precio mayor a 0 y modelo reconocido
    productos = filtrar_productos_validos(productos)
    # Aplicar filtro para descartar productos irrelevantes
    productos = filtrar_productos_irrelevantes(productos)
    
    return productos 