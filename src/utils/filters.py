# filters.py
"""
Módulo con funciones para filtrar productos según diferentes criterios.
"""

def filtrar_productos_irrelevantes(productos):
    """
    Filtra productos irrelevantes como cables, soportes, fundas, etc.
    Utiliza un sistema mejorado de detección basado en palabras clave y análisis de patrones.
    
    Args:
        productos (list): Lista de diccionarios con información de productos
        
    Returns:
        list: Lista filtrada de productos
    """
    # Lista ampliada de palabras prohibidas organizadas por categorías
    accesorios = [
        'cable', 'adaptador', 'conversor', 'connector', 'conector', 'extensor', 
        'hub', 'splitter', 'extension', 'alargador', 'riser', 'switch', 'kvm'
    ]
    
    soportes = [
        'soporte', 'base', 'stand', 'holder', 'bracket', 'mount', 'rack', 
        'apoyo', 'patas', 'elevador', 'dock', 'docking'
    ]
    
    protecciones = [
        'funda', 'carcasa', 'case', 'cover', 'skin', 'protector', 'sleeve',
        'bag', 'bolsa', 'estuche', 'maletin', 'protección', 'protection'
    ]
    
    refrigeracion = [
        'cooler', 'ventilador', 'fan', 'disipador', 'cooling', 'refrigeración',
        'heatsink', 'radiador', 'thermal', 'térmico', 'pasta térmica', 'thermal paste',
        'watercooling', 'water cooling', 'liquid cooling', 'enfriamiento'
    ]
    
    decorativos = [
        'poster', 'sticker', 'pegatina', 'llavero', 'keychain', 'figura', 'figure',
        'adorno', 'decoración', 'decoration', 'art', 'arte', 'pin', 'pines', 'badge'
    ]
    
    otros = [
        'power supply', 'fuente de poder', 'psu', 'mouse pad', 'mousepad',
        'alfombrilla', 'monitor', 'pantalla', 'screen', 'teclado', 'keyboard',
        'mouse', 'ratón', 'headset', 'auriculares', 'audífonos', 'PC', 'desktop',
        'portatil', 'laptop', 'notebook', 'cámara', 'camera', 'webcam', 'micrófono',
        'microphone', 'parlante', 'speaker', 'escritorio', 'desk', 'silla', 'chair',
        'ram', 'memory', 'memoria', 'ssd', 'hdd', 'disco', 'drive', 'motherboard',
        'placa base', 'placa madre', 'tarjeta madre', 'mother board'
    ]
    
    # Combinamos todas las categorías
    palabras_prohibidas = accesorios + soportes + protecciones + refrigeracion + decorativos + otros
    
    # Palabras que indican definitivamente que es una GPU
    palabras_gpu = [
        'geforce', 'rtx', 'nvidia', 'graphics card', 'tarjeta gráfica', 
        'tarjeta de video', 'gpu', 'graphics processing unit', 'gddr', 'vram'
    ]
    
    productos_filtrados = []
    
    for producto in productos:
        nombre = producto.get('nombre', '').lower()
        es_relevante = True
        
        # Si el precio es demasiado bajo para ser una GPU, probablemente no sea relevante
        if producto.get('precio', 0) < 2000:  # Asumiendo que una GPU RTX 4000 no costará menos de 2000 pesos
            es_relevante = False
        
        # Verificar si el nombre contiene alguna palabra prohibida
        palabras_prohibidas_encontradas = []
        for palabra in palabras_prohibidas:
            if palabra.lower() in nombre:
                palabras_prohibidas_encontradas.append(palabra)
        
        # Verificar si el nombre contiene palabras que indican que es una GPU
        palabras_gpu_encontradas = []
        for palabra in palabras_gpu:
            if palabra.lower() in nombre:
                palabras_gpu_encontradas.append(palabra)
        
        # Reglas de decisión mejoradas:
        # 1. Si tiene más palabras prohibidas que palabras de GPU, probablemente no es relevante
        # 2. Si tiene palabras específicas que son muy indicativas de no ser una GPU, no es relevante
        # 3. Si tiene "rtx" o "geforce" y no tiene palabras muy específicas de accesorios, es relevante
        
        if len(palabras_prohibidas_encontradas) > len(palabras_gpu_encontradas):
            es_relevante = False
        
        # Algunas palabras son muy indicativas de accesorios, incluso si menciona GPU
        muy_especificas = ['cable', 'soporte', 'base', 'funda', 'adaptador', 'conversor', 'pasta']
        for palabra in muy_especificas:
            if palabra in nombre:
                es_relevante = False
                break
        
        # Si contiene rtx y no tiene palabras muy específicas de accesorios, probablemente es relevante
        if ('rtx' in nombre or 'geforce' in nombre) and not any(p in nombre for p in muy_especificas):
            es_relevante = True
        
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
