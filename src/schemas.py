"""Esquemas Pydantic de la API: lo que recibe (Create) y lo que devuelve (Read)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

from Models.Usuario import Usuario, Cliente
from Models.Producto import Producto, ProductoElectronico, ProductoRopa
from Models.Pedido import Pedido


# ---------- USUARIOS ----------

# Esquema para crear un usuario
class UsuarioCreate(BaseModel):
    nombre: str = Field(min_length=1, examples=["Jorge Seoane"])
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$", examples=["jorge@correo.com"])
    tipo: Literal["cliente", "administrador"]
    dir_postal: str | None = Field(default=None, examples=["C/ Luciano Yordi de Carricarte"])

    # Un cliente tiene que tener dirección postal; un administrador no la necesita
    @model_validator(mode="after")
    def comprobar_direccion(self):
        if self.tipo == "cliente" and not self.dir_postal:
            raise ValueError("Un cliente necesita dir_postal")
        return self


# Esquema para devolver un usuario
class UsuarioRead(BaseModel):
    id: int
    nombre: str
    email: str
    es_admin: bool
    dir_postal: str | None = None

    # Convierte un objeto Usuario de la P1 en este esquema
    @classmethod
    def desde_modelo(cls, usuario: Usuario) -> "UsuarioRead":
        return cls(
            id=usuario.identificador,
            nombre=usuario.name,
            email=usuario.email,
            es_admin=usuario.is_admin(),
            dir_postal=usuario.dir_postal if isinstance(usuario, Cliente) else None,
        )


# ---------- PRODUCTOS ----------

TipoProducto = Literal["generico", "electronico", "ropa"]


# Esquema para crear un producto
class ProductoCreate(BaseModel):
    tipo: TipoProducto
    nombre: str = Field(min_length=1, examples=["Televisión"])
    precio: float = Field(gt=0, examples=[659.99])
    stock: int = Field(ge=0, examples=[10])
    meses_garantia: int | None = Field(default=None, gt=0, examples=[24])
    talla: str | None = Field(default=None, examples=["M"])
    color: str | None = Field(default=None, examples=["Azul"])

    # Cada tipo de producto necesita sus atributos propios
    @model_validator(mode="after")
    def comprobar_atributos_del_tipo(self):
        if self.tipo == "electronico" and self.meses_garantia is None:
            raise ValueError("Un producto electrónico necesita meses_garantia")
        if self.tipo == "ropa" and (not self.talla or not self.color):
            raise ValueError("Un producto de ropa necesita talla y color")
        return self


# Esquema para devolver un producto (los atributos extra solo se rellenan según el tipo)
class ProductoRead(BaseModel):
    id: int
    tipo: TipoProducto
    nombre: str
    precio: float
    stock: int
    meses_garantia: int | None = None
    talla: str | None = None
    color: str | None = None

    # Convierte un objeto Producto de la P1 en este esquema
    @classmethod
    def desde_modelo(cls, producto: Producto) -> "ProductoRead":
        datos = {
            "id": producto.identificador,
            "nombre": producto.name,
            "precio": producto.price,
            "stock": producto.stock,
        }
        if isinstance(producto, ProductoElectronico):
            return cls(tipo="electronico", meses_garantia=producto.meses_garantia, **datos)
        if isinstance(producto, ProductoRopa):
            return cls(tipo="ropa", talla=producto.talla, color=producto.color, **datos)
        return cls(tipo="generico", **datos)


# ---------- PEDIDOS ----------

# Una línea del pedido al crearlo: qué producto y cuántas unidades
class PedidoItemCreate(BaseModel):
    producto_id: int
    cantidad: int = Field(gt=0, examples=[2])


# Esquema para crear un pedido
class PedidoCreate(BaseModel):
    cliente_id: int
    items: list[PedidoItemCreate] = Field(min_length=1)


# Una línea del pedido al devolverlo
class PedidoItemRead(BaseModel):
    producto_id: int
    nombre: str
    precio_unitario: float
    cantidad: int
    subtotal: float


# Esquema para devolver un pedido completo
class PedidoRead(BaseModel):
    id: int
    fecha: datetime
    cliente_id: int
    cliente_nombre: str
    total: float
    items: list[PedidoItemRead]

    # Convierte un objeto Pedido de la P1 en este esquema
    @classmethod
    def desde_modelo(cls, pedido: Pedido) -> "PedidoRead":
        items = [
            PedidoItemRead(
                producto_id=producto.identificador,
                nombre=producto.name,
                precio_unitario=producto.price,
                cantidad=cantidad,
                subtotal=round(producto.price * cantidad, 2),
            )
            for producto, cantidad in pedido.productos
        ]
        return cls(
            id=pedido.identificador,
            fecha=pedido.fecha,
            cliente_id=pedido.cliente.identificador,
            cliente_nombre=pedido.cliente.name,
            total=round(pedido.calcular_total(), 2),
            items=items,
        )
