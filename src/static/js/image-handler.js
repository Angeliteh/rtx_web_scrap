/**
 * Maneja las imágenes de MercadoLibre, intentando diferentes variaciones de URL
 * si la imagen original falla en cargar.
 */
class MercadoLibreImageHandler {
    constructor() {
        this.fallbackImage = '/static/img/no-image.png';
        this.transformations = [
            // Transformación 1: Calidad alta
            (url) => url.replace('D_Q_NP', 'D_NQ_NP'),
            
            // Transformación 2: Imagen completa
            (url) => url.replace('-V.webp', '-F.webp'),
            
            // Transformación 3: Sin optimización
            (url) => url.replace('-O.webp', '-F.webp'),
            
            // Transformación 4: Cambio de formato
            (url) => url.replace('.jpg', '-F.webp'),
            
            // Transformación 5: Combinación de calidad alta y formato
            (url) => url.replace('D_Q_NP', 'D_NQ_NP').replace('-V.webp', '-F.webp'),
        ];
    }

    handleImage(img) {
        if (!img.dataset.originalSrc) {
            img.dataset.originalSrc = img.src;
            img.dataset.transformIndex = '0';
        }

        const tryNextTransformation = () => {
            const index = parseInt(img.dataset.transformIndex);
            
            if (index < this.transformations.length) {
                const newSrc = this.transformations[index](img.dataset.originalSrc);
                img.dataset.transformIndex = (index + 1).toString();
                console.log(`Intentando transformación ${index + 1}: ${newSrc}`);
                img.src = newSrc;
            } else {
                console.log('Todas las transformaciones fallaron, usando imagen por defecto');
                img.src = this.fallbackImage;
                img.onerror = null;
            }
        };

        img.onerror = tryNextTransformation;
    }
}

// Inicializar el manejador cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    const imageHandler = new MercadoLibreImageHandler();
    
    // Aplicar a todas las imágenes de productos de MercadoLibre
    document.querySelectorAll('img[data-store="mercadolibre"]').forEach(img => {
        imageHandler.handleImage(img);
    });
});