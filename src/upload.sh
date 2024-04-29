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

chmod +x upload.sh

echo "Creando archivos de prueba..."

seq 100 > seq.txt

python3 ./main_client.py upload -n upload_result.txt -s seq.txt > /dev/null 2>&1

diff seq.txt upload_result.txt
test_result "Los archivos son iguales"

rm seq.txt
rm upload_result.txt

# Nota: En caso de que aparezca 'Permiso denegado' ejecutar '$ chmod +x upload.sh'