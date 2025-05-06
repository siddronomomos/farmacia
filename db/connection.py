import mysql.connector
from mysql.connector import Error
from typing import Optional
from config import Config

class Connection:
    _instance: Optional['Connection'] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        try:
            self.con = mysql.connector.connect(
                host=Config.DB_HOST,
                user=Config.DB_USER,
                password=Config.DB_PASSWORD
            )
            self.cursor = self.con.cursor(dictionary=True)

            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {Config.DB_NAME}")
            self.cursor.execute(f"USE {Config.DB_NAME}")

            self._create_tables()
        except Error as e:
            raise ConnectionError(f"Error al conectar a la base de datos: {e}")

    def _create_tables(self):
        tables = [
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                usuarioid INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(50) NOT NULL,
                user_name VARCHAR(50) NOT NULL UNIQUE,
                password VARCHAR(100) NOT NULL,
                perfil ENUM('admin', 'cajero', 'gerente') NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS clientes (
                clienteid INT AUTO_INCREMENT PRIMARY KEY,
                usuarioid INT NOT NULL,
                nombre VARCHAR(50) NOT NULL,
                telefono VARCHAR(10) NOT NULL,
                RFC VARCHAR(13) NOT NULL UNIQUE,
                FOREIGN KEY (usuarioid) REFERENCES usuarios(usuarioid)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS proveedor (
                proveedorid INT AUTO_INCREMENT PRIMARY KEY,
                nombre VARCHAR(50) NOT NULL,
                empresa VARCHAR(50),
                direccion VARCHAR(100),
                telefono VARCHAR(10)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS articulos (
                articuloid INT AUTO_INCREMENT PRIMARY KEY,
                descripcion VARCHAR(100) NOT NULL,
                precio_venta DECIMAL(10,2) NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS det_art (
                detid INT AUTO_INCREMENT PRIMARY KEY,
                proveedorid INT NOT NULL,
                articuloid INT NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                existencias INT NOT NULL,
                FOREIGN KEY (proveedorid) REFERENCES proveedor(proveedorid),
                FOREIGN KEY (articuloid) REFERENCES articulos(articuloid)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS ventas (
                folio INT AUTO_INCREMENT PRIMARY KEY,
                fecha DATE NOT NULL DEFAULT CURRENT_DATE,
                usuarioid INT NOT NULL,
                clienteid INT NOT NULL,
                FOREIGN KEY (usuarioid) REFERENCES usuarios(usuarioid),
                FOREIGN KEY (clienteid) REFERENCES clientes(clienteid)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS det_venta (
                detid INT AUTO_INCREMENT PRIMARY KEY,
                folio INT NOT NULL,
                articuloid INT NOT NULL,
                cantidad INT NOT NULL,
                FOREIGN KEY (folio) REFERENCES ventas(folio),
                FOREIGN KEY (articuloid) REFERENCES articulos(articuloid)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS compras (
                folio INT AUTO_INCREMENT PRIMARY KEY,
                fecha DATE NOT NULL DEFAULT CURRENT_DATE,
                usuarioid INT NOT NULL,
                proveedorid INT NOT NULL,
                FOREIGN KEY (proveedorid) REFERENCES proveedor(proveedorid)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS det_compra (
                detid INT AUTO_INCREMENT PRIMARY KEY,
                folio INT NOT NULL,
                articuloid INT NOT NULL,
                cantidad INT NOT NULL,
                FOREIGN KEY (folio) REFERENCES compras(folio),
                FOREIGN KEY (articuloid) REFERENCES articulos(articuloid)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS descuento_puntos (
                descuentoid INT AUTO_INCREMENT PRIMARY KEY,
                puntos_minimos INT NOT NULL,
                puntos_maximos INT NOT NULL,
                porcentaje_descuento DECIMAL(5,2) NOT NULL
            )
            """
        ]

        try:
            for table in tables:
                self.cursor.execute(table)
            self.con.commit()
        except Error as e:
            print(f"Error al crear tablas: {e}")
            self.con.rollback()

    def close(self):
        try:
            if hasattr(self, 'cursor') and self.cursor:
                self.cursor.close()
        except Exception:
            pass
        try:
            if hasattr(self, 'con') and self.con and self.con.is_connected():
                self.con.close()
        except Exception:
            pass

    def commit(self):
        self.con.commit()

    def rollback(self):
        self.con.rollback()
