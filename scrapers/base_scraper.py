# scrapers/base_scraper.py
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