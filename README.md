# Tienda Online

**Autor:** Jorge Seoane García

## Descripción

API REST desarrollada en Python con FastAPI que simula una tienda online.
Permite gestionar usuarios, productos y pedidos: registrar usuarios, crear,
consultar y eliminar productos, realizar pedidos comprobando el stock y
consultar el historial de pedidos de cada cliente.

## Estructura del proyecto

```
.
├── src/
│   ├── main.py                 # Endpoints de la API (punto de entrada)
│   ├── schemas.py              # Esquemas Pydantic de entrada y salida
│   ├── Models/                 # Clases Usuario, Producto y Pedido
│   └── Services/
│       └── Tienda_service.py   # Lógica de la tienda (TiendaService)
├── requirements.txt            # Dependencias con versiones fijadas
├── dockerfile                  # Definición de la imagen Docker
└── .dockerignore               # Ficheros excluidos de la imagen
```

## Ejecución local (sin Docker)

```bash
pip install -r requirements.txt
cd src
py -m uvicorn main:app --reload
```

La API queda disponible en http://127.0.0.1:8000/docs

## Docker

### Construir la imagen

Desde la raíz del repositorio:

```bash
docker build -t tienda-online:1.0 .
```

### Ejecutar el contenedor

```bash
docker run -d --name tienda-online -p 8000:8000 tienda-online:1.0
```

Para usar otro puerto dentro del contenedor:

```bash
docker run -d --name tienda-online -p 9000:9000 -e PORT=9000 tienda-online:1.0
```

Ver los logs y parar el contenedor:

```bash
docker logs tienda-online
docker stop tienda-online
docker rm tienda-online
```

### Variables de entorno

| Variable | Valor por defecto | Descripción |
|----------|-------------------|-------------|
| `PORT`   | `8000`            | Puerto en el que escucha la API dentro del contenedor |

### Salida esperada y pruebas

Al arrancar, `docker logs tienda-online` debe mostrar algo como:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Después se puede probar la API:

- Abrir http://localhost:8000/docs para ver y probar todos los endpoints desde el navegador.
- `GET http://localhost:8000/productos` devuelve `[]` al arrancar.
- Crear un producto:

```bash
curl -X POST http://localhost:8000/productos -H "Content-Type: application/json" -d "{\"tipo\": \"electronico\", \"nombre\": \"Television\", \"precio\": 659.99, \"stock\": 10, \"meses_garantia\": 24}"
```

- Crear un cliente:

```bash
curl -X POST http://localhost:8000/usuarios -H "Content-Type: application/json" -d "{\"nombre\": \"Jorge\", \"email\": \"jorge@correo.com\", \"tipo\": \"cliente\", \"dir_postal\": \"C/ Ejemplo 1\"}"
```

- Crear un pedido con los `id` devueltos en las peticiones anteriores:

```bash
curl -X POST http://localhost:8000/pedidos -H "Content-Type: application/json" -d "{\"cliente_id\": ID_CLIENTE, \"items\": [{\"producto_id\": ID_PRODUCTO, \"cantidad\": 2}]}"
```

### Descargar la imagen desde Docker Hub

La imagen está publicada en Docker Hub:

```bash
docker pull jorgeseogar/tienda-online:1.0
docker run -d --name tienda-online -p 8000:8000 jorgeseogar/tienda-online:1.0
```

### Publicar una nueva versión

```bash
docker login
docker tag tienda-online:1.0 jorgeseogar/tienda-online:1.0
docker push jorgeseogar/tienda-online:1.0
```
