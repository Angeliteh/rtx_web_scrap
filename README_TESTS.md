# Pruebas Unitarias para el Monitor de Precios de GPUs

Este documento explica cómo ejecutar las pruebas unitarias para el sistema de monitoreo de precios de GPUs y qué funcionalidades se están probando.

## Requisitos

Antes de ejecutar las pruebas, asegúrate de tener instaladas todas las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecutar las Pruebas

Para ejecutar todas las pruebas unitarias:

```bash
python -m unittest tests.py
```

Para ejecutar una clase de prueba específica:

```bash
python -m unittest tests.TestScrapers
```

Para ejecutar un método de prueba específico:

```bash
python -m unittest tests.TestScrapers.test_amazon_scraper
```

## Qué se está Probando

Las pruebas unitarias verifican las siguientes funcionalidades:

### 1. Scrapers de Tiendas (`TestScrapers`)

- **Amazon**: Verifica que el scraper de Amazon extraiga correctamente los productos, incluyendo nombre, precio, modelo, vendedor y ID de producto.
- **MercadoLibre**: Verifica que el scraper de MercadoLibre extraiga correctamente los productos.
- **Newegg**: Verifica que el scraper de Newegg extraiga correctamente los productos.

### 2. Funciones Base (`TestFuncionesBase`)

- **Detección de Modelos**: Verifica que la función `detectar_modelo` identifique correctamente los modelos de GPU en los nombres de productos.
- **Creación de Productos**: Verifica que la función `crear_producto_base` cree correctamente los diccionarios de productos.
- **Filtrado de Productos Válidos**: Verifica que la función `filtrar_productos_validos` filtre correctamente los productos sin precio o con modelo no reconocido.
- **Filtrado de Productos Irrelevantes**: Verifica que la función `filtrar_productos_irrelevantes` filtre correctamente productos que no son GPUs (cables, soportes, etc.).
- **Filtrado por Búsqueda**: Verifica que la función `filtrar_productos_por_busqueda` filtre correctamente los productos según un término de búsqueda.

### 3. Utilidades (`TestUtils`)

- **User-Agent Aleatorio**: Verifica que la función `get_random_user_agent` devuelva un User-Agent válido.
- **Headers HTTP**: Verifica que la función `get_headers` genere los headers correctos para las peticiones HTTP.

### 4. Base de Datos (`TestDatabase`)

- **Creación de Tablas**: Verifica que la función `crear_tabla` cree correctamente las tablas en la base de datos.
- **Guardar Productos**: Verifica que la función `guardar_en_db` guarde correctamente los productos en la base de datos.
- **Historial de Precios**: Verifica que la función `obtener_historial_precios` devuelva correctamente el historial de precios de un producto.

## Estructura de los Datos de Prueba

Las pruebas utilizan archivos HTML de ejemplo almacenados en el directorio `test_data/`. Estos archivos contienen ejemplos simplificados de páginas de resultados de cada tienda para probar los scrapers sin necesidad de realizar peticiones HTTP reales.

## Solución de Problemas

Si alguna prueba falla, el mensaje de error indicará qué prueba falló y por qué. Algunas causas comunes de fallos son:

1. **Cambios en la estructura HTML**: Si una tienda cambia la estructura de su página, el scraper correspondiente puede fallar. En este caso, será necesario actualizar el scraper.
2. **Problemas de conexión a la base de datos**: Verifica que la configuración de la base de datos sea correcta.
3. **Dependencias faltantes**: Asegúrate de tener todas las dependencias instaladas.

## Añadir Nuevas Pruebas

Para añadir nuevas pruebas:

1. Añade un nuevo método de prueba a la clase correspondiente en `tests.py`.
2. Si es necesario, añade nuevos archivos HTML de ejemplo en el directorio `test_data/`.
3. Ejecuta las pruebas para verificar que todo funciona correctamente. 