#Importamos las librerías
import random  
from datetime import datetime  


class Pedido:

    def __init__(self, cliente, productos):
        self.identificador = random.randint(1000, 9999)
        self.cliente = cliente
        self.productos = productos
        self.fecha = datetime.now()  # fecha y hora del momento en que se crea el pedido

    # Calcula el importe total: suma precio x cantidad de cada producto
    def calcular_total(self):
        total = 0
        # Cada elemento de la lista es una tupla, la separamos en producto y cantidad
        for producto, cantidad in self.productos:
            total += producto.price * cantidad
        return total
    
    def __str__(self):
        texto = f"Pedido [{self.identificador}] - {self.fecha:%d/%m/%Y %H:%M}\n"  
        texto += f"Cliente: {self.cliente.name}\n"
        # Una línea por cada producto del pedido
        for producto, cantidad in self.productos:
            texto += f"  - {producto.name} x{cantidad} = {producto.price * cantidad:.2f} €\n" 
        texto += f"Total: {self.calcular_total():.2f} €"
        return texto
