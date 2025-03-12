import re
import os
import requests
from bs4 import BeautifulSoup
import time
import webbrowser
from urllib.parse import urlparse, parse_qs

# Ejemplo de HTML que no muestra la imagen correctamente (productosinimagen.txt)
html_sin_imagen = """
<li class="ui-search-layout__item shops__layout-item"><div class="ui-search-result__wrapper"><div class="poly-card poly-card--list"><div class="poly-card__portada"><img width="150" height="150" decoding="async" src="https://http2.mlstatic.com/D_Q_NP_2X_997944-MLM82618465249_022025-V.webp" class="poly-component__picture" alt=""></div><div class="poly-card__content"><span class="poly-component__brand">ASUS</span><h3 class="poly-component__title-wrapper"><a href="https://articulo.mercadolibre.com.mx/MLM-2242582947-tarjeta-de-video-nvidia-geforce-rtx-4060-asus-dual-oc-8gb-_JM#polycard_client=search-nordic&amp;position=27&amp;search_layout=stack&amp;type=item&amp;tracking_id=9bd0cc79-fa06-4951-83d2-68fa6556c143" target="_self" class="poly-component__title">Tarjeta De Video Nvidia Geforce Rtx 4060 Asus Dual Oc, 8gb</a></h3><span class="poly-component__seller">Por PCEL <svg aria-label="Tienda oficial" width="12" height="12" viewBox="0 0 12 12" role="img"><use href="#poly_cockade"></use></svg></span><div class="poly-component__price"><div class="poly-price__current"><span class="andes-money-amount andes-money-amount--cents-superscript" style="font-size:24px" role="img" aria-label="7399 pesos mexicanos" aria-roledescription="Monto"><span class="andes-money-amount__currency-symbol" aria-hidden="true">$</span><span class="andes-money-amount__fraction" aria-hidden="true">7,399</span></span></div><span style="color:#000000e6" class="poly-price__installments"><span class="poly-phrase-label">en</span> 24 meses de <span class="andes-money-amount poly-phrase-price andes-money-amount--cents-dot" style="font-size:inherit" role="img" aria-label="447 pesos mexicanos con 12 centavos" aria-roledescription="Monto"><span class="andes-money-amount__currency-symbol" aria-hidden="true">$</span><span class="andes-money-amount__fraction" aria-hidden="true">447</span><span aria-hidden="true">.</span><span class="andes-money-amount__cents" aria-hidden="true">12</span></span></span></div><div class="poly-component__shipping">Envío gratis</div></div><div class="poly-component__bookmark"><button type="button" class="poly-bookmark__btn" role="switch" aria-checked="false" aria-label="Favorito"><svg class="poly-bookmark__icon-full" width="20" height="20" viewBox="0 0 20 20"><use href="#poly_bookmark"></use></svg><svg class="poly-bookmark__icon-empty" width="20" height="20" viewBox="0 0 20 20"><use href="#poly_bookmark"></use></svg></button></div></div></div></li>
"""

# Ejemplo de HTML que sí muestra la imagen correctamente (html_producto_mercado.txt)
html_con_imagen = """
<li class="ui-search-layout__item shops__layout-item"><div class="ui-search-result__wrapper"><div class="poly-card poly-card--list"><div class="poly-card__portada"><img width="150" height="150" decoding="async" src="https://http2.mlstatic.com/D_Q_NP_2X_644537-MLU73129803450_122023-V.webp" class="poly-component__picture" alt=""></div><div class="poly-card__content"><span class="poly-component__brand">MSI</span><h3 class="poly-component__title-wrapper"><a href="https://www.mercadolibre.com.mx/tarjeta-de-video-nvidia-msi-geforce-rtx-4060-ti-ventus-2x-black-8g-oc-912-v512-007/p/MLM23798521#polycard_client=search-nordic&amp;searchVariation=MLM23798521&amp;wid=MLM3579582256&amp;position=3&amp;search_layout=stack&amp;type=product&amp;tracking_id=9bd0cc79-fa06-4951-83d2-68fa6556c143&amp;sid=search" target="_self" class="poly-component__title">Tarjeta de video Nvidia MSI GeForce RTX™ 4060 Ti VENTUS 2X BLACK 8G OC 912-V512-007</a></h3><div class="poly-content"><div class="poly-content__column"><div class="poly-component__price"><div class="poly-price__current"><span class="andes-money-amount andes-money-amount--cents-superscript" style="font-size:24px" role="img" aria-label="9650 pesos mexicanos" aria-roledescription="Monto"><span class="andes-money-amount__currency-symbol" aria-hidden="true">$</span><span class="andes-money-amount__fraction" aria-hidden="true">9,650</span></span></div><span style="color:#000000e6" class="poly-price__installments"><span class="poly-phrase-label">en</span> 24 meses de <span class="andes-money-amount poly-phrase-price andes-money-amount--cents-dot" style="font-size:inherit" role="img" aria-label="583 pesos mexicanos con 14 centavos" aria-roledescription="Monto"><span class="andes-money-amount__currency-symbol" aria-hidden="true">$</span><span class="andes-money-amount__fraction" aria-hidden="true">583</span><span aria-hidden="true">.</span><span class="andes-money-amount__cents" aria-hidden="true">14</span></span></span></div><div class="poly-component__shipping">Envío gratis</div><div class="poly-component__buy-box"><span class="poly-buy-box__headline">Otra opción de compra</span><a href="https://www.mercadolibre.com.mx/tarjeta-de-video-nvidia-msi-geforce-rtx-4060-ti-ventus-2x-black-8g-oc-912-v512-007/p/MLM23798521?offer_type=BEST_INSTALLMENTS#wid=MLM3579452582&amp;sid=search&amp;tracking_id=9bd0cc79-fa06-4951-83d2-68fa6556c143" class="poly-buy-box__alternative-option poly-component__link" target="_self"><div class="poly-component__price"><div class="poly-price__current"><span class="andes-money-amount andes-money-amount--cents-superscript" style="font-size:24px" role="img" aria-label="10250 pesos mexicanos" aria-roledescription="Monto"><span class="andes-money-amount__currency-symbol" aria-hidden="true">$</span><span class="andes-money-amount__fraction" aria-hidden="true">10,250</span></span></div><span style="color:#00a650" class="poly-price__installments"><span style="color:#000000e6" class="poly-phrase-label">en</span> 15 meses sin intereses de <span class="andes-money-amount poly-phrase-price andes-money-amount--cents-dot" style="font-size:inherit" role="img" aria-label="683 pesos mexicanos con 33 centavos" aria-roledescription="Monto"><span class="andes-money-amount__currency-symbol" aria-hidden="true">$</span><span class="andes-money-amount__fraction" aria-hidden="true">683</span><span aria-hidden="true">.</span><span class="andes-money-amount__cents" aria-hidden="true">33</span></span></span></div></a></div></div><div class="poly-content__column"><div class="poly-component__reviews"><span class="andes-visually-hidden">Calificación 4.7 de 5 (77 calificaciones)</span><span class="poly-reviews__rating" aria-hidden="true">4.7</span><span class="poly-reviews__starts"><svg width="15" height="15" viewBox="0 0 15 15"><use href="#poly_star_fill"></use></svg> <svg width="15" height="15" viewBox="0 0 15 15"><use href="#poly_star_fill"></use></svg> <svg width="15" height="15" viewBox="0 0 15 15"><use href="#poly_star_fill"></use></svg> <svg width="15" height="15" viewBox="0 0 15 15"><use href="#poly_star_fill"></use></svg> <svg width="15" height="15" viewBox="0 0 15 15"><use href="#poly_star_half"></use></svg></span><span class="poly-reviews__total" aria-hidden="true">(77)</span></div></div></div></div><div class="poly-component__bookmark"><button type="button" class="poly-bookmark__btn" role="switch" aria-checked="false" aria-label="Favorito"><svg class="poly-bookmark__icon-full" width="20" height="20" viewBox="0 0 20 20"><use href="#poly_bookmark"></use></svg><svg class="poly-bookmark__icon-empty" width="20" height="20" viewBox="0 0 20 20"><use href="#poly_bookmark"></use></svg></button></div></div></div></li>
"""

def extraer_imagen_mercadolibre(html):
    """Extrae la URL de la imagen de un producto de MercadoLibre"""
    soup = BeautifulSoup(html, 'html.parser')
    img_tag = soup.find('img', class_='poly-component__picture')
    
    if not img_tag or not img_tag.get('src'):
        return None
    
    return img_tag['src']

def generar_variantes_url_imagen(url_original):
    """Genera diferentes variantes de URL para intentar obtener la imagen correcta"""
    if not url_original:
        return []
    
    # Extraer la base de la URL y el ID de la imagen
    base_url = url_original.split('/D_')[0]
    
    # Patrones para extraer el ID de la imagen
    patterns = [
        r'(\d+-[A-Z]{2,3}\d+_\d+)',  # Ej: 644537-MLU73129803450_122023
        r'(\d+-[A-Z]{2,3}\d+)',      # Ej: 940224-MLA79721049641
        r'(\d+-MLM\d+)',             # Ej: 967338-MLM82699680404
    ]
    
    image_id = None
    for pattern in patterns:
        match = re.search(pattern, url_original)
        if match:
            image_id = match.group(1)
            break
    
    if not image_id:
        print(f"No se pudo extraer el ID de la imagen: {url_original}")
        # Intentar transformaciones directas
        return [
            url_original.replace('D_Q_NP', 'D_NQ_NP').replace('-V.webp', '-F.webp'),
            url_original.replace('D_Q_NP_2X', 'D_NQ_NP').replace('-V.webp', '-F.webp'),
            url_original.replace('D_Q_NP_2X', 'D_NQ_NP_2X').replace('-V.webp', '-F.webp'),
            url_original.replace('-V.webp', '.webp'),
            url_original.replace('-V.webp', '-F.jpg'),
            url_original.replace('webp', 'jpg')
        ]
    
    # Generar variantes con el ID extraído
    variantes = [
        f"{base_url}/D_NQ_NP_2X_{image_id}-F.webp",
        f"{base_url}/D_NQ_NP_{image_id}-F.webp",
        f"{base_url}/D_NQ_NP_{image_id}-O.webp",
        f"{base_url}/D_NQ_NP_{image_id}-O.jpg",
        f"{base_url}/D_NQ_NP_{image_id}.webp",
        f"{base_url}/D_NQ_NP_{image_id}.jpg",
    ]
    
    # Si el ID contiene guiones o guiones bajos, probar con partes del ID
    if '-' in image_id:
        variantes.append(f"{base_url}/D_NQ_NP_{image_id.split('-')[0]}-F.webp")
    if '_' in image_id:
        variantes.append(f"{base_url}/D_NQ_NP_{image_id.split('_')[0]}-F.webp")
    
    return variantes

def verificar_url_imagen(url):
    """Verifica si una URL de imagen es válida"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.head(url, headers=headers, timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"Error verificando URL {url}: {e}")
        return False

def generar_html_prueba(urls_imagenes):
    """Genera un HTML de prueba con las URLs de imágenes proporcionadas"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Prueba de Imágenes MercadoLibre</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .container { display: flex; flex-wrap: wrap; }
            .imagen-test { margin: 10px; padding: 10px; border: 1px solid #ccc; width: 300px; }
            .imagen-test img { max-width: 100%; max-height: 200px; display: block; margin: 0 auto; }
            .url { font-size: 10px; word-break: break-all; margin-top: 5px; color: #666; }
            h2 { color: #333; }
            .status { font-weight: bold; margin-top: 5px; }
            .success { color: green; }
            .error { color: red; }
        </style>
    </head>
    <body>
        <h1>Prueba de Imágenes de MercadoLibre</h1>
        <div class="container">
    """
    
    for i, url_data in enumerate(urls_imagenes):
        url = url_data['url']
        status = url_data['status']
        origen = url_data['origen']
        
        status_class = "success" if status else "error"
        status_text = "FUNCIONA" if status else "NO FUNCIONA"
        
        html += f"""
        <div class="imagen-test">
            <h2>Imagen {i+1} ({origen})</h2>
            <img src="{url}" onerror="this.onerror=null; this.src='https://via.placeholder.com/300x200?text=Imagen+No+Disponible';">
            <div class="url">{url}</div>
            <div class="status {status_class}">Estado: {status_text}</div>
        </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    # Guardar el HTML en un archivo temporal
    temp_file = os.path.join(os.getcwd(), "test_imagenes_ml_v2.html")
    with open(temp_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    return temp_file

def analizar_diferencias(url1, url2):
    """Analiza las diferencias entre dos URLs de imágenes"""
    print("\n=== ANÁLISIS DE DIFERENCIAS ENTRE URLS ===")
    print(f"URL que funciona: {url1}")
    print(f"URL que no funciona: {url2}")
    
    # Analizar partes de la URL
    parsed1 = urlparse(url1)
    parsed2 = urlparse(url2)
    
    # Comparar dominios
    if parsed1.netloc != parsed2.netloc:
        print(f"Diferente dominio: {parsed1.netloc} vs {parsed2.netloc}")
    
    # Comparar rutas
    path1 = parsed1.path.split('/')
    path2 = parsed2.path.split('/')
    
    if len(path1) != len(path2):
        print(f"Diferente estructura de ruta: {len(path1)} partes vs {len(path2)} partes")
    
    for i in range(min(len(path1), len(path2))):
        if path1[i] != path2[i]:
            print(f"Diferencia en parte {i} de la ruta: '{path1[i]}' vs '{path2[i]}'")
    
    # Analizar formato de imagen
    if path1[-1].split('.')[-1] != path2[-1].split('.')[-1]:
        print(f"Diferente formato de imagen: {path1[-1].split('.')[-1]} vs {path2[-1].split('.')[-1]}")
    
    # Analizar patrones en el nombre del archivo
    file1 = path1[-1]
    file2 = path2[-1]
    
    print(f"\nNombre de archivo 1: {file1}")
    print(f"Nombre de archivo 2: {file2}")
    
    # Buscar patrones específicos de MercadoLibre
    ml_patterns = [
        ('D_Q_NP', 'Calidad baja'),
        ('D_NQ_NP', 'Calidad alta'),
        ('-V.webp', 'Vista previa'),
        ('-F.webp', 'Imagen completa'),
        ('-O.webp', 'Imagen optimizada'),
        ('2X_', 'Doble resolución')
    ]
    
    for pattern, desc in ml_patterns:
        in_file1 = pattern in file1
        in_file2 = pattern in file2
        
        if in_file1 and not in_file2:
            print(f"Patrón '{pattern}' ({desc}) presente en URL1 pero no en URL2")
        elif not in_file1 and in_file2:
            print(f"Patrón '{pattern}' ({desc}) presente en URL2 pero no en URL1")
    
    # Extraer IDs de imagen
    id_patterns = [
        r'(\d+-[A-Z]{2,3}\d+_\d+)',
        r'(\d+-[A-Z]{2,3}\d+)',
        r'(\d+-MLM\d+)',
    ]
    
    id1 = None
    id2 = None
    
    for pattern in id_patterns:
        match1 = re.search(pattern, file1)
        if match1:
            id1 = match1.group(1)
            break
    
    for pattern in id_patterns:
        match2 = re.search(pattern, file2)
        if match2:
            id2 = match2.group(1)
            break
    
    if id1 and id2:
        print(f"\nID de imagen 1: {id1}")
        print(f"ID de imagen 2: {id2}")
        
        if id1 != id2:
            print("Los IDs de imagen son diferentes")
            
            # Analizar estructura del ID
            parts1 = re.split(r'[-_]', id1)
            parts2 = re.split(r'[-_]', id2)
            
            if len(parts1) != len(parts2):
                print(f"Diferente estructura de ID: {len(parts1)} partes vs {len(parts2)} partes")
            
            for i in range(min(len(parts1), len(parts2))):
                if parts1[i] != parts2[i]:
                    print(f"Diferencia en parte {i} del ID: '{parts1[i]}' vs '{parts2[i]}'")

def probar_transformaciones_directas(url):
    """Prueba diferentes transformaciones directas en la URL de la imagen"""
    transformaciones = [
        # Transformación 1: Reemplazar D_Q_NP por D_NQ_NP y -V.webp por -F.webp
        lambda src: src.replace('D_Q_NP', 'D_NQ_NP').replace('-V.webp', '-F.webp'),
        
        # Transformación 2: Mantener D_Q_NP_2X pero cambiar -V.webp por -F.webp
        lambda src: src.replace('-V.webp', '-F.webp'),
        
        # Transformación 3: Reemplazar D_Q_NP_2X por D_NQ_NP_2X y -V.webp por -F.webp
        lambda src: src.replace('D_Q_NP_2X', 'D_NQ_NP_2X').replace('-V.webp', '-F.webp'),
        
        # Transformación 4: Reemplazar D_Q_NP_2X por D_NQ_NP y -V.webp por -F.webp
        lambda src: src.replace('D_Q_NP_2X', 'D_NQ_NP').replace('-V.webp', '-F.webp'),
        
        # Transformación 5: Cambiar formato a jpg
        lambda src: src.replace('.webp', '.jpg'),
        
        # Transformación 6: Cambiar -V.webp por -O.webp
        lambda src: src.replace('-V.webp', '-O.webp'),
        
        # Transformación 7: Cambiar -V.webp por -O.jpg
        lambda src: src.replace('-V.webp', '-O.jpg'),
    ]
    
    resultados = []
    
    print("\n=== PROBANDO TRANSFORMACIONES DIRECTAS ===")
    print(f"URL original: {url}")
    
    for i, transformacion in enumerate(transformaciones):
        nueva_url = transformacion(url)
        funciona = verificar_url_imagen(nueva_url)
        
        print(f"Transformación {i+1}: {nueva_url} - {'FUNCIONA' if funciona else 'NO FUNCIONA'}")
        
        resultados.append({
            'url': nueva_url,
            'status': funciona,
            'origen': f'Transformación {i+1}'
        })
    
    return resultados

def main():
    # Extraer URLs originales
    url_sin_imagen = extraer_imagen_mercadolibre(html_sin_imagen)
    url_con_imagen = extraer_imagen_mercadolibre(html_con_imagen)
    
    print(f"URL original que no muestra imagen: {url_sin_imagen}")
    print(f"URL original que sí muestra imagen: {url_con_imagen}")
    
    # Analizar diferencias entre las URLs originales
    analizar_diferencias(url_con_imagen, url_sin_imagen)
    
    # Probar transformaciones directas en la URL que no funciona
    transformaciones = probar_transformaciones_directas(url_sin_imagen)
    
    # Verificar cada URL original
    urls_a_probar = [
        {'url': url_sin_imagen, 'status': verificar_url_imagen(url_sin_imagen), 'origen': 'Original (No funciona)'},
        {'url': url_con_imagen, 'status': verificar_url_imagen(url_con_imagen), 'origen': 'Original (Funciona)'}
    ]
    
    # Agregar las transformaciones a las URLs a probar
    urls_a_probar.extend(transformaciones)
    
    # Generar variantes para la URL que no funciona
    variantes_sin_imagen = generar_variantes_url_imagen(url_sin_imagen)
    
    print("\nProbando variantes para la URL que no funciona:")
    for i, variante in enumerate(variantes_sin_imagen):
        status = verificar_url_imagen(variante)
        print(f"{i+1}. {variante} - {'FUNCIONA' if status else 'NO FUNCIONA'}")
        urls_a_probar.append({'url': variante, 'status': status, 'origen': f'Variante {i+1}'})
    
    # Generar HTML de prueba
    html_file = generar_html_prueba(urls_a_probar)
    print(f"\nSe ha generado un archivo HTML de prueba: {html_file}")
    print("Abriendo en el navegador...")
    
    # Abrir el archivo HTML en el navegador
    webbrowser.open('file://' + os.path.abspath(html_file))
    
    # Generar solución recomendada
    print("\n=== SOLUCIÓN RECOMENDADA ===")
    print("Basado en el análisis, se recomienda modificar la función handleImageError en index.html:")
    
    # Encontrar la transformación que funciona (si existe)
    transformacion_funcional = next((t for t in transformaciones if t['status']), None)
    
    if transformacion_funcional:
        print(f"Se encontró una transformación que funciona: {transformacion_funcional['url']}")
        
        # Analizar qué transformación funcionó
        if 'D_NQ_NP' in transformacion_funcional['url'] and 'D_Q_NP' in url_sin_imagen:
            print("- Reemplazar 'D_Q_NP' por 'D_NQ_NP'")
        
        if '-F.webp' in transformacion_funcional['url'] and '-V.webp' in url_sin_imagen:
            print("- Reemplazar '-V.webp' por '-F.webp'")
        
        if '.jpg' in transformacion_funcional['url'] and '.webp' in url_sin_imagen:
            print("- Probar cambiar el formato de '.webp' a '.jpg'")
            
        # Generar código JavaScript para la solución
        print("\nCódigo JavaScript recomendado para handleImageError:")
        print("""
function handleImageError(img, store) {
    if (store === 'mercadolibre') {
        const originalSrc = img.src;
        console.log("Intentando recuperar imagen de MercadoLibre:", originalSrc);
        
        // Aplicar directamente la transformación que sabemos que funciona
        if (originalSrc.includes('http2.mlstatic.com')) {
            // Transformación 1: D_Q_NP -> D_NQ_NP y -V.webp -> -F.webp
            let newSrc = originalSrc.replace('D_Q_NP', 'D_NQ_NP').replace('-V.webp', '-F.webp');
            console.log("Aplicando transformación 1:", newSrc);
            img.src = newSrc;
            
            // Configurar un manejador de error para esta transformación
            img.onerror = function() {
                // Transformación 3: D_Q_NP_2X -> D_NQ_NP_2X y -V.webp -> -F.webp
                newSrc = originalSrc.replace('D_Q_NP_2X', 'D_NQ_NP_2X').replace('-V.webp', '-F.webp');
                console.log("Aplicando transformación 3:", newSrc);
                img.src = newSrc;
                
                // Configurar un manejador de error para esta transformación
                img.onerror = function() {
                    // Transformación 6: -V.webp -> -O.webp
                    newSrc = originalSrc.replace('-V.webp', '-O.webp');
                    console.log("Aplicando transformación 6:", newSrc);
                    img.src = newSrc;
                    
                    // Configurar un manejador de error para esta transformación
                    img.onerror = function() {
                        // Si todas las transformaciones fallan, usar imagen por defecto
                        setDefaultImage(img);
                    };
                };
            };
            
            return;
        }
        
        setDefaultImage(img);
    } else if (store === 'amazon') {
        // Código existente para Amazon
    } else {
        setDefaultImage(img);
    }
}
        """)
    else:
        print("No se encontró ninguna transformación directa que funcione. Se recomienda:")
        print("- Implementar un sistema de caché de imágenes en el servidor")
        print("- Mejorar el manejo de errores para mostrar una imagen por defecto")
        print("- Considerar descargar las imágenes al servidor en lugar de enlazarlas directamente")

if __name__ == "__main__":
    main() 