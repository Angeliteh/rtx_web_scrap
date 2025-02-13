import requests
from bs4 import BeautifulSoup
import time
import random
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt

# ==============================
# Configuración inicial
# ==============================
DATABASE_NAME = "gpu_prices.db"       # Nombre de la base de datos SQLite
CSV_NAME = "productos.csv"             # Nombre del archivo CSV (si se desea exportar)
MODELOS_BUSQUEDA = ['4070', '4080', '4090']  # Modelos a buscar en Amazon
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
]

# ==============================
# Funciones de utilidad para HTTP
# ==============================
def get_random_user_agent():
    """Devuelve un User-Agent aleatorio para simular distintos navegadores."""
    return random.choice(USER_AGENTS)

def get_headers():
    """Genera los headers necesarios para la solicitud HTTP a Amazon."""
    return {
        "User-Agent": get_random_user_agent(),
        "Accept-Language": "es-MX,es;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Referer": "https://www.amazon.com.mx/",
        "Connection": "keep-alive",
    }

def fetch_page(url, headers):
    """
    Realiza la solicitud HTTP a la URL dada y retorna el contenido HTML
    si la respuesta es exitosa.
    """
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        if "CAPTCHA" in response.text:
            print("¡Bloqueado por CAPTCHA!")
            return None
        return response.content
    else:
        print(f"Error: No se pudo acceder a la página. Código de estado: {response.status_code}")
        return None

# ==============================
# Funciones para la Base de Datos
# ==============================
def crear_tabla():
    """
    Crea la tabla 'productos' si no existe.
    Se incluyen campos para:
      - tienda (para identificar el origen, por ejemplo 'Amazon')
      - modelo, nombre, precio, fecha, vendedor, link e imagen.
    Esto permite almacenar productos de distintos marketplaces en una única tabla.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tienda TEXT,
                modelo TEXT,
                nombre TEXT,
                precio REAL,
                fecha DATETIME,
                vendedor TEXT,
                link TEXT,
                imagen TEXT
                )''')
    conn.commit()
    conn.close()

def guardar_en_db(productos):
    """
    Guarda en la base de datos una lista de productos.
    Cada producto es un diccionario con la información extraída.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    for producto in productos:
        c.execute('''INSERT INTO productos 
                    (tienda, modelo, nombre, precio, fecha, vendedor, link, imagen)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (producto.get('tienda', 'Amazon'),
                 producto['modelo'],
                 producto['nombre'],
                 producto['precio'],
                 datetime.now().isoformat(),
                 producto.get('vendedor', ''),
                 producto.get('link', ''),
                 producto.get('imagen', '')
                ))
    
    conn.commit()
    conn.close()

# ==============================
# Funciones de Análisis y Estadísticas
# ==============================
def obtener_estadisticas():
    """
    Obtiene estadísticas de precios para cada modelo de GPU (RTX 4070, 4080, 4090).
    Calcula:
      - Precio mínimo, máximo y promedio.
      - Las 5 mejores ofertas (productos con precio inferior al promedio).
    """
    conn = sqlite3.connect(DATABASE_NAME)
    c = conn.cursor()
    
    estadisticas = {}
    for modelo in MODELOS_BUSQUEDA:
        c.execute('''SELECT MIN(precio), MAX(precio), AVG(precio)
                    FROM productos WHERE modelo = ?''', (f"RTX {modelo}",))
        min_price, max_price, avg_price = c.fetchone()
        
        # Selecciona las 5 mejores ofertas (productos cuyo precio es menor al promedio)
        c.execute('''SELECT nombre, precio FROM productos 
                    WHERE modelo = ? AND precio < ?
                    ORDER BY precio LIMIT 5''', (f"RTX {modelo}", avg_price))
        mejores_ofertas = c.fetchall()
        
        estadisticas[f"RTX {modelo}"] = {
            'min': min_price,
            'max': max_price,
            'avg': avg_price,
            'ofertas': mejores_ofertas
        }
    
    conn.close()
    return estadisticas

# ==============================
# Función de Filtrado de Productos
# ==============================
def filtrar_productos_por_busqueda(productos, filtro):
    """
    Filtra la lista de productos según el criterio de búsqueda.
    Por ejemplo:
      - Si se ingresa 'rtx 4070', se devolverán todos los productos que contengan '4070'
        en su nombre o en su modelo (incluyendo variantes como 'Ti' o 'Super').
      - Si se ingresa 'super', se filtrarán solo los productos que contengan 'super'.
    """
    filtro = filtro.lower()
    return [p for p in productos if filtro in p['nombre'].lower() or filtro in p['modelo'].lower()]

# ==============================
# Funciones para Generar URL y Detectar Modelo
# ==============================
def get_search_url(modelo):
    """
    Genera la URL de búsqueda para un modelo específico en Amazon.
    Ejemplo: Para modelo '4070' genera la URL para buscar "rtx 4070".
    """
    return f"https://www.amazon.com.mx/s?k=rtx+{modelo}"

def detectar_modelo(nombre_producto):
    """
    Detecta el modelo de la GPU a partir del nombre del producto.
    Retorna 'RTX <modelo>' si se encuentra alguno de los modelos en MODELOS_BUSQUEDA,
    de lo contrario retorna 'Otro'.
    """
    for modelo in MODELOS_BUSQUEDA:
        if modelo in nombre_producto:
            return f"RTX {modelo}"
    return "Otro"

# ==============================
# Función de Scraping para Amazon
# ==============================
def scrape_amazon_page(html_content):
    """
    Extrae la información relevante de cada producto de una página de resultados de Amazon.
    
    Para cada producto, se extraen:
      - Nombre del producto.
      - Precio (convertido a float).
      - Modelo detectado (usando detectar_modelo).
      - Vendedor (si está disponible).
      - Link de compra (se genera la URL completa al producto).
      - Imagen del producto (URL de la imagen).
      - Se asigna 'Amazon' como tienda.
      
    Sólo se incluyen productos con precio mayor a 0 y cuyo modelo no sea 'Otro'.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    productos = []
    PALABRAS_PROHIBIDAS = ["soporte", "stand", "cable", "hub", "extensor", "base", "refrigeración", "extensión", "adaptador", "computadora", "estación"]

    
    for item in soup.find_all('div', {'data-component-type': 's-search-result'}):
        try:
            # Extraer nombre del producto
            nombre_tag = item.find('h2')
            nombre = nombre_tag.text.strip() if nombre_tag else "Nombre no disponible"
            
            # Validamos que no contenga palabras clave prohibidas
            if any(palabra in nombre.lower() for palabra in PALABRAS_PROHIBIDAS):
                print(f"Descartando producto no válido: {nombre}")
                continue  # Salta este producto


            # Extraer precio
            precio_tag = item.find('span', class_='a-offscreen')
            precio_text = precio_tag.text.replace('$', '').replace(',', '').strip() if precio_tag else ""
            precio = float(precio_text) if precio_text and precio_text.replace('.', '', 1).isdigit() else 0.0
            
            # Extraer link de compra
            link_tag = item.find('a', class_='a-link-normal s-line-clamp-4 s-link-style a-text-normal')
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
    
    # Se filtran productos con precio mayor a 0 y modelo reconocido
    return [p for p in productos if p['precio'] > 0 and p['modelo'] != "Otro"]

# ==============================
# Flujo Principal del Programa
# ==============================
def main():
    """
    Flujo general:
      1. Se crea la base de datos y la tabla si no existen.
      2. Por cada modelo en MODELOS_BUSQUEDA, se genera la URL de búsqueda y se obtiene el HTML.
      3. Se realiza el scraping de la página de Amazon con scrape_amazon_page.
      4. Los productos extraídos se guardan en la base de datos.
      5. Se realiza un ejemplo de filtrado (por ejemplo, productos que contengan 'super').
      6. Se generan estadísticas (mínimo, máximo, promedio y mejores ofertas).
      7. Se crea un gráfico de barras con los precios promedio.
    """
    crear_tabla()
    todos_productos = []
    
    for modelo in MODELOS_BUSQUEDA:
        print(f"Buscando RTX {modelo} en Amazon...")
        url = get_search_url(modelo)
        html_content = fetch_page(url, get_headers())
        
        if html_content:
            productos = scrape_amazon_page(html_content)
            guardar_en_db(productos)
            todos_productos.extend(productos)
            time.sleep(random.uniform(2, 5))  # Delay aleatorio para evitar bloqueos
    
    # Ejemplo de filtrado: filtrar productos que contengan 'super'
    filtro = "super"
    productos_filtrados = filtrar_productos_por_busqueda(todos_productos, filtro)
    print(f"\nProductos filtrados con '{filtro}':")
    for p in productos_filtrados:
        print(f"Nombre: {p['nombre']}\nPrecio: ${p['precio']}\nLink: {p['link']}\nImagen: {p['imagen']}\n")
    
    # Generar reporte de estadísticas
    stats = obtener_estadisticas()
    for modelo, data in stats.items():
        print(f"\nEstadísticas para {modelo}:")
        print(f"Precio mínimo: ${data['min']}")
        print(f"Precio máximo: ${data['max']}")
        print(f"Precio promedio: ${data['avg']:.2f}")
        print("Mejores ofertas:")
        for oferta in data['ofertas']:
            print(f"- {oferta[0]} (${oferta[1]})")
    
    # Generar gráfico de precios promedio (opcional)
    modelos = [f"RTX {m}" for m in MODELOS_BUSQUEDA]
    promedios = [stats[f"RTX {m}"]['avg'] for m in MODELOS_BUSQUEDA]
    
    plt.bar(modelos, promedios, color='skyblue')
    plt.title('Precios Promedio de GPUs')
    plt.ylabel('Precio (MXN)')
    plt.savefig('precios_promedio.png')
    plt.close()
    print("\nGráfico de precios promedio guardado como 'precios_promedio.png'.")

if __name__ == "__main__":
    main()
