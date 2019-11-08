#! /bin/bash
cls
@echo off
echo \n
echo Descargando herramientas...
echo ...........................
echo \n

echo Borrando versiones antiguas...
echo ..............................
del Git.exe 
echo \n

sudo apt-get update && sudo apt-get install git

echo \n
echo Comenzamos descarga programa principal
echo ......................................
echo \n
echo \n
echo Clonando repositorio
echo ....................
echo \n

git clone https://github.com/danitxu79/CleanMediaRomsQT.git

./setup.sh 


