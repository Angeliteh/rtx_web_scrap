# scrapers/base_scraper.py
import re
from src.config.config import MODELOS_BUSQUEDA, PALABRAS_PROHIBIDAS

def detectar_modelo(nombre_producto):
    """
    Detecta el modelo de la GPU a partir del nombre del producto.
    Retorna 'RTX <modelo>' si se encuentra alguno de los modelos en MODELOS_BUSQUEDA;
    de lo contrario retorna 'Otro'.
    """
    nombre_lower = nombre_producto.lower()
    
    # Verificar si contiene "rtx" o "nvidia"
    if "rtx" in nombre_lower or "nvidia" in nombre_lower:
        # Buscar patrones como "rtx 4070", "rtx4070", "4070 ti", etc.
        for modelo in MODELOS_BUSQUEDA:
            # Patrones comunes
            patrones = [
                f"rtx{modelo}",
                f"rtx {modelo}",
                f"rtx-{modelo}",
                f"{modelo}ti",
                f"{modelo} ti",
                f"{modelo}-ti",
                f"{modelo}super",
                f"{modelo} super",
                f"{modelo}-super"
            ]
            
            # Verificar cada patrón
            for patron in patrones:
                if patron in nombre_lower:
                    return f"RTX {modelo}"
            
            # Verificar el modelo directamente
            if modelo in nombre_lower:
                return f"RTX {modelo}"
    
    # Si no se encontró ningún modelo, intentar con expresiones regulares
    rtx_pattern = re.search(r'rtx\s*(\d{4})', nombre_lower)
    if rtx_pattern:
        modelo_encontrado = rtx_pattern.group(1)
        # Verificar si el modelo encontrado está en la lista de modelos
        for modelo in MODELOS_BUSQUEDA:
            if modelo == modelo_encontrado:
                return f"RTX {modelo}"
    
    return "Otro"

def crear_producto_base(tienda, nombre, precio, link, imagen, id_producto, vendedor=""):
    """
    Crea un diccionario base para un producto con los campos comunes.
    
    Args:
        tienda (str): Nombre de la tienda (Amazon, MercadoLibre, etc.)
        nombre (str): Nombre del producto
        precio (float): Precio del producto
        link (str): Enlace al producto
        imagen (str): URL de la imagen del producto
        id_producto (str): Identificador único del producto
        vendedor (str, opcional): Nombre del vendedor
        
    Returns:
        dict: Diccionario con la información del producto
    """
    return {
        'tienda': tienda,
        'modelo': detectar_modelo(nombre),
        'nombre': nombre,
        'precio': precio,
        'vendedor': vendedor,
        'link': link,
        'imagen': imagen,
        'id_producto': id_producto  # Cambiado de 'asin' a 'id_producto' para mayor claridad
    }

def filtrar_productos_validos(productos):
    """
    Filtra los productos para incluir solo aquellos con precio mayor a 0
    y modelo reconocido (diferente de 'Otro').
    
    Args:
        productos (list): Lista de diccionarios de productos
        
    Returns:
        list: Lista filtrada de productos
    """
    return [p for p in productos if p['precio'] > 0 and p['modelo'] != "Otro"] 