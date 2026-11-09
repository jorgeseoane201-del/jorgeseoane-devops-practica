# Importamos las clases del modelo que usa el servicio
import random

from Models.Producto import Producto, ProductoElectronico, ProductoRopa
from Models.Usuario import Usuario, Cliente, Administrador
from Models.Pedido import Pedido


# Errores propios del servicio. En vez de hacer print y devolver None (como en la P1),
# el servicio lanza estos errores y main.py los traduce al código HTTP adecuado
class NoEncontradoError(Exception):
    """No existe el usuario o el producto pedido (HTTP 404)."""


class OperacionNoValidaError(Exception):
    """Los datos no tienen sentido para la operación, p.ej. un admin haciendo un pedido (HTTP 400)."""


class StockInsuficienteError(Exception):
    """No hay unidades suficientes de un producto (HTTP 409)."""


class TiendaService:
    """Gestiona usuarios, productos y pedidos de la tienda."""

    def __init__(self):
        self.usuarios = {}      # {identificador: usuario}
        self.productos = {}     # {identificador: producto}
        self.pedidos = []


    # Cambia el id del objeto si ya está ocupado, para que dos objetos nunca compartan id
    # (los ids se generan con random y en una API con muchos datos podrían repetirse)
    def _asegurar_id_unico(self, objeto, ocupados):
        while objeto.identificador in ocupados:
            objeto.identificador = random.randint(1000, 9999)


    # ---------- USUARIOS ----------

    # Registra un cliente o un administrador según el tipo indicado
    # dir_postal es opcional (None por defecto) porque el administrador no la necesita
    def registrar_usuario(self, tipo: str, name: str, email: str, dir_postal: str | None = None) -> Usuario:
        """Crea y guarda un usuario del tipo indicado."""
        if tipo == "cliente":
            if not dir_postal:
                raise OperacionNoValidaError("Un cliente necesita dirección postal")
            usuario = Cliente(name, email, dir_postal)
        elif tipo == "administrador":
            usuario = Administrador(name, email)
        else:
            raise OperacionNoValidaError(f"El tipo '{tipo}' no existe (cliente o administrador)")

        self._asegurar_id_unico(usuario, self.usuarios)
        self.usuarios[usuario.identificador] = usuario
        return usuario

    def obtener_usuario(self, id_usuario: int) -> Usuario:
        """Devuelve el usuario con ese id o lanza NoEncontradoError."""
        if id_usuario not in self.usuarios:
            raise NoEncontradoError(f"No existe ningún usuario con id {id_usuario}")
        return self.usuarios[id_usuario]

    def listar_usuarios(self) -> list[Usuario]:
        """Devuelve todos los usuarios registrados."""
        return list(self.usuarios.values())


    # ---------- PRODUCTOS ----------

    # Añade al inventario un producto de cualquier tipo (normal, electrónico o ropa)
    def anadir_producto(self, producto: Producto) -> Producto:
        """Guarda un producto ya creado en el inventario."""
        self._asegurar_id_unico(producto, self.productos)
        self.productos[producto.identificador] = producto
        return producto

    # Crea el objeto de la clase que toca según el tipo y lo añade al inventario
    def crear_producto(self, tipo: str, name: str, price: float, stock: int,
                       meses_garantia: int | None = None,
                       talla: str | None = None, color: str | None = None) -> Producto:
        """Crea un producto genérico, electrónico o de ropa y lo añade al inventario."""
        if tipo == "generico":
            producto = Producto(name, price, stock)
        elif tipo == "electronico":
            producto = ProductoElectronico(name, price, stock, meses_garantia)
        elif tipo == "ropa":
            producto = ProductoRopa(name, price, stock, talla, color)
        else:
            raise OperacionNoValidaError(f"El tipo de producto '{tipo}' no existe")
        return self.anadir_producto(producto)

    def obtener_producto(self, id_producto: int) -> Producto:
        """Devuelve el producto con ese id o lanza NoEncontradoError."""
        if id_producto not in self.productos:
            raise NoEncontradoError(f"No existe ningún producto con id {id_producto}")
        return self.productos[id_producto]

    # Elimina un producto a partir de su id
    def eliminar_producto(self, id_producto: int) -> None:
        """Borra un producto del inventario o lanza NoEncontradoError."""
        self.obtener_producto(id_producto)  # si no existe, lanza el error
        del self.productos[id_producto]

    # Devuelve una lista con todos los productos del inventario
    def listar_productos(self) -> list[Producto]:
        """Devuelve todos los productos del inventario."""
        return list(self.productos.values())


    # ---------- PEDIDOS ----------

    # Crea un pedido para un cliente
    # lista_pedido: lista de tuplas (id_producto, cantidad)
    def realizar_pedido(self, id_usuario: int, lista_pedido: list[tuple[int, int]]) -> Pedido:
        """Comprueba cliente, productos y stock; descuenta el stock y crea el pedido."""

        # 1. Comprobamos que el usuario existe y que es un cliente
        usuario = self.obtener_usuario(id_usuario)
        if not isinstance(usuario, Cliente):
            raise OperacionNoValidaError(f"{usuario.name} no es un cliente")

        # 2. Juntamos las cantidades si un mismo producto aparece en varias líneas
        #    (si no, pedir 2 + 2 de un producto con stock 3 pasaría la comprobación)
        cantidades = {}
        for id_producto, cantidad in lista_pedido:
            cantidades[id_producto] = cantidades.get(id_producto, 0) + cantidad

        # 3. Comprobamos que existen todos los productos y que hay stock suficiente.
        #    Aquí todavía NO se descuenta nada, solo se comprueba
        productos_pedido = []
        for id_producto, cantidad in cantidades.items():
            producto = self.obtener_producto(id_producto)
            if not producto.comprobar_stock(cantidad):
                raise StockInsuficienteError(
                    f"No hay stock suficiente de {producto.name} "
                    f"(disponible: {producto.stock}, pedido: {cantidad})"
                )
            productos_pedido.append((producto, cantidad))

        # 4. Si todo está bien, descontamos el stock (cantidad en negativo = restar)
        for producto, cantidad in productos_pedido:
            producto.actualizar_stock(-cantidad)

        # 5. Creamos el pedido, lo guardamos y lo devolvemos
        pedido = Pedido(usuario, productos_pedido)
        self.pedidos.append(pedido)
        return pedido

    # Devuelve los pedidos de un usuario ordenados por fecha (del más antiguo al más reciente)
    def listar_pedidos_usuario(self, id_usuario: int) -> list[Pedido]:
        """Devuelve los pedidos de un cliente ordenados por fecha."""
        usuario = self.obtener_usuario(id_usuario)
        if not isinstance(usuario, Cliente):
            raise OperacionNoValidaError(f"{usuario.name} no es un cliente y no tiene pedidos")
        pedidos_usuario = []
        for pedido in self.pedidos:
            if pedido.cliente.identificador == id_usuario:
                pedidos_usuario.append(pedido)
        return sorted(pedidos_usuario, key=lambda pedido: pedido.fecha)
