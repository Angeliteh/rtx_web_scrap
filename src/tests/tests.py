import unittest
import os
import json
from bs4 import BeautifulSoup
from unittest.mock import patch, MagicMock

# Importar funciones a probar
from scrapers.amazon_scraper import scrape_amazon_page
from scrapers.mercadolibre_scraper import scrape_mercadolibre_page
from scrapers.newegg_scraper import scrape_newegg_page
from scrapers.base_scraper import detectar_modelo, crear_producto_base, filtrar_productos_validos
from filters import filtrar_productos_irrelevantes, filtrar_productos_por_busqueda
from database import crear_tabla, guardar_en_db, obtener_historial_precios
from utils import get_random_user_agent, get_headers

# Directorio para almacenar archivos HTML de prueba
TEST_DATA_DIR = "test_data"

class TestScrapers(unittest.TestCase):
    """Pruebas para los scrapers de diferentes tiendas"""
    
    @classmethod
    def setUpClass(cls):
        """Crear directorio para datos de prueba si no existe"""
        if not os.path.exists(TEST_DATA_DIR):
            os.makedirs(TEST_DATA_DIR)
    
    def setUp(self):
        """Configuración antes de cada prueba"""
        # Crear archivos HTML de ejemplo si no existen
        self.crear_html_ejemplo()
    
    def crear_html_ejemplo(self):
        """Crea archivos HTML de ejemplo para pruebas"""
        # Amazon
        if not os.path.exists(f"{TEST_DATA_DIR}/amazon_example.html"):
            with open(f"{TEST_DATA_DIR}/amazon_example.html", "w", encoding="utf-8") as f:
                f.write("""
                <html>
                <body>
                    <div data-component-type="s-search-result" data-asin="B0BHJJ2NHT">
                        <h2><a class="a-link-normal s-line-clamp-4 s-link-style a-text-normal" href="/dp/B0BHJJ2NHT/">ASUS TUF Gaming NVIDIA GeForce RTX 4070 OC</a></h2>
                        <span class="a-offscreen">$12,999.00</span>
                        <img class="s-image" src="https://example.com/image1.jpg">
                        <div class="a-row a-size-base a-color-secondary">Vendido por: ASUS Store</div>
                    </div>
                </body>
                </html>
                """)
        
        # MercadoLibre
        if not os.path.exists(f"{TEST_DATA_DIR}/mercadolibre_example.html"):
            with open(f"{TEST_DATA_DIR}/mercadolibre_example.html", "w", encoding="utf-8") as f:
                f.write("""
                <html>
                <body>
                    <li class="ui-search-layout__item">
                        <a class="poly-component__title" href="https://www.mercadolibre.com.mx/tarjeta-de-video-asus-dual-geforce-rtx-4070-evo-oc-edition-12gb-gddr6x-dual-rtx4070-o12g-evo/p/MLM37557470">MSI Gaming X Trio RTX 4080 Super 16GB GDDR6X</a>
                        <span class="andes-money-amount__fraction">19999</span>
                        <img class="poly-component__picture" src="https://example.com/image2.jpg">
                        <span class="poly-component__seller">Por MSI Official Store</span>
                    </li>
                </body>
                </html>
                """)
        
        # Newegg
        if not os.path.exists(f"{TEST_DATA_DIR}/newegg_example.html"):
            with open(f"{TEST_DATA_DIR}/newegg_example.html", "w", encoding="utf-8") as f:
                f.write("""
                <html>
                <body>
                    <div class="item-cell">
                        <div class="item-container">
                            <a class="item-title" href="https://www.newegg.com/p/N82E16814137771?Item=N82E16814137771">MSI Gaming X Trio GeForce RTX 4090 24GB GDDR6X</a>
                            <li class="price-current">
                                <strong>1,999</strong>
                                <sup>99</sup>
                            </li>
                            <img class="item-img" src="https://example.com/image3.jpg">
                            <div class="item-branding">
                                <a>MSI</a>
                            </div>
                        </div>
                    </div>
                </body>
                </html>
                """)
    
    def test_amazon_scraper(self):
        """Prueba la extracción de productos de Amazon"""
        with open(f"{TEST_DATA_DIR}/amazon_example.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        productos = scrape_amazon_page(html_content)
        
        # Verificar que se extrajo al menos un producto
        self.assertGreaterEqual(len(productos), 1)
        
        # Verificar que el primer producto tiene los campos esperados
        if productos:
            producto = productos[0]
            self.assertEqual(producto['tienda'], 'Amazon')
            self.assertEqual(producto['modelo'], 'RTX 4070')
            self.assertIn('ASUS TUF Gaming NVIDIA GeForce RTX 4070', producto['nombre'])
            self.assertGreater(producto['precio'], 0)
            self.assertIn('ASUS', producto['vendedor'])
            self.assertIn('B0BHJJ2NHT', producto['id_producto'])
    
    def test_mercadolibre_scraper(self):
        """Prueba la extracción de productos de MercadoLibre"""
        with open(f"{TEST_DATA_DIR}/mercadolibre_example.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        productos = scrape_mercadolibre_page(html_content)
        
        # Verificar que se extrajo al menos un producto
        self.assertGreaterEqual(len(productos), 1)
        
        # Verificar que el primer producto tiene los campos esperados
        if productos:
            producto = productos[0]
            self.assertEqual(producto['tienda'], 'MercadoLibre')
            self.assertEqual(producto['modelo'], 'RTX 4080')
            self.assertIn('MSI Gaming X Trio RTX 4080', producto['nombre'])
            self.assertGreater(producto['precio'], 0)
            self.assertIn('MSI', producto['vendedor'])
            self.assertIn('MLM', producto['id_producto'])
    
    def test_newegg_scraper(self):
        """Prueba la extracción de productos de Newegg"""
        with open(f"{TEST_DATA_DIR}/newegg_example.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        
        productos = scrape_newegg_page(html_content)
        
        # Verificar que se extrajo al menos un producto
        self.assertGreaterEqual(len(productos), 1)
        
        # Verificar que el primer producto tiene los campos esperados
        if productos:
            producto = productos[0]
            self.assertEqual(producto['tienda'], 'Newegg')
            self.assertEqual(producto['modelo'], 'RTX 4090')
            self.assertIn('MSI Gaming X Trio GeForce RTX 4090', producto['nombre'])
            self.assertGreater(producto['precio'], 0)
            self.assertIn('MSI', producto['vendedor'])
            self.assertIn('N82E16814137771', producto['id_producto'])

class TestFuncionesBase(unittest.TestCase):
    """Pruebas para las funciones base del scraper"""
    
    def test_detectar_modelo(self):
        """Prueba la detección de modelos de GPU"""
        self.assertEqual(detectar_modelo("NVIDIA GeForce RTX 4070 Ti"), "RTX 4070")
        self.assertEqual(detectar_modelo("MSI Gaming X Trio RTX 4080 Super"), "RTX 4080")
        self.assertEqual(detectar_modelo("ASUS ROG Strix GeForce RTX 4090 OC"), "RTX 4090")
        self.assertEqual(detectar_modelo("Tarjeta de video GTX 1660"), "Otro")
    
    def test_crear_producto_base(self):
        """Prueba la creación de un producto base"""
        producto = crear_producto_base(
            tienda="Amazon",
            nombre="ASUS TUF Gaming NVIDIA GeForce RTX 4070 OC",
            precio=12999.00,
            link="https://example.com/product",
            imagen="https://example.com/image.jpg",
            id_producto="B0BHJJ2NHT",
            vendedor="ASUS Store"
        )
        
        self.assertEqual(producto['tienda'], "Amazon")
        self.assertEqual(producto['modelo'], "RTX 4070")
        self.assertEqual(producto['nombre'], "ASUS TUF Gaming NVIDIA GeForce RTX 4070 OC")
        self.assertEqual(producto['precio'], 12999.00)
        self.assertEqual(producto['link'], "https://example.com/product")
        self.assertEqual(producto['imagen'], "https://example.com/image.jpg")
        self.assertEqual(producto['id_producto'], "B0BHJJ2NHT")
        self.assertEqual(producto['vendedor'], "ASUS Store")
    
    def test_filtrar_productos_validos(self):
        """Prueba el filtrado de productos válidos"""
        productos = [
            {'modelo': 'RTX 4070', 'precio': 12999.00},
            {'modelo': 'RTX 4080', 'precio': 0},
            {'modelo': 'Otro', 'precio': 9999.00},
            {'modelo': 'RTX 4090', 'precio': 29999.00}
        ]
        
        filtrados = filtrar_productos_validos(productos)
        
        self.assertEqual(len(filtrados), 2)
        self.assertEqual(filtrados[0]['modelo'], 'RTX 4070')
        self.assertEqual(filtrados[1]['modelo'], 'RTX 4090')
    
    def test_filtrar_productos_irrelevantes(self):
        """Prueba el filtrado de productos irrelevantes"""
        productos = [
            {'nombre': 'ASUS TUF Gaming NVIDIA GeForce RTX 4070 OC', 'modelo': 'RTX 4070'},
            {'nombre': 'Cable adaptador para RTX 4080', 'modelo': 'RTX 4080'},
            {'nombre': 'Soporte para tarjeta gráfica RTX 4090', 'modelo': 'RTX 4090'},
            {'nombre': 'MSI Gaming X Trio RTX 4080 Super 16GB', 'modelo': 'RTX 4080'}
        ]
        
        filtrados = filtrar_productos_irrelevantes(productos)
        
        self.assertEqual(len(filtrados), 2)
        self.assertIn('ASUS TUF Gaming', filtrados[0]['nombre'])
        self.assertIn('MSI Gaming X Trio', filtrados[1]['nombre'])
    
    def test_filtrar_productos_por_busqueda(self):
        """Prueba el filtrado de productos por búsqueda"""
        productos = [
            {'nombre': 'ASUS TUF Gaming NVIDIA GeForce RTX 4070 OC', 'modelo': 'RTX 4070'},
            {'nombre': 'MSI Gaming X Trio RTX 4080 Super 16GB', 'modelo': 'RTX 4080'},
            {'nombre': 'ASUS ROG Strix GeForce RTX 4090 OC', 'modelo': 'RTX 4090'}
        ]
        
        # Filtrar por modelo
        filtrados = filtrar_productos_por_busqueda(productos, '4080')
        self.assertEqual(len(filtrados), 1)
        self.assertIn('4080', filtrados[0]['modelo'])
        
        # Filtrar por marca
        filtrados = filtrar_productos_por_busqueda(productos, 'ASUS')
        self.assertEqual(len(filtrados), 2)
        
        # Filtrar por término específico
        filtrados = filtrar_productos_por_busqueda(productos, 'Super')
        self.assertEqual(len(filtrados), 1)
        self.assertIn('Super', filtrados[0]['nombre'])

class TestUtils(unittest.TestCase):
    """Pruebas para las utilidades"""
    
    def test_get_random_user_agent(self):
        """Prueba la obtención de un User-Agent aleatorio"""
        user_agent = get_random_user_agent()
        self.assertIsNotNone(user_agent)
        self.assertIsInstance(user_agent, str)
    
    def test_get_headers(self):
        """Prueba la obtención de headers para las solicitudes HTTP"""
        headers = get_headers()
        self.assertIsNotNone(headers)
        self.assertIn('User-Agent', headers)
        self.assertIn('Accept-Language', headers)

@patch('database.get_db_connection')
class TestDatabase(unittest.TestCase):
    """Pruebas para las funciones de base de datos"""
    
    def test_crear_tabla(self, mock_get_db_connection):
        """Prueba la creación de tablas en la base de datos"""
        # Configurar el mock para SQLite
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = (mock_conn, "sqlite")
        
        crear_tabla()
        
        # Verificar que se llamaron los métodos correctos
        mock_conn.cursor.assert_called_once()
        self.assertEqual(mock_cursor.execute.call_count, 2)  # Dos CREATE TABLE
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    def test_guardar_en_db_nuevo_producto(self, mock_get_db_connection):
        """Prueba guardar un nuevo producto en la base de datos"""
        # Configurar el mock para SQLite
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = (mock_conn, "sqlite")
        
        # Simular que el producto no existe
        mock_cursor.fetchone.return_value = None
        
        # Producto de prueba
        productos = [{
            'tienda': 'Amazon',
            'modelo': 'RTX 4070',
            'nombre': 'ASUS TUF Gaming NVIDIA GeForce RTX 4070 OC',
            'precio': 12999.00,
            'vendedor': 'ASUS Store',
            'link': 'https://example.com/product',
            'imagen': 'https://example.com/image.jpg',
            'id_producto': 'B0BHJJ2NHT'
        }]
        
        guardar_en_db(productos)
        
        # Verificar que se llamaron los métodos correctos
        mock_conn.cursor.assert_called_once()
        self.assertEqual(mock_cursor.execute.call_count, 3)  # SELECT, INSERT productos, INSERT historial
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    def test_obtener_historial_precios(self, mock_get_db_connection):
        """Prueba obtener el historial de precios de un producto"""
        # Configurar el mock para SQLite
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db_connection.return_value = (mock_conn, "sqlite")
        
        # Simular resultados de la consulta
        mock_cursor.fetchall.return_value = [
            ('2023-05-01', 12999.00, 'ASUS Store'),
            ('2023-04-15', 13499.00, 'ASUS Store'),
            ('2023-04-01', 13999.00, 'ASUS Store')
        ]
        
        historial = obtener_historial_precios('B0BHJJ2NHT', limite=3)
        
        # Verificar que se llamaron los métodos correctos
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once()
        mock_conn.close.assert_called_once()
        
        # Verificar el formato del historial
        self.assertEqual(len(historial), 3)
        self.assertIn('fecha', historial[0])
        self.assertIn('precio', historial[0])
        self.assertIn('vendedor', historial[0])
        self.assertEqual(historial[0]['precio'], 12999.00)

if __name__ == '__main__':
    unittest.main() 