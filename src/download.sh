#!/bin/bash

green=$(tput setaf 2)
red=$(tput setaf 1)
reset=$(tput sgr0)

# Función para mostrar mensajes de éxito o fallo
function test_result() {
    if [ $? -eq 0 ]; then
        echo "${green}OK - $1${reset}"
    else
        echo "${red}FAIL - $1${reset}"
    fi
}

echo "Creando archivos de prueba..."

seq 100 > seq.txt

python3 ./main_client.py download -d download_result.txt -n seq.txt > /dev/null 2>&1

diff seq.txt download_result.txt
test_result "Los archivos son iguales"

rm seq.txt
rm download_result.txt

# Nota: En caso de que aparezca 'Permiso denegado' ejecutar '$ chmod +x download.sh'