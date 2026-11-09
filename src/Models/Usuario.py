import random  # para generar el identificador de cada usuario


# Clase padre de todos los usuarios de la tienda
class Usuario:

    # Constructor: guarda nombre y email, y genera el identificador automáticamente
    def __init__(self, name, email):
        self.name = name
        self.email = email
        self.identificador = random.randint(1000, 9999)

   
    def is_admin(self):
        return False

   
    def __str__(self):
        return f"[{self.identificador}],{self.name} y su email es: {self.email}"


# Cliente: hereda de Usuario y añade la dirección postal
class Cliente(Usuario):

    def __init__(self,name,email, dir_postal):
       
        super().__init__(name, email)
        self.dir_postal = dir_postal  



class Administrador(Usuario):

    def is_admin(self):
        return True
