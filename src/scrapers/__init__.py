# scrapers/__init__.py
"""
Paquete que contiene los módulos de scraping para diferentes sitios web.
Cada sitio tiene su propio módulo con una función principal que sigue el patrón:
scrape_<sitio>_page(html_content) -> list[dict]
"""

__all__ = [
    'amazon_scraper',
    'mercadolibre_scraper',
    'newegg_scraper',
    'bestbuy_scraper',
    'aliexpress_scraper'
] 