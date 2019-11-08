#! /bin/bash
echo off
echo \n
echo Instalando requisitos
echo .....................
echo \n

python -m pip install --upgrade pip
python -m pip install --upgrade virtualenv
virtualenv --python python CMQTenv
source ./CMQTenv/Scripts/activate
pip install --upgrade pyqt5-tools
pip install --upgrade colorama
pip install --upgrade clear-screen

echo \n 
echo Iniciando Clean Media QT
echo ........................
echo \n
echo \n 

cd CleanMediaRomsQT
python ./CleanMediaQT.py
conda deactivate
