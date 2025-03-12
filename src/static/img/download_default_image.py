import os
import urllib.request
import sys

def download_default_image():
    """
    Descarga una imagen por defecto para usar cuando no se puede cargar una imagen de producto.
    """
    # Ruta donde se guardará la imagen
    img_dir = os.path.dirname(os.path.abspath(__file__))
    img_path = os.path.join(img_dir, 'no-image.png')
    
    # Verificar si la imagen ya existe
    if os.path.exists(img_path):
        print(f"La imagen ya existe en {img_path}")
        return
    
    # URL de una imagen de "no disponible" genérica
    url = "https://www.publicdomainpictures.net/pictures/280000/velka/not-found-image-15383864787lu.jpg"
    
    try:
        print(f"Descargando imagen por defecto desde {url}...")
        urllib.request.urlretrieve(url, img_path)
        print(f"Imagen descargada correctamente en {img_path}")
    except Exception as e:
        print(f"Error al descargar la imagen: {e}")
        
        # Intentar con otra URL si la primera falla
        backup_url = "https://static.vecteezy.com/system/resources/thumbnails/004/141/669/small/no-photo-or-blank-image-icon-loading-images-or-missing-image-mark-image-not-available-or-image-coming-soon-sign-simple-nature-silhouette-in-frame-isolated-illustration-vector.jpg"
        try:
            print(f"Intentando con URL alternativa: {backup_url}...")
            urllib.request.urlretrieve(backup_url, img_path)
            print(f"Imagen descargada correctamente en {img_path}")
        except Exception as e:
            print(f"Error al descargar la imagen de respaldo: {e}")
            sys.exit(1)

if __name__ == "__main__":
    download_default_image() 