# -*- coding: utf-8 -*-

from PyQt5 import QtWidgets, uic
# from interface_ui import Ui_CleanMediaInterface
# from interface_ui import *
import sys
import os
from os import remove
from time import sleep
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import (QAbstractItemView, QApplication, QDialog,
                             QFileDialog, QGridLayout, QHBoxLayout,
                             QHeaderView, QLabel,
                             QProgressDialog, QPushButton, QSizePolicy,
                             QMessageBox)
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow
from clear_screen import clear
from colorama import Fore, Back, Style
from colorama import init, AnsiToWin32
import threading

stream = AnsiToWin32(sys.stderr).stream
init()
init(autoreset=True)
init(wrap=False)

LimiteBarra = 0
directory = ""
fileXML = ""
archivoProcesado = ""

qtCreatorFile = "CleanMediaUI.ui"  # Nombre del archivo UI aquí.
# qtCreatorFile = "interface.ui"  # Nombre del archivo UI aquí.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)  # El modulo ui carga el archivo


class mywindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):  # Constructor de la clase

        # super(mywindow, self).__init__()
        QtWidgets.QMainWindow.__init__(self)  # Constructor
        Ui_MainWindow.__init__(self)  # Constructor
        self.setupUi(self)  # Método Constructor de la ventana

#        self.ui = Ui_CleanMediaInterface()
#
#        self.setupUi(self)

        self.pushButtonComenzar.clicked.connect(self.btnClicked)

        self.pushButtonXML.clicked.connect(self.btnClickedXML)

        self.pushButtonRom.clicked.connect(self.btnClickedRom)

        self.radio_value()
        self.radioButtonBorrar.clicked.connect(self.radio_value)
        self.radioButtonMover.clicked.connect(self.radio_value)

        self.progressBar.setValue(LimiteBarra)
        self.pushButtonInfo.clicked.connect(self.btnClickedInfo)
        #self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.show()

    def btnClickedInfo(self):
        QMessageBox.about(self, "Info",
                          """
     Limpia archivos obsoletos de los directorios "media" dentro de la
   carpeta "ROMS", usando el gamelist.txt como guía para saber si se usa
   el archivo.
     Versión beta, haz una copia de seguridad antes de usar este programa

     CleanMedia.py  ver. 2.0

     Creado por Daniel Serrano   -   dani.eus79@gmail.com

     https://danitxu79.github.io/CleanMediaRoms/

     """)

    def radio_value(self):
        if self.radioButtonMover.isChecked():
            self.labelOpcion.setText("Mover archivos al directorio Backup")
        elif self.radioButtonBorrar.isChecked():
            self.labelOpcion.setText("Borrar archivos media no utilizados")

    def btnClickedRom(self):
        global directory

        directory = str(QFileDialog.getExistingDirectory(self,
                                                         "Selecciona el directorio media"))
        if directory:
            # print("Directorio seleccionado: ", directory)
            self.labelROM.setText(directory)

    def btnClickedXML(self):
        global fileXML

        fileXML, _ = QFileDialog.getOpenFileName(self,
                                              'Selecciona el archivo .xml', os.getcwd(),
                                              "Archivos .XML (*.xml);;Todos los archivos(*.*)")
        # QDir.homePath(),
        if fileXML:
            # print("Archivo seleccionado: ", file)
            self.labelXML.setText(fileXML)

    def btnClicked(self):
        self.pushButtonComenzar.setEnabled(False)

        #Escaneo()
        iniciar=threading.Thread(name='Escaneo', target=Escaneo)

        iniciar.start()

        self.pushButtonComenzar.setEnabled(True)


def Escaneo():

        global LimiteBarra
        ruta_app = os.getcwd()
        total = 0
        num_archivos = 0
        linea = '-' * 120
        todos_directorios = []
        todos_archivos = []
        ruta_xml = fileXML  # ruta_app + '\\roms\\gamelist.xml'
        ruta_roms = ruta_app + '\\roms'

        clear()
        print(Back.BLUE + Fore.WHITE + Style.BRIGHT + f"""\n


            Limpia archivos obsoletos de los directorios "media" dentro de la
         carpeta "ROMS", usando el gamelist.txt como guía para saber si se usa
           el archivo.

          Versión beta, haz una copia de seguridad antes de usar este programa

               CleanMedia.py  ver. 2.0

            Creado por Daniel Serrano   -   dani.eus79@gmail.com

        """)

        # sleep(5)

        for ruta, directorios, archivos in os.walk(directory, topdown=True):
            print(Back.BLUE + Style.BRIGHT + '\nRuta       :',
                  Back.BLUE + Style.BRIGHT + ruta)
            print('\n')
            print(Back.BLUE + Style.BRIGHT + '\nArchivo xml       :',
                  Back.BLUE + Style.BRIGHT + fileXML)
            print('\n')

            sleep(2)
            for elemento in archivos:
                num_archivos += 1
                archivo = ruta + os.sep + elemento
                estado = os.stat(archivo)
                tamaño = estado.st_size
                total += tamaño
                print(linea)
                print(Fore.YELLOW + 'archivo      :',
                      Fore.LIGHTYELLOW_EX + elemento)
                print(Fore.YELLOW + 'tamaño (Kb)  :', round(tamaño/1024, 1))
                if elemento.endswith(('png', 'PNG', 'mp4',
                                      'MP4', 'jpg', 'JPG')):
                    print(Fore.MAGENTA + 'Ruta         :',
                          Fore.LIGHTMAGENTA_EX + ruta)
                    print(Back.BLACK + Fore.GREEN + Style.BRIGHT +
                          "ENCONTRADO ARCHIVO MULTIMEDIA")
                    todos_directorios.append(ruta)
                    todos_archivos.append(elemento)
                    LimiteBarra = num_archivos
        print(LimiteBarra)

        print(linea)
        print(Back.BLACK + Fore.BLUE + Style.BRIGHT +
              'Núm. archivos:', num_archivos)
        print(Back.BLACK + Fore.YELLOW + Style.BRIGHT +
              'Total (kb)   :', round(total/1024, 1))
        peso_kb = round(total/1024)
        peso_Mb = peso_kb / 1000
        print(Back.BLACK + Fore.YELLOW + Style.BRIGHT +
              'Total (Mb)   :', peso_Mb)

        print(linea)
        diccionario = dict((('directorios', todos_directorios),
                            ('archivos', todos_archivos)))
        print("\n")
        print(linea)
        print("\n")
        numero_archivos = len(todos_archivos)
        print(Back.BLACK + Fore.GREEN + Style.BRIGHT +
              "Total archivos multimedia escaneados: ", numero_archivos)
        if num_archivos == 0:
            sys.exit()
        print("\n")
        print(linea)
        print("\n")
        sleep(5)
        clear()

        diccionario_archivos = diccionario.values()
        diccionario_directorios = diccionario.keys()
        print(linea)
        numero = 0
        archivo_objetivo = diccionario['archivos'][0]
        directorio_objetivo = diccionario['directorios'][0]
        total = directorio_objetivo + '\\' + archivo_objetivo
        total_archivos_borrados = 0
        pesototal = 0

        LimiteBarra = 50
        for file in todos_archivos:
            correcto = 0
            with open(ruta_xml, "r", encoding="utf8") as fichero_xml:
                for line in fichero_xml:
                    archivo_objetivo = diccionario['archivos'][numero]
                    if file in line:
                        # clear()
                        print(linea)
                        print()
                        print(Back.BLACK + Fore.YELLOW + Style.BRIGHT +
                              "Archivo correcto:")
                        directorio_objetivo = diccionario['directorios'][numero]
                        archivo_objetivo = diccionario['archivos'][numero]
                        total = directorio_objetivo + '\\' + archivo_objetivo
                        print(Back.BLACK + Fore.RED + Style.BRIGHT + "     ",
                              total)
                        # print(numero)
                        if numero < num_archivos:
                            numero = numero + 1
                        correcto = 1
                        # print(file)
                        print()
                        break

            if correcto == 0:
                directorio_objetivo = diccionario['directorios'][numero]
                archivo_objetivo = diccionario['archivos'][numero]
                total = directorio_objetivo + '\\' + archivo_objetivo
                # clear()
                print(linea)
                print()
                print(Back.BLACK + Fore.YELLOW + Style.BRIGHT +
                      "Archivo obsoleto:")
                print(Back.BLACK + Fore.BLUE + Style.BRIGHT + "El archivo ",
                      Back.BLACK + Fore.WHITE + Style.BRIGHT + total +
                      Back.BLACK + Fore.RED + Style.BRIGHT +
                      " va a ser eliminado")
                if numero < num_archivos:
                    numero = numero + 1
                print()
                archivo = total
                estado = os.stat(archivo)
                tamaño = estado.st_size
                pesototal += tamaño
                total_archivos_borrados += 1
                # remove(total)

        fichero_xml.close()

        clear()
        print()
        print(linea)
        print()
        print(Back.BLACK + Fore.YELLOW + Style.BRIGHT +
              "Total archivos obsoletos borrados: ", total_archivos_borrados)
        print(Back.BLACK + Fore.GREEN + Style.BRIGHT +
              'Total (kb)   :', round(pesototal/1024, 1))
        peso_kb = round(pesototal/1024)
        peso_Mb = peso_kb / 1000
        print(Back.BLACK + Fore.RED + Style.BRIGHT + 'Total (Mb)   :', peso_Mb)




if __name__ == "__main__":
    app =  QtWidgets.QApplication(sys.argv)
    window = mywindow()
    window.show()
    sys.exit(app.exec_())


#app = QtWidgets.QApplication([])
#
#application = mywindow()
#
#application.show()
#
#sys.exit(app.exec_())
