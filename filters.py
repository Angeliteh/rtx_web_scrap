# filters.py
"""
Módulo con funciones para filtrar productos según diferentes criterios.
"""

def filtrar_productos_irrelevantes(productos):
    """
    Filtra productos irrelevantes como cables, soportes, fundas, etc.
    
    Args:
        productos (list): Lista de diccionarios con información de productos
        
    Returns:
        list: Lista filtrada de productos
    """
    palabras_prohibidas = [
        'cable', 'adaptador', 'soporte', 'funda', 'carcasa', 'cooler', 
        'ventilador', 'disipador', 'pasta térmica', 'thermal paste',
        'stand', 'holder', 'bracket', 'case', 'cover', 'skin', 'protector',
        'power supply', 'fuente de poder', 'psu', 'mouse pad', 'mousepad',
        'alfombrilla', 'poster', 'sticker', 'pegatina', 'llavero', 'keychain'
    ]
    
    productos_filtrados = []
    
    for producto in productos:
        nombre = producto.get('nombre', '').lower()
        es_relevante = True
        
        # Verificar si el nombre contiene alguna palabra prohibida
        for palabra in palabras_prohibidas:
            if palabra.lower() in nombre:
                es_relevante = False
                break
        
        if es_relevante:
            productos_filtrados.append(producto)
    
    return productos_filtrados

def filtrar_productos_por_busqueda(productos, termino_busqueda):
    """
    Filtra productos según un término de búsqueda.
    
    Args:
        productos (list): Lista de diccionarios con información de productos
        termino_busqueda (str): Término a buscar en el nombre, modelo o vendedor
        
    Returns:
        list: Lista filtrada de productos que coinciden con el término de búsqueda
    """
    if not termino_busqueda:
        return productos
    
    termino_busqueda = termino_busqueda.lower()
    productos_filtrados = []
    
    for producto in productos:
        nombre = producto.get('nombre', '').lower()
        modelo = producto.get('modelo', '').lower()
        vendedor = producto.get('vendedor', '').lower()
        tienda = producto.get('tienda', '').lower()
        
        # Verificar si el término de búsqueda está en alguno de los campos
        if (termino_busqueda in nombre or 
            termino_busqueda in modelo or 
            termino_busqueda in vendedor or
            termino_busqueda in tienda):
            productos_filtrados.append(producto)
    
    return productos_filtrados
