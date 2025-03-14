# config.py

# Configuración de la base de datos
DATABASE_TYPE = "sqlite"  # Opciones: "sqlite", "postgresql", "mongodb"
DATABASE_NAME = "gpu_prices.db"
CSV_NAME = "productos.csv"

# Sitios habilitados para realizar scraping
SITIOS_HABILITADOS = ['amazon', 'mercadolibre']  # Solo Amazon y MercadoLibre habilitados para pruebas

# Configuración para conexión a PostgreSQL (si se utiliza)
POSTGRES_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'gpu_prices',
    'user': 'postgres',
    'password': 'postgres'
}

# Configuración para MongoDB (si se utiliza)
MONGODB_CONFIG = {
    'host': 'localhost',
    'port': 27017,
    'database': 'gpu_prices',
    'collection': 'productos'
}

# Modelos a buscar en los sitios web
MODELOS_BUSQUEDA = ['4060', '4070', '4080']

# Lista de User-Agents para evitar bloqueos
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1"
]

# Lista de palabras prohibidas para filtrar productos irrelevantes (no GPUs)
PALABRAS_PROHIBIDAS = [
    "soporte", "stand", "cable", "hub", "extensor", "base",
    "refrigeración", "extensión", "adaptador", "computadora", "estación", "laptop", "placa",
    "pines", "pin", "awg", "pc", "water", "block", "hybrid", "icue", "aegis", "personalizada",
    "t3for", "k4for", "atx3.0", "pci-e", "procesador"
]

# Configuración para alertas de precios
ALERTA_ACTIVADA = True
UMBRAL_PRECIO_PORCENTAJE = 10  # Alerta cuando el precio cae un 10% o más
EMAIL_ALERTAS = "usuario@ejemplo.com"

# Configuración de Telegram para alertas
TELEGRAM_ACTIVADO = False
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

# Configuración de Discord para alertas
DISCORD_ACTIVADO = False
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"

# Flag para mostrar el gráfico en pantalla (True) o guardarlo (False)
MOSTRAR_GRAFICO = True

# Configuración de proxies (para evitar bloqueos)
USAR_PROXIES = False
PROXIES = [
    "http://user:pass@proxy1.example.com:8080",
    "http://user:pass@proxy2.example.com:8080"
]

# Configuración del intervalo de escaneo (en minutos)
INTERVALO_ESCANEO = 60

# Configuración para peticiones HTTP
TIMEOUT_PETICIONES = 30  # Tiempo máximo de espera para peticiones en segundos
REINTENTOS_PETICIONES = 3  # Número de reintentos si falla una petición
DELAY_ENTRE_PETICIONES = 2  # Tiempo de espera entre peticiones en segundos

# Configuración para pruebas unitarias
TEST_DATABASE_NAME = "test_gpu_prices.db"  # Base de datos para pruebas
TEST_DATA_DIR = "test_data"  # Directorio para datos de prueba
