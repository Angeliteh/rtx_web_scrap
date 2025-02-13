# filters.py
from config import PALABRAS_PROHIBIDAS

def filtrar_productos_por_busqueda(productos, filtro):
    """
    Filtra la lista de productos según el criterio de búsqueda.
    Por ejemplo:
      - Si se ingresa 'rtx 4070', se devolverán todos los productos que contengan '4070'
        en su nombre o modelo (incluyendo variantes como 'Ti' o 'Super').
      - Si se ingresa 'super', se filtrarán solo los productos que contengan 'super'.
    """
    filtro = filtro.lower()
    return [p for p in productos if filtro in p['nombre'].lower() or filtro in p['modelo'].lower()]

def filtrar_productos_irrelevantes(productos):
    """
    Filtra productos que contienen palabras prohibidas en su nombre,
    descartando aquellos que probablemente no sean tarjetas gráficas.
    """
    return [p for p in productos if not any(palabra in p['nombre'].lower() for palabra in PALABRAS_PROHIBIDAS)]
