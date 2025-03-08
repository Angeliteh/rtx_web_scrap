from bs4 import BeautifulSoup
from scrapers.mercadolibre_scraper import scrape_mercadolibre_page
from scrapers.base_scraper import crear_producto_base, filtrar_productos_validos, detectar_modelo
from filters import filtrar_productos_irrelevantes
import re

# HTML de ejemplo proporcionado
html_ejemplo = """
<li class="ui-search-layout__item shops__layout-item"><div class="ui-search-result__wrapper"><div class="poly-card poly-card--list"><div class="poly-card__portada"><img width="150" height="150" decoding="sync" src="https://http2.mlstatic.com/D_Q_NP_2X_940224-MLA79721049641_102024-V.webp" class="poly-component__picture" fetchpriority="high" alt=""></div><div class="poly-card__content"><span style="color:#FFFFFF;background-color:#FF7733" class="poly-component__highlight">MÁS VENDIDO</span><span class="poly-component__brand">ASUS</span><h3 class="poly-component__title-wrapper"><a href="https://www.mercadolibre.com.mx/tarjeta-de-video-asus-dual-geforce-rtx-4060-v2-oc-8gb-gdrr6/p/MLM41420314#polycard_client=search-nordic&amp;searchVariation=MLM41420314&amp;wid=MLM3490400866&amp;position=3&amp;search_layout=stack&amp;type=product&amp;tracking_id=ce42b891-4f47-4e5b-bd48-05b345a2b3bc&amp;sid=search" target="_self" class="poly-component__title">Tarjeta De Video Asus Dual Geforce Rtx 4060 V2 Oc 8gb Gdrr6</a></h3><span class="poly-component__seller">Por Supergamer <svg aria-label="Tienda oficial" width="12" height="12" viewBox="0 0 12 12" role="img"><use href="#poly_cockade"></use></svg></span><div class="poly-content"><div class="poly-content__column"><div class="poly-component__price"><div class="poly-price__current"><span class="andes-money-amount andes-money-amount--cents-superscript" style="font-size:24px" role="img" aria-label="7499 pesos mexicanos" aria-roledescription="Monto"><span class="andes-money-amount__currency-symbol" aria-hidden="true">$</span><span class="andes-money-amount__fraction" aria-hidden="true">7,499</span></span></div><span style="color:#00a650" class="poly-price__installments"><span style="color:#000000e6" class="poly-phrase-label">en</span> 15 meses sin intereses de <span class="andes-money-amount poly-phrase-price andes-money-amount--cents-dot" style="font-size:inherit" role="img" aria-label="499 pesos mexicanos con 93 centavos" aria-roledescription="Monto"><span class="andes-money-amount__currency-symbol" aria-hidden="true">$</span><span class="andes-money-amount__fraction" aria-hidden="true">499</span><span aria-hidden="true">.</span><span class="andes-money-amount__cents" aria-hidden="true">93</span></span></span></div><div class="poly-component__shipping"><span class="poly-shipping--next_day_sunday">Llega gratis mañana domingo</span></div><span class="poly-component__shipped-from">Enviado por <svg aria-label="FULL" width="41" height="13" viewBox="0 0 41 13" role="img"><use href="#poly_full"></use></svg></span><div class="poly-component__buy-box"><span class="poly-buy-box__headline">Otra opción de compra</span><a href="https://www.mercadolibre.com.mx/tarjeta-de-video-asus-dual-geforce-rtx-4060-v2-oc-8gb-gdrr6/p/MLM41420314?offer_type=BEST_PRICE#wid=MLM2213182333&amp;sid=search&amp;tracking_id=ce42b891-4f47-4e5b-bd48-05b345a2b3bc" class="poly-buy-box__alternative-option poly-component__link" target="_self"><div class="poly-component__price"><s class="andes-money-amount andes-money-amount--previous andes-money-amount--cents-dot" style="font-size:12px" role="img" aria-label="Antes: 8189 pesos mexicanos" aria-roledescription="Monto"><span class="andes-money-amount__currency-symbol" aria-hidden="true">$</span><span class="andes-money-amount__fraction" aria-hidden="true">8,189</span></s><div class="poly-price__current"><span class="andes-money-amount andes-money-amount--cents-superscript" style="font-size:24px" role="img" aria-label="7129 pesos mexicanos" aria-roledescription="Monto"><span class="andes-money-amount__currency-symbol" aria-hidden="true">$</span><span class="andes-money-amount__fraction" aria-hidden="true">7,129</span></span><span class="andes-money-amount__discount" style="font-size:14px">12% OFF</span></div><span style="color:#0000008c" class="poly-price__installments">Precio más conveniente</span></div></a></div></div><div class="poly-content__column"><div class="poly-component__reviews"><span class="andes-visually-hidden">Calificación 4.9 de 5 (66 calificaciones)</span><span class="poly-reviews__rating" aria-hidden="true">4.9</span><span class="poly-reviews__starts"><svg width="15" height="15" viewBox="0 0 15 15"><use href="#poly_star_fill"></use></svg> <svg width="15" height="15" viewBox="0 0 15 15"><use href="#poly_star_fill"></use></svg> <svg width="15" height="15" viewBox="0 0 15 15"><use href="#poly_star_fill"></use></svg> <svg width="15" height="15" viewBox="0 0 15 15"><use href="#poly_star_fill"></use></svg> <svg width="15" height="15" viewBox="0 0 15 15"><use href="#poly_star_fill"></use></svg></span><span class="poly-reviews__total" aria-hidden="true">(66)</span></div></div></div></div><div class="poly-component__bookmark"><button type="button" class="poly-bookmark__btn" role="switch" aria-checked="false" aria-label="Favorito"><svg class="poly-bookmark__icon-full" width="20" height="20" viewBox="0 0 20 20"><use href="#poly_bookmark"></use></svg><svg class="poly-bookmark__icon-empty" width="20" height="20" viewBox="0 0 20 20"><use href="#poly_bookmark"></use></svg></button></div></div></div></li>
"""

# Crear un HTML completo para que BeautifulSoup pueda procesarlo correctamente
html_completo = f"""
<html>
<body>
<div class="ui-search-results">
{html_ejemplo}
</div>
</body>
</html>
"""

print("Analizando HTML de ejemplo de MercadoLibre...")

# Analizar el HTML manualmente para crear un producto
soup = BeautifulSoup(html_completo, 'html.parser')
item = soup.find('li', class_=lambda c: c and ('ui-search-layout__item' in c))

if item:
    # Extraer datos manualmente
    titulo_tag = item.find('a', class_='poly-component__title')
    nombre = titulo_tag.text.strip() if titulo_tag else "Nombre no disponible"
    link = titulo_tag['href'] if titulo_tag and titulo_tag.get('href') else ""
    
    # Extraer ID del producto
    producto_id = ""
    if link:
        mlm_pattern = re.search(r'\/(?:p\/|)(?:MLM|MLA|MCO|MEC)[-]?(\d+)', link)
        if mlm_pattern:
            producto_id = f"MLM{mlm_pattern.group(1)}"
        else:
            producto_id = f"ML-{link[-10:]}"
    
    # Extraer precio
    precio_tag = item.find('span', class_='andes-money-amount__fraction')
    precio = 0.0
    if precio_tag:
        precio_text = precio_tag.text.replace('.', '').replace(',', '').strip()
        try:
            precio = float(precio_text)
        except ValueError:
            precio = 0.0
    
    # Extraer imagen
    img_tag = item.find('img', class_='poly-component__picture')
    imagen = img_tag['src'] if img_tag and img_tag.get('src') else ""
    
    # Extraer vendedor
    vendedor_tag = item.find('span', class_='poly-component__seller')
    vendedor = vendedor_tag.text.strip().replace('Por ', '') if vendedor_tag else ""
    
    # Crear producto manualmente
    producto_manual = crear_producto_base(
        tienda='MercadoLibre',
        nombre=nombre,
        precio=precio,
        link=link,
        imagen=imagen,
        id_producto=producto_id,
        vendedor=vendedor
    )
    
    print("\nProducto creado manualmente:")
    for key, value in producto_manual.items():
        print(f"{key}: {value}")
    
    # Verificar si el producto sería filtrado
    modelo = detectar_modelo(nombre)
    print(f"\nModelo detectado: {modelo}")
    
    if modelo == "Otro":
        print("El producto sería filtrado porque no se detectó un modelo RTX válido.")
    elif precio <= 0:
        print("El producto sería filtrado porque el precio es 0 o negativo.")
    else:
        # Verificar si sería filtrado por filtrar_productos_irrelevantes
        productos_filtrados = filtrar_productos_irrelevantes([producto_manual])
        if not productos_filtrados:
            print("El producto sería filtrado por filtrar_productos_irrelevantes.")
        else:
            print("El producto pasaría todos los filtros.")

# Intentar extraer productos con el scraper
print("\nProbando el scraper completo:")
productos = scrape_mercadolibre_page(html_completo)
print(f'Productos encontrados: {len(productos)}')

# Si hay productos, mostrar el primero
if productos:
    print("\nProducto encontrado por el scraper:")
    for key, value in productos[0].items():
        print(f"{key}: {value}")
else:
    print("\nEl scraper no encontró productos.") 