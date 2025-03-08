from utils import fetch_page
from scrapers.mercadolibre_scraper import scrape_mercadolibre_page
import time

# URLs para cada modelo
urls = [
    "https://listado.mercadolibre.com.mx/rtx-4060",
    "https://listado.mercadolibre.com.mx/rtx-4070",
    "https://listado.mercadolibre.com.mx/rtx-4080",
    "https://listado.mercadolibre.com.mx/rtx-4090"
]

total_productos = 0

for url in urls:
    print(f"\nObteniendo productos de: {url}")
    
    # Obtener el HTML usando Selenium para cargar el contenido dinámico
    html = fetch_page(url, use_selenium=True)
    print(f"Longitud del HTML: {len(html)}")
    
    # Guardar el HTML para análisis (solo el primero)
    if "4060" in url:
        with open('mercadolibre_real.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("HTML guardado en mercadolibre_real.html")
    
    # Extraer productos
    productos = scrape_mercadolibre_page(html)
    print(f"Productos encontrados: {len(productos)}")
    
    # Mostrar los primeros 3 productos (si hay)
    for i, producto in enumerate(productos[:3]):
        print(f"\nProducto {i+1}:")
        print(f"Nombre: {producto['nombre']}")
        print(f"Modelo: {producto['modelo']}")
        print(f"Precio: ${producto['precio']}")
        print(f"ID: {producto['id_producto']}")
    
    total_productos += len(productos)
    
    # Esperar un poco entre peticiones para evitar bloqueos
    time.sleep(2)

print(f"\nTotal de productos encontrados: {total_productos}")

# Verificar si hay elementos li con la clase ui-search-layout__item en el HTML
if "4060" in urls[0]:
    with open('mercadolibre_real.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Buscar elementos li con clase que contenga ui-search-layout__item
    items = soup.find_all('li', class_=lambda c: c and ('ui-search-layout__item' in c))
    print(f"\nElementos li con clase ui-search-layout__item encontrados: {len(items)}")
    
    # Buscar elementos con clase poly-component__title
    titulos = soup.find_all('a', class_='poly-component__title')
    print(f"Elementos a con clase poly-component__title encontrados: {len(titulos)}")
    
    # Mostrar las primeras 5 clases de elementos li para análisis
    li_elements = soup.find_all('li')
    print(f"\nPrimeros 5 elementos li y sus clases:")
    for i, li in enumerate(li_elements[:5]):
        print(f"Li {i+1}: {li.get('class', 'Sin clase')}")
        
    # Buscar otros posibles elementos que contengan productos
    print("\nBuscando otros posibles elementos que contengan productos:")
    
    # Buscar divs con clase que contenga "ui-search-result"
    result_divs = soup.find_all('div', class_=lambda c: c and ('ui-search-result' in c))
    print(f"Divs con clase ui-search-result: {len(result_divs)}")
    
    # Buscar divs con clase que contenga "poly-card"
    poly_cards = soup.find_all('div', class_=lambda c: c and ('poly-card' in c))
    print(f"Divs con clase poly-card: {len(poly_cards)}")
    
    # Si encontramos poly-cards, mostrar la estructura del primero
    if poly_cards:
        print("\nEstructura del primer poly-card:")
        card = poly_cards[0]
        
        # Buscar título
        titulo = card.find('a', class_='poly-component__title')
        if titulo:
            print(f"Título: {titulo.text.strip()}")
            print(f"Enlace: {titulo.get('href', 'No encontrado')}")
        
        # Buscar precio
        precio = card.find('span', class_='andes-money-amount__fraction')
        if precio:
            print(f"Precio: {precio.text.strip()}")
        
        # Buscar vendedor
        vendedor = card.find('span', class_='poly-component__seller')
        if vendedor:
            print(f"Vendedor: {vendedor.text.strip()}")
        
        # Buscar imagen
        imagen = card.find('img', class_='poly-component__picture')
        if imagen:
            print(f"Imagen: {imagen.get('src', 'No encontrada')}") 