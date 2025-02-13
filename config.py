# config.py

# Nombre de la base de datos y archivo CSV (si se desea exportar)
DATABASE_NAME = "gpu_prices.db"
CSV_NAME = "productos.csv"

# Modelos a buscar en Amazon
MODELOS_BUSQUEDA = ['4070', '4080', '4090']

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
    "refrigeración", "extensión", "adaptador", "computadora", "estación", "laptop", "placa"
]

# Flag para mostrar el gráfico en pantalla (True) o guardarlo (False)
MOSTRAR_GRAFICO = True
