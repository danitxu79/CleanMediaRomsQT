cls
@echo off
echo.
echo Descargando herramientas...
echo ...........................
echo.

echo Borrando versiones antiguas...
echo ..............................
del Git.exe 
echo.

START /WAIT /B .\Wget\wget.exe -N -q "https://raw.githubusercontent.com/danitxu79/CleanMediaRomsQT/master/GitZip/Git.exe" --no-check-certificate      

echo.
echo Descomprimiendo herramientas...
echo ...............................
echo.

timeout /nobreak 03

Start /WAIT .\Git.exe -WindowStyle Minimized -ArgumentList -y
echo.
echo.

del Git.exe -y

echo Comenzamos descarga programa principal
echo ......................................
echo.
echo.
echo Clonando repositorio
echo ....................
echo.

.\Git\bin\git.exe clone https://github.com/danitxu79/CleanMediaRomsQT.git

START .\Git\git-bash.exe setup.sh 


