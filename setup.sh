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



RP="$HOME/RetroPie"
RPMENU="$RP/retropiemenu"
RPSETUP="$
HOME/RetroPie-Setup"
RPCONFIGS="/opt/retropie/configs/all"
GAMELIST="$RP/roms/retropie/gamelist.xml"
SCRIPTPATH=$(realpath $0)

cd $PMENU
echo -e "\n ${LRED}--${NC}${WHITE} Writing Gamelist.xml modifications...${NC}"
sleep 1

 if [ -f ~/RetroPie/retropiemenu/gamelist.xml ]; then
        cp ~/RetroPie/retropiemenu/gamelist.xml /tmp
 else
        cp /opt/retropie/configs/all/emulationstation/gamelists/retropie/gamelist.xml /tmp
 fi
 cat /tmp/gamelist.xml |grep -v "</gameList>" > /tmp/templist.xml

ifexist=`cat /tmp/templist.xml |grep CleanManagerQT |wc -l`

if [[ ${ifexist} > 0 ]]; then 
		echo "already in gamelist.xml" > /tmp/exists
else
	echo " <game>" >> /tmp/templist.xml
    echo "      <path>./CleanManagerQT.sh</path>" >> /tmp/templist.xml
    echo "      <name>Clean Manager QT</name>" >> /tmp/templist.xml
    echo "      <desc>Clean al media no used from disk</desc>" >> /tmp/templist.xml
    echo "      <image>./icons/CleanMediaQT.png</image>" >> /tmp/templist.xml
    echo "      <playcount>1</playcount>" >cd > /tmp/templist.xml
    echo "      <lastplayed></lastplayed>" >> /tmp/templist.xml
    echo "    </game>" >> /tmp/templist.xml
    echo "</gameList>" >> /tmp/templist.xml
    cp /tmp/templist.xml ~/RetroPie/retropiemenu/gamelist.xml
fi

echo -e "\n ${LRED}[${NC}${LGREEN} Installation Finished ${NC}${LRED}]${NC}\n"
sleep 1


cd $RP
cd "$RP/CleanManagerQT"
cp CleanManagerQT,png "$RPEMU/images"

echo #! /bin/bash >> "$RPMENU/CleanManagerQT.sh"
echo sh \\..\..\CleanManagerQT\launcher.sh >> "$RPMENU/CleanManagerQT.SH"



echo \n 
echo Iniciando Clean Media QT
echo ........................
echo \n
echo \n 

cd CleanMediaRomsQT
python ./CleanMediaQT.py
conda deactivate
