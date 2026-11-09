"""
Antes de nada debemos instalar fastapi uvicorn, después debemos abrir la terminal en esta misma carpeta y ejecutamos
el siguiente comando: py -m uvicorn main:app --reload 
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse

from Services.Tienda_service import (
    TiendaService,
    NoEncontradoError,
    OperacionNoValidaError,
    StockInsuficienteError,
)
from schemas import (
    UsuarioCreate, UsuarioRead,
    ProductoCreate, ProductoRead,
    PedidoCreate, PedidoRead,
)

app = FastAPI(title="Tienda Online")

# Creamos la tienda una sola vez y la usan todos los endpoints.
tienda = TiendaService()


# Al abrir http://127.0.0.1:8000/ nos lleva directamente a la documentación
@app.get("/", include_in_schema=False)
def inicio():
    return RedirectResponse(url="/docs")



# Creamos un nuevo usuario
@app.post("/usuarios", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def nuevo_usuario(usuario: UsuarioCreate):
    try:
        nuevo = tienda.registrar_usuario(usuario.tipo, usuario.nombre, usuario.email, usuario.dir_postal)
    except OperacionNoValidaError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return UsuarioRead.desde_modelo(nuevo)


# Devuelve todos los usuarios
@app.get("/usuarios", response_model=list[UsuarioRead])
def lectura_usuarios():
    return [UsuarioRead.desde_modelo(u) for u in tienda.listar_usuarios()] # Esto de aqui actúa de forma semejante a un for, pero para crear una lista


# Busca un usuario por su id
@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead)
def leer_usuario(usuario_id: int):
    try:
        usuario = tienda.obtener_usuario(usuario_id)
    except NoEncontradoError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UsuarioRead.desde_modelo(usuario)


# Crea un producto en la tienda
@app.post("/productos", response_model=ProductoRead, status_code=status.HTTP_201_CREATED)
def create_producto(producto: ProductoCreate):
    nuevo = tienda.crear_producto(
        producto.tipo, producto.nombre, producto.precio, producto.stock,
        meses_garantia=producto.meses_garantia, talla=producto.talla, color=producto.color,
    )
    return ProductoRead.desde_modelo(nuevo)


# Obtener productos
@app.get("/productos", response_model=list[ProductoRead])
def read_productos():
    return [ProductoRead.desde_modelo(p) for p in tienda.listar_productos()]


# Gracias a la ID obtener un producto
@app.get("/productos/{producto_id}", response_model=ProductoRead)
def read_producto(producto_id: int):
    try:
        producto = tienda.obtener_producto(producto_id)
    except NoEncontradoError:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return ProductoRead.desde_modelo(producto)


# Eliminar un producto por su ID
@app.delete("/productos/{producto_id}")
def delete_producto(producto_id: int):
    try:
        tienda.eliminar_producto(producto_id)
    except NoEncontradoError:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"message": "Producto eliminado correctamente"}


# Crear un pedido
@app.post("/pedidos", response_model=PedidoRead, status_code=status.HTTP_201_CREATED)
def create_pedido(pedido: PedidoCreate):
    lineas = [(item.producto_id, item.cantidad) for item in pedido.items]
    try:
        nuevo = tienda.realizar_pedido(pedido.cliente_id, lineas)
    except NoEncontradoError as e:          # el cliente o algún producto no existe
        raise HTTPException(status_code=404, detail=str(e))
    except OperacionNoValidaError as e:     # el usuario no es un cliente
        raise HTTPException(status_code=400, detail=str(e))
    except StockInsuficienteError as e:     # no hay unidades suficientes
        raise HTTPException(status_code=409, detail=str(e))
    return PedidoRead.desde_modelo(nuevo)


# Obtener el historial de pedidos de un cliente (ordenado por fecha)
@app.get("/usuarios/{cliente_id}/pedidos", response_model=list[PedidoRead])
def read_pedidos_cliente(cliente_id: int):
    try:
        pedidos = tienda.listar_pedidos_usuario(cliente_id)
    except NoEncontradoError:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    except OperacionNoValidaError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return [PedidoRead.desde_modelo(p) for p in pedidos]
