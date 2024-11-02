import sys
import os
import smtplib
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QComboBox, QLineEdit, QWidget
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QFont
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import sqlite3
from dotenv import load_dotenv

# Cargar variables de entorno para el correo
load_dotenv()
remit = os.getenv('CORREO')
serv = os.getenv('SERV')
puerto = int(os.getenv('PUERTO'))
contra = os.getenv('CONTRA')

# Conectar a la base de datos SQLite
conn = sqlite3.connect('Candyvoyage.db')
cursor = conn.cursor()

class FacturacionApp(QMainWindow):
    def __init__(self):
        super(FacturacionApp, self).__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setObjectName("CandyVoyage")
        self.resize(466, 700)
        self.setStyleSheet("background-color: rgb(237, 159, 172);")
        self.centralwidget = QWidget(self)
        
        # Label para el nombre de la Tienda
        self.lblEmpresa = QLabel("CandyVoyage", self.centralwidget)
        self.lblEmpresa.setGeometry(QRect(0, 0, 471, 81))
        font = QFont()
        font.setFamily("Yu Gothic UI Semibold")
        font.setPointSize(16)
        self.lblEmpresa.setFont(font)
        self.lblEmpresa.setStyleSheet("background-color: rgb(245, 213, 231); font: 63 16pt 'Yu Gothic UI Semibold';")
        self.lblEmpresa.setAlignment(Qt.AlignCenter)

        # ComboBox para seleccionar el producto
        self.cmbProducto = QComboBox(self.centralwidget)
        self.cmbProducto.setGeometry(QRect(180, 111, 151, 31))
        self.cmbProducto.setStyleSheet("background-color: rgb(237, 159, 172); font: 14pt 'MS Shell Dlg 2';")
        self.cmbProducto.addItems(["Dulce cafe $1.00", "chocolate kiss $1.50", "Marsmello $0.75"])

        # Label y campo para cantidad
        self.txtCantidad = QLineEdit(self.centralwidget)
        self.txtCantidad.setGeometry(QRect(200, 140, 50, 31))
        self.txtCantidad.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.txtCantidad.setPlaceholderText("Cantidad")

        # Label para el total
        self.lblTotal = QLabel("Cuenta: $0.00", self.centralwidget)
        self.lblTotal.setGeometry(QRect(200, 310, 231, 31))
        self.lblTotal.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lblTotal.setAlignment(Qt.AlignCenter)

        # Campo para cantidad pagada por el cliente
        self.txtPagoCliente = QLineEdit(self.centralwidget)
        self.txtPagoCliente.setGeometry(QRect(200, 390, 231, 31))
        self.txtPagoCliente.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.txtPagoCliente.setPlaceholderText("Dinero recibido del cliente")

        # Label para el cambio
        self.lblCambio = QLabel("Cambio: $0.00", self.centralwidget)
        self.lblCambio.setGeometry(QRect(200, 430, 231, 31))
        self.lblCambio.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.lblCambio.setAlignment(Qt.AlignCenter)

        # Botón para calcular el total y el cambio
        self.btnCalcular = QPushButton("Calcular Total y Cambio", self.centralwidget)
        self.btnCalcular.setGeometry(QRect(110, 250, 211, 23))
        self.btnCalcular.setStyleSheet("background-color: rgb(255, 170, 0);")
        self.btnCalcular.clicked.connect(self.calcular_total)

        # Campo para dirección del cliente
        self.txtCorreoCliente = QLineEdit(self.centralwidget)
        self.txtCorreoCliente.setGeometry(QRect(200, 500, 231, 31))
        self.txtCorreoCliente.setStyleSheet("background-color: rgb(255, 170, 0);")
        self.txtCorreoCliente.setPlaceholderText("Correo del cliente")

        # Botón para enviar recibo
        self.btnEnviarRecibo = QPushButton("Enviar Recibo", self.centralwidget)
        self.btnEnviarRecibo.setGeometry(QRect(110, 550, 161, 23))
        self.btnEnviarRecibo.setStyleSheet("background-color: rgb(255, 170, 0);")
        self.btnEnviarRecibo.clicked.connect(self.enviar_recibo)

        # Configurar el widget central
        self.setCentralWidget(self.centralwidget)
        self.setWindowTitle("CandyVoyage")

    def calcular_total(self):
        """Calcula el total basado en el producto seleccionado y la cantidad, y también el cambio."""
        precios = {
            "Dulce cafe $1.00": 1.00,
            "chocolate kiss $1.50": 1.50,
            "Marsmello $0.75": 0.75,
        }

        producto = self.cmbProducto.currentText()
        precio = precios.get(producto, 0)

        # Validar que cantidad es un número entero positivo
        try:
            cantidad = int(self.txtCantidad.text())
            if cantidad <= 0:
                self.lblTotal.setText("Cantidad debe ser mayor a 0")
                return
        except ValueError:
            self.lblTotal.setText("Cantidad inválida")
            return

        total = precio * cantidad
        self.lblTotal.setText(f"Cuenta: ${total:.2f}")

        # Calcular el cambio con validación de pago válido
        try:
            pago_cliente = float(self.txtPagoCliente.text())
            cambio = pago_cliente - total
            if cambio < 0:
                self.lblCambio.setText("Cambio: Pago insuficiente")
            else:
                self.lblCambio.setText(f"Cambio: ${cambio:.2f}")
        except ValueError:
            self.lblCambio.setText("Cambio: Ingrese un pago válido")

    def enviar_recibo(self):
        """Envía el recibo por correo electrónico al cliente, incluyendo el total y el cambio."""
        correo_cliente = self.txtCorreoCliente.text()
        if not correo_cliente:
            print("Por favor ingrese un correo válido.")
            return

        total = self.lblTotal.text().split(": $")[-1]
        cambio = self.lblCambio.text().split(": $")[-1]

        mensaje = MIMEMultipart()
        mensaje['From'] = remit
        mensaje['To'] = correo_cliente
        mensaje['Subject'] = "Recibo de compra - CandyVoyage"
        
        cuerpo = f"Gracias por su compra.\nTotal de la cuenta: ${total}\nCambio: ${cambio}\n¡MUCHAS GRACIAS POR TU COMPRA!"
        mensaje.attach(MIMEText(cuerpo, 'plain'))

        try:
            if puerto == 465:  # Si el puerto es 465, usa SSL
                with smtplib.SMTP_SSL(serv, puerto) as server:
                    server.login(remit, contra)
                    server.sendmail(remit, correo_cliente, mensaje.as_string())
            else:  # Si el puerto es diferente, usa TLS
                with smtplib.SMTP(serv, puerto) as server:
                    server.starttls()
                    server.login(remit, contra)
                    server.sendmail(remit, correo_cliente, mensaje.as_string())

            print("Recibo enviado correctamente.")
        except smtplib.SMTPAuthenticationError:
            print("Error de autenticación. Verifique el usuario y la contraseña.")
        except smtplib.SMTPConnectError:
            print("No se pudo conectar al servidor de correo. Verifique el servidor y el puerto.")
        except smtplib.SMTPException as e:
            print(f"Error al enviar el recibo: {e}")

    def closeEvent(self, event):
        """Cierra la conexión a la base de datos al cerrar la aplicación."""
        conn.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = FacturacionApp()
    ventana.show()
    sys.exit(app.exec_())