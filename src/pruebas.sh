#!/usr/bin/env bash

FILE="tp.pdf"

echo "Pruebas con 10% de pérdida de paquetes"
sudo iptables -A INPUT -m statistic --mode random --probability 0.1 -j DROP

# mato cualquier servidor que haya en el puerto 12000
PORT_NUMBER=12000
sudo lsof -i udp:${PORT_NUMBER} | awk 'NR!=1 {print $2}' | xargs kill > /dev/null 2>&1 

> gbn_download.txt
> gbn_upload.txt
> snw_download.txt
> snw_upload.txt


echo "Iniciando server Go-Back-N"
python3 main_server.py -P 0 -q > /dev/null 2>&1 & 
server_1_pid=$!


echo ""
echo "Iniciando cliente 1 (download)"
start_client_1=`date +%s`
python3 main_client.py download -P 0 -q -n $FILE -d "upload_libro1.pdf" > /dev/null 2>&1 & 
client_1_pid=$!


start_client_2=`date +%s`
echo "Iniciando cliente 2 (upload)"
python3 main_client.py upload -P 0 -q  -s $FILE -n "upload_libro2.pdf" > /dev/null 2>&1 &
client_2_pid=$!



start_client_3=`date +%s`
echo "Iniciando cliente 3 (download)"
python3 main_client.py download -P 0 -q  -n $FILE -d "upload_libro3.pdf" > /dev/null 2>&1 &
client_3_pid=$!


start_client_4=`date +%s`
echo "Iniciando cliente 4 (upload)"
python3 main_client.py upload -P 0 -q  -s $FILE -n "upload_libro3.pdf" > /dev/null 2>&1 &
client_4_pid=$!

wait $client_1_pid
echo "Termina cliente 1 (download)"
end_1=`date +%s`
echo `expr $end_1 - $start_client_1` >> gbn_download.txt
time_client_1_gbn=`expr $end_1 - $start_client_1`

wait $client_2_pid
echo "Termina cliente 2 (upload)"
end_2=`date +%s`
echo `expr $end_2 - $start_client_2` >> gbn_upload.txt
time_client_2_gbn=`expr $end_2 - $start_client_2`

wait $client_3_pid
echo "Termina cliente 3 (download)"
end_3=`date +%s`
echo `expr $end_3 - $start_client_3` >> gbn_download.txt
time_client_3_gbn=`expr $end_3 - $start_client_3`


wait $client_4_pid
echo "Termina cliente 4 (upload)"
end_4=`date +%s`
echo `expr $end_4 - $start_client_4` >> gbn_upload.txt
time_client_4_gbn=`expr $end_4 - $start_client_4`


sudo kill $server_1_pid


echo ""
echo ""

echo "Iniciando server Stop & Wait"

python3 main_server.py -P 1 > /dev/null 2>&1 &
server_2_pid=$!

echo ""
echo "Iniciando cliente 1 (download)"
start_client_1=`date +%s`
python3 main_client.py download -P 1 -n $FILE -d "upload_libro1.pdf" > /dev/null 2>&1 &
client_1_pid=$!

echo "Iniciando cliente 2 (upload)"
start_client_2=`date +%s`
python3 main_client.py upload -P 1 -s $FILE -n "upload_libro2.pdf" > /dev/null 2>&1 &
client_2_pid=$!

echo "Iniciando cliente 3 (download)"
start_client_3=`date +%s`
python3 main_client.py download -P 1 -n $FILE -d "upload_libro3.pdf" > /dev/null 2>&1 &
client_3_pid=$!

echo "Iniciando cliente 4 (upload)"
start_client_4=`date +%s`
python3 main_client.py upload -P 1 -s $FILE -n "upload_libro4.pdf" > /dev/null 2>&1 &
client_4_pid=$!


wait $client_1_pid
echo "Termina cliente 1"
end_1=`date +%s`
echo `expr $end_1 - $start_client_1` >> snw_download.txt
time_client_1_snw=`expr $end_1 - $start_client_1`

echo "Termina cliente 2"
wait $client_2_pid
end_2=`date +%s`
echo `expr $end_2 - $start_client_2` >> snw_upload.txt
time_client_2_snw=`expr $end_2 - $start_client_2`

echo "Termina cliente 3"
wait $client_3_pid
end_3=`date +%s`
echo `expr $end_3 - $start_client_3` >> snw_download.txt
time_client_3_snw=`expr $end_3 - $start_client_3`

echo "Termina cliente 4"
wait $client_4_pid
end_4=`date +%s`
echo `expr $end_4 - $start_client_4` >> snw_upload.txt
time_client_4_snw=`expr $end_4 - $start_client_4`


echo ""
echo ""
echo "------------------------------ Métricas ------------------------------" 
echo "Go-Back-N download:"
echo "Cliente 1 = $time_client_1_gbn segundos"
echo "Cliente 3 = $time_client_3_gbn segundos"
awk '{ sum += $1; } END {printf( "Promedio = %.4f\n", sum/NR ); }'  gbn_download.txt
echo ""
echo "Go-Back-N upload:"
echo "Cliente 2 = $time_client_2_gbn segundos"
echo "Cliente 4 = $time_client_4_gbn segundos"
awk '{ sum += $1; } END {printf( "Promedio = %.4f\n", sum/NR ); }'  gbn_upload.txt
echo ""
echo ""
echo ""
echo "Stop & Wait download:"
echo "Cliente 1 = $time_client_1_snw segundos"
echo "Cliente 3 = $time_client_3_snw segundos"
awk '{ sum += $1; } END {printf( "Promedio = %.4f\n", sum/NR ); }'  snw_download.txt
echo ""
echo "Stop & Wait upload:"
echo "Cliente 2 = $time_client_2_snw segundos"
echo "Cliente 4 = $time_client_4_snw segundos"
awk '{ sum += $1; } END {printf( "Promedio = %.4f\n", sum/NR ); }'  snw_upload.txt
sudo kill $server_2_pid

sudo rm gbn_download.txt
sudo rm gbn_upload.txt
sudo rm snw_download.txt
sudo rm snw_upload.txt

#sudo lsof -i udp:${PORT_NUMBER} | awk 'NR!=1 {print $2}' | xargs kill > /dev/null 2>&1 

sudo iptables -D INPUT -m statistic --mode random --probability 0.1 -j DROP