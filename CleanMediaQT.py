#!/usr/bin/env python
# -*- coding: utf-8 -*-
# *****************************************************************************
# *                                                                           *
# *                                                                           *
# *      Versión QT de Clean Media Roms                                       *
# *                                                                           *
# *      Limpia archivos obsoletos de los directorios "media" dentro de la    *
# *   carpeta "ROMS", usando el gamelist.txt como guía para saber si se usa   *
# *   el archivo.                                                             *
# *                                                                           *
# *       Versión beta, haz una copia de seguridad antes de usar este programa*
# *                                                                           *
# *       CleanMediaQT.py  ver. 2.0                                           *
# *                                                                           *
# *      Creado por Daniel Serrano   -   dani.eus79@gmail.com                 *
# *                                                                           *
# *****************************************************************************

from PyQt5 import QtWidgets, uic
import sys
import os
from os import remove, rename
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import (QDialog, QProgressBar, QFileDialog,
                             QLabel, QPushButton, QMessageBox)
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow
import recursos_rc
from PyQt5.QtGui import QPixmap

from clear_screen import clear
import shutil
from colorama import Fore, Back, Style
from colorama import init, AnsiToWin32
from time import sleep
from urllib.request import urlopen

stream = AnsiToWin32(sys.stderr).stream
init()
init(autoreset=True)
init(wrap=False)

LimiteBarra = 0
directory = ""
fileXML = ""
archivoProcesado = ""
total = 0
num_archivos = 0
linea = '-' * 120
todos_directorios = []
todos_archivos = []
ruta_xml = ""
diccionario = []
halistado = False
ficheroOpcion = 0
numero_archivos = 0
yaborrado = False
directorioOriginal = ""
directorioOriginal = os.getcwd()

qtCreatorFile = "CleanMediaUI.ui"  # Nombre del archivo UI aquí.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)
# El modulo ui carga el archivo


class mywindow(QtWidgets.QMainWindow, Ui_MainWindow):

    def __init__(self):  # Constructor de la clase
        # super(mywindow, self).__init__()
        QtWidgets.QMainWindow.__init__(self)  # Constructor
        Ui_MainWindow.__init__(self)  # Constructor
        self.setupUi(self)  # Método Constructor de la ventana

        self.pushButtonComenzar.clicked.connect(self.initBusqueda)
        self.pushButtonEjecutar.clicked.connect(self.initEjecutar)
        self.pushButtonXML.clicked.connect(self.btnClickedXML)

        self.pushButtonRom.clicked.connect(self.btnClickedRom)

        self.radio_value()
        self.radioButtonBorrar.clicked.connect(self.radio_value)
        self.radioButtonMover.clicked.connect(self.radio_value)

        self.pushButtonInfo.clicked.connect(self.btnClickedInfo)
        self.progressBar = self.progressBar2
        self.listWidget2 = self.listWidget
        self.labelImage2 = self.labelImage
        self.show()
        if os.path.isfile("version.act"):
            remove("version.act")
        if os.path.isfile("actualizar.py"):
            remove("actualizar.py")
        if os.path.isfile("CleanMediaQT.act"):
            remove("CleanMediaQT.act")
        self.actualizar()

    def initEjecutar(self):
        global halistado, yaborrado
        if halistado is True:
            if ficheroOpcion != 0 and yaborrado is False:
                # Deshabilitar el botón mientras se descarga el archivo.
                self.pushButtonEjecutar.setEnabled(False)
                self.pushButtonComenzar.setEnabled(False)
                # Ejecutar la descarga en un nuevo hilo.
                self.ejecutar = Ejecutar()
                # Conectar las señales que indican el progreso de la descarga
                # con los métodos correspondientes de la barra de progreso.
                self.ejecutar.setTotalProgress.connect(self.progressBar.setMaximum)
                self.ejecutar.setCurrentProgress.connect(self.progressBar.setValue)
                self.ejecutar.setListWidgetFile.connect(self.listWidget2.addItem)

                # Qt invocará el método `succeeded` cuando el archivo se haya
                # descargado correctamente y `downloadFinished()`
                # cuando el hilo
                # haya terminado.
                self.ejecutar.succeeded.connect(self.ejecutarSucceeded)
                self.ejecutar.finished.connect(self.ejecutarFinished)
                self.progressBar2.setValue(0)
                self.listWidget2.clear()
                yaborrado = True
                self.ejecutar.start()
            else:
                QMessageBox.about(self, "Info", "Primero selecciona una\
                                  opción o vuelve a listar")

    def ejecutarSucceeded(self):
        # Establecer el progreso en 100%.
        self.progressBar.setValue(self.progressBar.maximum())
        # self.labelArchivoProcesado2.setText("Terminado")

    def ejecutarFinished(self):
        # Restablecer el botón.
        self.pushButtonEjecutar.setEnabled(True)
        self.pushButtonComenzar.setEnabled(True)
        # Eliminar el hilo una vez que fue utilizado.
        del self.ejecutar

    def initBusqueda(self):
        global yaborrado
        if directory:
            yaborrado = False
            # Deshabilitar el botón mientras se descarga el archivo.
            self.pushButtonComenzar.setEnabled(False)
            self.pushButtonEjecutar.setEnabled(False)
            # Ejecutar la descarga en un nuevo hilo.
            self.busqueda = Busqueda()
            # Conectar las señales que indican el progreso de la descarga
            # con los métodos correspondientes de la barra de progreso.
            self.busqueda.setTotalProgress.connect(self.progressBar.setMaximum)
            self.busqueda.setCurrentProgress.connect(self.progressBar.setValue)
            # self.busqueda.setLabelArchivoProcesado.connect
            # (self.labelArchivoProcesado2.setText)
            self.busqueda.setListWidgetFile.connect(self.listWidget2.addItem)
            # self.busqueda.setImagen.connect(self.labelImagen2.setPixmap)
            # Qt invocará el método `succeeded` cuando el archivo se haya
            # descargado correctamente y `downloadFinished()` cuando el hilo
            # haya terminado.
            self.busqueda.succeeded.connect(self.busquedaSucceeded)
            self.busqueda.finished.connect(self.busquedaFinished)
            self.listWidget2.clear()
            self.busqueda.start()
        else:
            QMessageBox.about(self, "Info", "Primero selecciona un directorio")

    def busquedaSucceeded(self):
        global halistado
        # Establecer el progreso en 100%.
        self.progressBar.setValue(self.progressBar.maximum())
        halistado = True
        # self.labelArchivoProcesado2.setText("Terminado")

    def busquedaFinished(self):
        # Restablecer el botón.
        self.pushButtonComenzar.setEnabled(True)
        self.pushButtonEjecutar.setEnabled(True)
        # Eliminar el hilo una vez que fue utilizado.
        del self.busqueda

    def btnClickedInfo(self):
        QMessageBox.about(self, "Info",
                          """
     Limpia archivos obsoletos de los directorios "media" dentro de la
   carpeta "ROMS", usando el gamelist.txt como guía para saber si se usa
   el archivo.
     Versión beta, haz una copia de seguridad antes de usar este programa

     CleanMediaQT.py  ver. 2.0

     Creado por Daniel Serrano   -   dani.eus79@gmail.com

     https://danitxu79.github.io/CleanMediaRoms/

     """)

    def actualizar(self):
        if os.path.isfile("version.cmr"):
            r = urlopen("https://raw.githubusercontent.com/danitxu79/"
                        "CleanMediaRomsQT/master/version.cmr")
            f = open("version.act", "wb")
            f.write(r.read())
            r.close()
            f.close()
            f = open("version.act", "r")
            r = open("version.cmr", "r")
            lf = f.read()
            lr = r.read()
            r.close()
            f.close()
            if lr < lf:
                # remove("version.act")
                dialog = Dialog(self)  # self hace referencia al padre
                dialog.show()
            else:
                remove("version.act")
        else:
            r = urlopen("https://raw.githubusercontent.com/danitxu79/"
                        "CleanMediaRomsQT/master/version.cmr")
            f = open("version.act", "wb")
            f.write(r.read())
            r.close()
            f.close()
            dialog = Dialog(self)  # self hace referencia al padre
            dialog.show()

    def radio_value(self):
        global ficheroOpcion
        if self.radioButtonMover.isChecked():
            self.labelOpcion.setText("Mover archivos al directorio Backup")
            ficheroOpcion = 2
            self.pushButtonEjecutar.setText("Mover")
        elif self.radioButtonBorrar.isChecked():
            ficheroOpcion = 1
            self.labelOpcion.setText("Borrar archivos media no utilizados")
            self.pushButtonEjecutar.setText("Borrar")

    def btnClickedRom(self):
        global directory, fileXML, directorioOriginal
        tempdir = directory
        directory = str(QFileDialog.getExistingDirectory(self,
                                           "Selecciona el directorio media"))
        temp = ""
        temp = directory.replace('/', '\\')
        directory = temp
        if directory == "" and tempdir == "":
            directory = directorioOriginal
        if directory == "" and tempdir != "":
            directory = tempdir
        fileXML = directory + os.sep + 'gamelist.xml'
        os.chdir(directory)
        temp = os.path.basename(directory)
        fileImage = ""

        if temp == "roms" or temp == "rom":
            self.labelPlataforma.setText("Directorio Principal de las ROMs")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "EmulationStation.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "EmulationStation.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)       

        elif temp == "3do":
            self.labelPlataforma.setText("3do Real Multiplayer")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "3do.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "3do.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "amiga":
            self.labelPlataforma.setText("Amiga")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "amiga.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "amiga.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "amigacd32":
            self.labelPlataforma.setText("Amiga CD 32")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "amigacd32.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "amigacd32.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "amstradcpc":
            self.labelPlataforma.setText("Amstrad CPC")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "amstradcpc.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "amstradcpc.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "apple2":
            self.labelPlataforma.setText("Apple 2")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "apple2.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "apple2.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "arcade":
            self.labelPlataforma.setText("Arcade")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "arcade.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "arcade.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "atari2600":
            self.labelPlataforma.setText("Atari 2600")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "atari2600.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "atari2600.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "atari5200":
            self.labelPlataforma.setText("Atari 5200")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "atari5200.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "atari5200.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "atari7800":
            self.labelPlataforma.setText("Atari 7800")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "atari7800.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "atari7800.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "atarijaguar":
            self.labelPlataforma.setText("Atari Jaguar")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "atarijaguar.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "atarijaguar.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "atarilynx":
            self.labelPlataforma.setText("Atari Lynx")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "atarilynx.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "atarilynx.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "atarist":
            self.labelPlataforma.setText("Atari ST")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "atarist.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "atarist.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "philipscdi":
            self.labelPlataforma.setText("Philips CD-i")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "philipscdi.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "philipscdi.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "coco":
            self.labelPlataforma.setText("Tandy Colour Computer")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "coco.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "coco.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "colecovision":
            self.labelPlataforma.setText("Coleco Vision")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "colecovision.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "colecovision.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "c64":
            self.labelPlataforma.setText("Commodore 64")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "c64.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "c64.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "daphne":
            self.labelPlataforma.setText("Daphne")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "daphne.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "daphne.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "dragon32":
            self.labelPlataforma.setText("Dragon 32")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "dragon32.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "dragon32.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "dreamcast":
            self.labelPlataforma.setText("Dreamcast")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "dreamcast.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "dreamcast.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "fds":
            self.labelPlataforma.setText("Famicom Disk System")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "fds.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "fds.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "famicom":
            self.labelPlataforma.setText("Famicom")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "famicom.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "famicom.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "fba-libreto" or temp == "fba":
            self.labelPlataforma.setText("Final Burn Alpha Libreto")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "fba.png"
            self.im = QPixmap(":/Plataformas/systemlogo/fba.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "gameandwatch":
            self.labelPlataforma.setText("Game & Watch")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "gameandwatch.png"
            self.im = QPixmap(":/Plataformas/systemlogo/gameandwatch.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "gamegear":
            self.labelPlataforma.setText("GameGear")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "gamegear.png"
            self.im = QPixmap(":/Plataformas/systemlogo/gamegear.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "gb":
            self.labelPlataforma.setText("GameBoy")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "gb.png"
            self.im = QPixmap(":/Plataformas/systemlogo/gb.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "gba":
            self.labelPlataforma.setText("GameBoy Advance")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "gba.png"
            self.im = QPixmap(":/Plataformas/systemlogo/gba.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "gbc":
            self.labelPlataforma.setText("GameBoy Color")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "gbc.png"
            self.im = QPixmap(":/Plataformas/systemlogo/gbc.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "gc":
            self.labelPlataforma.setText("Game Cube")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "gc.png"
            self.im = QPixmap(":/Plataformas/systemlogo/gc.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "megadrive":
            self.labelPlataforma.setText("Megadrive")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "megadrive.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "megadrive.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "genesis":
            self.labelPlataforma.setText("Sega Genesis")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "genesis.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "genesis.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "intellivision":
            self.labelPlataforma.setText("Intellivision")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "intellivision.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "intellivision.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "lightgum":
            self.labelPlataforma.setText("Light Gum")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "lightgum.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "lightgum.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "macintosh":
            self.labelPlataforma.setText("Macintosh")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "macintosh.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "macintosh.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "mame":
            self.labelPlataforma.setText("Mame")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "mame.png"
            self.im = QPixmap(":/Plataformas/systemlogo/mame.png")
            self.labelImage2.setPixmap(self.im)

        elif temp == "mame-libreto":
            self.labelPlataforma.setText("Mame Libreto")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "mame-libreto.png"
            self.im = QPixmap(":/Plataformas/systemlogo/mame-libreto.png")
            self.labelImage2.setPixmap(self.im)

        elif temp == "mame4all":
            self.labelPlataforma.setText("Mame4all")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "mame4all.png"
            self.im = QPixmap(":/Plataformas/systemlogo/mame4all.png")
            self.labelImage2.setPixmap(self.im)

        elif temp == "mame-advmame":
            self.labelPlataforma.setText("Mame Advance")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "mame-advmame.png"
            self.im = QPixmap(":/Plataformas/systemlogo/mame-advmame.png")
            self.labelImage2.setPixmap(self.im)

        elif temp == "markiii":
            self.labelPlataforma.setText("Sega Mark III")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "markiii.png"
            self.im = QPixmap(":/Plataformas/systemlogo/markiii.png")
            self.labelImage2.setPixmap(self.im)

        elif temp == "sms":
            self.labelPlataforma.setText("Sega Master System")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "sms.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "sms.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "megacd":
            self.labelPlataforma.setText("Sega Mega CD")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "megacd.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "megacd.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)
            
        elif temp == "megadrive-japan":
            self.labelPlataforma.setText("Sega MegaDrive Japan")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "megadrive-japan.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "megadrive-japan.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "msx":
            self.labelPlataforma.setText("MSX")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "msx.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "msx.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "msx2":
            self.labelPlataforma.setText("MSX 2")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "msx2.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "msx2.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "n64":
            self.labelPlataforma.setText("Nintendo 64")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "n64.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "n64.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "nds":
            self.labelPlataforma.setText("Nintendo DS")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "nds.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "nds.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "neogeocd":
            self.labelPlataforma.setText("NeoGeo CD")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "neogeocd.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "neogeocd.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "neogeo":
            self.labelPlataforma.setText("NeoGeo")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "neogeo.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "neogeo.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "nes":
            self.labelPlataforma.setText("Nintendo Entertainment System")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "nes.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "nes.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "ngp":
            self.labelPlataforma.setText("NeoGeo Pocket")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "ngp.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "ngp.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "ngpc":
            self.labelPlataforma.setText("NeoGeo Pocket Color")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "ngpc.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "ngpc.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "nintendobsx":
            self.labelPlataforma.setText("Nintendo BSX")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "nintendobsx.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "nintendobsx.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "snes":
            self.labelPlataforma.setText("Súper Nintendo")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "snes.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "snes.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "videopac":
            self.labelPlataforma.setText("Magnavox Odyssey 2")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "videopac2.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "videopac2.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "oric":
            self.labelPlataforma.setText("Oric")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "oric.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "oric.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "pc":
            self.labelPlataforma.setText("PC Dos")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "pc.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "pc.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "pcengine":
            self.labelPlataforma.setText("PCEngine")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "pcengine.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "pcengine.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "pcenginecd":
            self.labelPlataforma.setText("PCEngine CD")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "pcenginecd.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "pcenginecd.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "pinball":
            self.labelPlataforma.setText("Pinball")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "pinball.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "pinball.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "ports":
            self.labelPlataforma.setText("Ports")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "ports.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "ports.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "ps2":
            self.labelPlataforma.setText("Playstation 2")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "ps2.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "ps2.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "psx":
            self.labelPlataforma.setText("Playstation")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "psx.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "psx.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "psp":
            self.labelPlataforma.setText("Playstation Portable")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "psp.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "psp.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "pspminis":
            self.labelPlataforma.setText("Playstation Portable Minis")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "pspminis.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "pspminis.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "residualvm":
            self.labelPlataforma.setText("Residualvm")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "residualvm.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "residualvm.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "retropie":
            self.labelPlataforma.setText("Retropie")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "retropie.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "retropie.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "saturn":
            self.labelPlataforma.setText("Sega Saturn")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "saturn.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "saturn.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "sc-3000":
            self.labelPlataforma.setText("Sega SC-3000")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "sc-3000.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "sc-3999.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "scummvm":
            self.labelPlataforma.setText("ScummVM")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "scummvm.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "scummvm.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "sega32x":
            self.labelPlataforma.setText("Sega 32x")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "sega32x.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "sega32x.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "segacd":
            self.labelPlataforma.setText("Sega CD")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "segacd.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "segacd.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "sfc":
            self.labelPlataforma.setText("Super Famicon")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "sfc.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "sfc.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "sg-1000":
            self.labelPlataforma.setText("Sega SG-1000")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "sg-1000.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "sg-1000.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "sgfx" or temp == "supergrafx":
            self.labelPlataforma.setText("Super Grafx")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "sgfx.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "sgfx.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "shmups":
            self.labelPlataforma.setText("Super Grafx")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "shmups.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "shmups.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "snescd":
            self.labelPlataforma.setText("Super Nintendo CD")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "snescd.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "snescd.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "steam":
            self.labelPlataforma.setText("Steam")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "steam.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "steam.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "sufami":
            self.labelPlataforma.setText("Sufami Turbo")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "sufami.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "sufami.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "tectoy":
            self.labelPlataforma.setText("Tectoy")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "tectoy.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "tectoy.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "tg16":
            self.labelPlataforma.setText("TurboGrafx 16")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "tg16.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "tg16.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "tg16cd":
            self.labelPlataforma.setText("TurboGrafx 16 CD")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "tg16cd.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "tg16cd.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "tg-cd":
            self.labelPlataforma.setText("TurboGrafx 16 CD")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "tg16cd.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "tg16cd.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "ti99":
            self.labelPlataforma.setText("Texas Instruments TI-99")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "ti99.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "ti99.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "trs-80":
            self.labelPlataforma.setText("Trackball")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "trs-80.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "trs-80.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "vectrex":
            self.labelPlataforma.setText("Vectrex")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "vectrex.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "vectrex.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "vi20":
            self.labelPlataforma.setText("Commodore Vi-20")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "vi20.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "vi20.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "videopac" or temp == "videopac2":
            self.labelPlataforma.setText("Magnavox Odyssey2")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "videopac2.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "videopac2.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "virtualboy":
            self.labelPlataforma.setText("Nintendo VirtualBoy")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "virtualboy.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "virtualboy.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "wii":
            self.labelPlataforma.setText("Nintendo WII")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "wii.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "wii.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "wiiu":
            self.labelPlataforma.setText("Nintendo WIIU")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "wiiu.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "wiiu.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "wonderswan":
            self.labelPlataforma.setText("WonderSwan")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "wonderswan.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "wonderswan.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "wonderswancolor":
            self.labelPlataforma.setText("WonderSwan Color")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "wonderswancolor.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "wonderswancolor.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "x68000":
            self.labelPlataforma.setText("Sharp X68000")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "x68000.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "x68000.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "zmachine":
            self.labelPlataforma.setText("Infocom")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "zmachine.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "zmachine.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "zxspectrum":
            self.labelPlataforma.setText("Sinclair ZX Spectrum")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "zxspectrum.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "zxspectrum.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        elif temp == "zx81":
            self.labelPlataforma.setText("Sinclair ZX-81")
            fileImage = directorioOriginal + os.sep + "systemlogo" + os.sep +\
                "zx81.png"
            self.im = QPixmap(":/Plataformas/systemlogo/"
                              "zx81.png")
            # self.im = QPixmap(fileImage)
            self.labelImage2.setPixmap(self.im)

        if directory:
            # print("Directorio seleccionado: ", directory)
            self.labelROM.setText(directory)
        else:
            directory = tempdir
            self.labelROM.setText(directory)

        if fileXML:
            # print("Archivo seleccionado: ", file)
            self.labelXML.setText(fileXML)

    def btnClickedXML(self):
        global fileXML
        tempXML = fileXML
        fileXML, _ = QFileDialog.getOpenFileName(self,
                                                 'Selecciona el archivo .xml',
                                                 os.getcwd(),
                                                 "Archivos .XML (*.xml);;Todos\
                                                 los archivos(*.*)")
        temp = ""
        temp = fileXML.replace('/', '\\')
        fileXML = temp
        # QDir.homePath(),
        if fileXML:
            # print("Archivo seleccionado: ", fileXML)
            self.labelXML.setText(fileXML)
        else:
            fileXML = tempXML
            # print("Archivo seleccionado: ", fileXML)
            self.labelXML.setText(fileXML)


class Dialog(QDialog):
    def __init__(self, *args, **kwargs):
        super(Dialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("Actualización requerida")
        self.resize(400, 300)
        self.label = QLabel("Presione el botón para iniciar la descarga.",
                            self)
        self.label.setGeometry(20, 20, 200, 25)
        self.button = QPushButton("Iniciar descarga", self)
        self.button.move(20, 60)
        self.button.pressed.connect(self.initDownload)
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(20, 115, 300, 25)

    def initDownload(self):
        self.label.setText("Descargando archivo...")
        # Deshabilitar el botón mientras se descarga el archivo.
        self.button.setEnabled(False)
        # Ejecutar la descarga en un nuevo hilo.
        self.downloader = Downloader()
        # Conectar las señales que indican el progreso de la descarga
        # con los métodos correspondientes de la barra de progreso.
        self.downloader.setTotalProgress.connect(self.progressBar.setMaximum)
        self.downloader.setCurrentProgress.connect(self.progressBar.setValue)
        # Qt invocará el método `succeeded` cuando el archivo se haya
        # descargado correctamente y `downloadFinished()` cuando el hilo
        # haya terminado.
        self.downloader.succeeded.connect(self.downloadSucceeded)
        self.downloader.finished.connect(self.downloadFinished)
        self.downloader.start()

    def downloadSucceeded(self):
        # Establecer el progreso en 100%.
        self.progressBar.setValue(self.progressBar.maximum())
        self.label.setText("¡El archivo se ha descargado!")

    def downloadFinished(self):
        # Restablecer el botón.
        self.button.setEnabled(True)
        # Eliminar el hilo una vez que fue utilizado.
        # rename("actualizar.act", "actualizar.py")
        # rename("CleanMediaACT.act", "CleanMediaACT.py")
        del self.downloader
        # os.system("python actualizar.py")
        # remove("CleanMediaQT.py")
        # rename("CleanMediaACT.py", "CleanMediaQT.py")
        if os.path.isfile("version.act"):
            if os.path.isfile("version.cmr"):
                remove("version.cmr")
            rename("version.act", "version.cmr")
        python = sys.executable
        os.execl(python, python, 'actualizar.py')
        # remove("actualizar.py")
        # python = sys.executable
        # os.execl(python, python, * sys.argv)
        # sys.exit()


class Downloader(QThread):

    # Señal para que la ventana establezca el valor máximo
    # de la barra de progreso.
    setTotalProgress = pyqtSignal(int)
    # Señal para aumentar el progreso.
    setCurrentProgress = pyqtSignal(int)
    # Señal para indicar que el archivo se descargó correctamente.
    succeeded = pyqtSignal()

    def __init__(self):
        super().__init__()

    def run(self):
        if os.path.isfile("recursos_rc.py"):
            url = "https://raw.githubusercontent.com/danitxu79/CleanMediaRomsQT/master/" "actualizar.py"
            url2 = "https://raw.githubusercontent.com/danitxu79/CleanMediaRomsQT/master/" "CleanMediaQT.py"
            filename = url[url.rfind("/") + 1:]
            # filename2 = url2[url2.rfind("/") + 1:]
            filename2 = "CleanMediaQT.act"
            f = urlopen(url)
            f2 = urlopen(url2)
            fsize = int(f.info()["Content-Length"])
            # fsize = 0
            f2size = int(f2.info()["Content-Length"])
            ftotal = fsize + f2size
            f.close()
            f2.close()
            self.setTotalProgress.emit(ftotal)
            self.descargar(url, filename)
            self.descargar(url2, filename2)
            self.setTotalProgress.emit(ftotal)
        else:
            url = "https://raw.githubusercontent.com/danitxu79/CleanMediaRomsQT/" "master/" "actualizar.py"
            url2 = "https://raw.githubusercontent.com/danitxu79/CleanMediaRomsQT/" "master/" "CleanMediaQT.py"
            filename = url[url.rfind("/") + 1:]
            # filename2 = url2[url2.rfind("/") + 1:]
            filename2 = "CleanMediaQT.act"
            f = urlopen(url)
            f2 = urlopen(url2)
            fsize = int(f.info()["Content-Length"])
            # fsize = 0
            f2size = int(f2.info()["Content-Length"])
            ftotal = fsize + f2size
            f.close()
            f2.close()
            self.setTotalProgress.emit(ftotal)
            self.descargar(url, filename)
            self.descargar(url2, filename2)
            self.setTotalProgress.emit(ftotal)

    def descargar(self, url, filename):
        readBytes = 0
        chunkSize = 1024
        # Abrir la dirección de URL.
        with urlopen(url) as r:
            # Avisar a la ventana cuántos bytes serán descargados.
            with open(filename, "ab") as f:
                while True:
                    # Leer una porción del archivo que estamos descargando.
                    chunk = r.read(chunkSize)
                    # Si el resultado es `None` quiere decir que todavía
                    # no se han descargado los datos. Simplemente
                    # seguimos esperando.
                    if chunk is None:
                        continue
                    # Si el resultado es una instancia de `bytes` vacía
                    # quiere decir que el archivo está completo.
                    elif chunk == b"":
                        break
                    # Escribir la porción descargada en el archivo local.
                    f.write(chunk)
                    readBytes += chunkSize
                    # Avisar a la ventana la cantidad de bytes recibidos.
                    self.setCurrentProgress.emit(readBytes)
        # Si esta línea llega a ejecutarse es porque no ocurrió ninguna
        # excepción en el código anterior.
        self.succeeded.emit()


class Busqueda(QThread):
    # Señal para que la ventana establezca el valor máximo
    # de la barra de progreso.
    setTotalProgress = pyqtSignal(int)
    # Señal para aumentar el progreso.
    setCurrentProgress = pyqtSignal(int)
    # Señal para indicar que el archivo se descargó correctamente.
    succeeded = pyqtSignal()
    # setLabelArchivoProcesado = pyqtSignal(str)
    setListWidgetFile = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        global LimiteBarra, total, num_archivos, linea, todos_directorios
        global todos_archivos, ruta_xml, diccionario, numero_archivos
        ruta_xml = fileXML
        LimiteBarra = 0
        clear()
        diccionario.clear()
        todos_archivos.clear()
        todos_directorios.clear()
        num_archivos = 0
        numero_archivos = 0
        estado = 0
        print(Back.BLUE + Fore.WHITE + Style.BRIGHT + f"""\n
        

            Limpia archivos obsoletos de los directorios "media" dentro de la
         carpeta "ROMS", usando el gamelist.txt como guía para saber si se usa
           el archivo.

          Versión beta, haz una copia de seguridad antes de usar este programa

               CleanMediaQT.py  ver. 2.0

            Creado por Daniel Serrano   -   dani.eus79@gmail.com

        """)

        actual = 0

        for ruta, directorios, archivos in os.walk(directory, topdown=True):
            LimiteBarra += len(archivos)

            print(linea)
            if LimiteBarra == 0:
                self.setListWidgetFile.emit(str("No hay ficheros"))
                return
        for ruta, directorios, archivos in os.walk(directory, topdown=True):
#            print(Back.BLUE + Style.BRIGHT + '\nRuta       :',
#                  Back.BLUE + Style.BRIGHT + ruta)
#            print('\n')
#            print(Back.BLUE + Style.BRIGHT + '\nArchivo xml       :',
#                  Back.BLUE + Style.BRIGHT + fileXML)
#            print('\n')

            for elemento in archivos:
                num_archivos += 1
                archivo = ruta + os.sep + elemento
                estado = os.stat(archivo)
                tamaño = estado.st_size
                totaltamaño = 0
                totaltamaño += tamaño
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
                    totalruta = ruta + os.sep + elemento
                    # LimiteBarra = len(archivos)
                    self.setTotalProgress.emit(int(LimiteBarra))
                    self.setCurrentProgress.emit(int(actual))
                    # setLabelArchivoProcesado.emit(str(elemento))
                    self.setListWidgetFile.emit(str(totalruta))
                    actual += 1

        print(linea)
        print(Back.BLACK + Fore.BLUE + Style.BRIGHT +
              'Núm. archivos:', num_archivos)
        print(Back.BLACK + Fore.YELLOW + Style.BRIGHT +
              'Total (kb)   :', round(totaltamaño/1024, 1))
        peso_kb = round(totaltamaño/1024)
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
            # sys.exit()
            return

        self.succeeded.emit()


class Ejecutar(QThread):
    # Señal para que la ventana establezca el valor máximo
    # de la barra de progreso.
    setTotalProgress = pyqtSignal(int)
    # Señal para aumentar el progreso.
    setCurrentProgress = pyqtSignal(int)
    # Señal para indicar que el archivo se descargó correctamente.
    succeeded = pyqtSignal()
    # setLabelArchivoProcesado = pyqtSignal(str)
    setListWidgetFile = pyqtSignal(str)

    def __init__(self):
        super().__init__()

    def run(self):
        global LimiteBarra, total, num_archivos, linea, todos_directorios
        global todos_archivos, ruta_xml, diccionario, total, numero_archivos
        ruta_xml = fileXML

        print("\n")
        print(linea)
        print("\n")
        clear()

        # diccionario_archivos = diccionario.values()
        # diccionario_directorios = diccionario.keys()
        print(linea)
        numero = 0
        archivo_objetivo = diccionario['archivos'][0]
        directorio_objetivo = diccionario['directorios'][0]
        total = directorio_objetivo + os.sep + archivo_objetivo
        total_archivos_borrados = 0
        pesototal = 0
        LimiteBarra = numero_archivos
        print(LimiteBarra)
        self.setTotalProgress.emit(int(LimiteBarra))
        actual = 0
        # queDirectorio = ""

        for file in todos_archivos:
            correcto = 0
            with open(ruta_xml, "r", encoding="utf8") as fichero_xml:
                for line in fichero_xml:
                    archivo_objetivo = diccionario['archivos'][numero]
                    if file in line:
                        # clear()
                        self.setCurrentProgress.emit(int(actual))
                        # setLabelArchivoProcesado.emit(str(elemento))
                        # self.setListWidgetFile.emit(str(total))
                        actual += 1
                        print(linea)
                        print()
                        print(Back.BLACK + Fore.YELLOW + Style.BRIGHT +
                              "Archivo correcto:")
                        directorio_objetivo = diccionario['directorios'][numero]
                        archivo_objetivo = diccionario['archivos'][numero]
                        total = directorio_objetivo + os.sep + archivo_objetivo
                        print(Back.BLACK + Fore.RED + Style.BRIGHT + "     ",
                              total)
                        if numero < num_archivos:
                            numero = numero + 1
                        correcto = 1
                        # print(file)
                        print()
                        break

            if correcto == 0:
                directorio_objetivo = diccionario['directorios'][numero]
                archivo_objetivo = diccionario['archivos'][numero]
                total = directorio_objetivo + os.sep + archivo_objetivo
                # clear()
                print(linea)
                print()
                print(Back.BLACK + Fore.YELLOW + Style.BRIGHT +
                      "Archivo obsoleto:")
                print(Back.BLACK + Fore.BLUE + Style.BRIGHT + "El archivo ",
                      Back.BLACK + Fore.WHITE + Style.BRIGHT + total +
                      Back.BLACK + Fore.RED + Style.BRIGHT +
                      " va a ser eliminado")
                self.setCurrentProgress.emit(int(actual))
                # setLabelArchivoProcesado.emit(str(elemento))
                self.setListWidgetFile.emit(str(total))
                actual += 1
                if numero < num_archivos:
                    numero = numero + 1
                print()
                archivo = total
                estado = os.stat(archivo)
                tamaño = estado.st_size
                pesototal += tamaño
                total_archivos_borrados += 1
                if ficheroOpcion == 1:
                    remove(total)
                else:
                    directorioBackup = directorio_objetivo + os.sep + 'backup'
                    archivoBackup = directorioBackup + os.sep + archivo_objetivo
                    if os.path.isdir(directorioBackup):
                        shutil.move(total, archivoBackup)
                    else:
                        os.mkdir(directorioBackup)
                        shutil.move(total, archivoBackup)

        fichero_xml.close()

        # clear()
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
        self.succeeded.emit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = mywindow()
    window.show()
    sys.exit(app.exec_())
