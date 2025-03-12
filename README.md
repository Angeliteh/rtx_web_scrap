# Monitor de Precios de GPUs NVIDIA RTX

Una aplicación web que monitorea y compara precios de tarjetas gráficas NVIDIA RTX en diferentes tiendas en línea.

## Características

- 🔍 Monitoreo de precios en tiempo real
- 📊 Estadísticas detalladas de precios
- 🌓 Modo oscuro/claro
- 📱 Diseño responsivo
- 🔎 Filtros por tienda y modelo
- 📈 Historial de precios
- ⚡ Actualización automática de precios

## Tecnologías Utilizadas

- Python 3.x
- Flask
- SQLite/PostgreSQL/MongoDB
- HTML5
- CSS3
- JavaScript
- Chart.js

## Instalación

1. Clona el repositorio:
```bash
git clone https://github.com/tu-usuario/rtx_web_scrap.git
cd rtx_web_scrap
```

2. Crea un entorno virtual e instala las dependencias:
```bash
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate
pip install -r requirements.txt
```

3. Configura la base de datos:
```bash
python setup.py
```

4. Inicia la aplicación:
```bash
python -m flask run
```

La aplicación estará disponible en `http://localhost:5000`

## Configuración

Puedes personalizar la aplicación editando el archivo `src/config/config.py`:

- Tipo de base de datos (SQLite, PostgreSQL, MongoDB)
- Sitios de scraping habilitados
- Modelos de tarjetas a buscar
- Intervalos de actualización
- Configuración de alertas

## Uso

1. La página principal muestra todas las tarjetas gráficas disponibles
2. Utiliza los filtros para buscar por:
   - Tienda (Amazon, MercadoLibre)
   - Modelo (RTX 4060, 4070, 4080, 4090)
3. Ordena los resultados por:
   - Precio
   - Nombre
   - Fecha
4. Consulta el historial de precios de cada producto
5. Activa el modo oscuro según tus preferencias

## Contribuir

1. Haz un Fork del proyecto
2. Crea una rama para tu función: `git checkout -b nueva-funcion`
3. Realiza tus cambios y haz commit: `git commit -m 'Agrega nueva función'`
4. Haz push a la rama: `git push origin nueva-funcion`
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## Contacto

Tu Nombre - [@tu_twitter](https://twitter.com/tu_twitter)

Link del proyecto: [https://github.com/tu-usuario/rtx_web_scrap](https://github.com/tu-usuario/rtx_web_scrap) 