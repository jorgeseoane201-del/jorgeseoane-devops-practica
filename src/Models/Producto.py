# Importamos la librería
import random  

# Definimos la clase producto, que va a ser la clase padre del resto de productos
class Producto:

    def __init__(self,name,price,stock):

        self.name = name
        self.price = price
        self.stock = stock  # unidades disponibles
    
        self.identificador = random.randint(1000, 9999)


    # Comprueba si hay stock suficiente para la cantidad pedida
    # La cantidad tiene que ser mayor que 0 y no superar el stock disponible
    def comprobar_stock (self,cantidad):

        if cantidad <= self.stock and cantidad > 0:
            return True
        else:
            return False

    # Suma unidades al stock o las resta , sin dejar nunca el stock en negativo
    def actualizar_stock (self,unidades):

        # Primero comprobamos cómo quedaría el stock, sin modificarlo todavía
        if (self.stock + unidades) >= 0 :
             self.stock += unidades  # si queda en 0 o más, actualizamos
             return True

        else:
            print ("Error no hay esa cantidad de stock")
            return False

    # Texto que se muestra al hacer print() de un producto
    def __str__(self):
        return f"{self.name} - {self.price} en stock hay {self.stock}"


# Producto electrónico: hereda de Producto y añade los meses de garantía
class ProductoElectronico(Producto):

    def __init__(self, name, price, stock, meses_garantia):
        # super() llama al constructor de Producto para guardar nombre, precio, stock e id
        super().__init__(name, price, stock)
        self.meses_garantia = meses_garantia 

    def __str__(self):
        return f"{super().__str__()} | Garantía: {self.meses_garantia} meses"


# Producto de ropa: hereda de Producto y añade talla y color
class ProductoRopa(Producto):

    def __init__(self, name, price, stock, talla, color):
       
        super().__init__(name, price, stock)
        self.talla = talla  
        self.color = color

    def __str__(self):
        return f"{super().__str__()} | Talla: {self.talla}, Color: {self.color}"
