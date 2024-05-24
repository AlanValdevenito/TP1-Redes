# TP1 Redes - Grupo 6

Trabajo practico cuyo objetivo es la implementacion de un File Transfer.

## Integrantes

- **Integrante 1** - [Alan Valdevenito](https://github.com/AlanValdevenito)
- **Integrante 2** - [Mateo Julián Rico](https://github.com/ricomateo)
- **Integrante 3** - [Mariana Galdo Martinez](https://github.com/marg30)
- **Integrante 4** - [José Manuel Dieguez](https://github.com/jmdieguez)
- **Integrante 5** - [Manuel Rivera Villatte](https://github.com/ManusaRivi)

## Dependencias

### Termcolor

1. Abrir una terminal

2. Ejecutar el siguiente comando:

```
$ pip3 install termcolor
```

### Matplotlib


1. Abrir una terminal

2. Ejecutar el siguiente comando:

```
$ pip3 install matplotlib
```

### Comcast

En el siguiente repositorio se encuentran las instrucciones de instalación: https://github.com/tylertreat/comcast

## Ejecucion

### Comando UPLOAD

1. Abrir dos terminales

2. En la primer terminal ejecutar el siguiente comando:

```
$ python3 ./start-server -P <numeroProtocolo>
```

3. En la segunda terminal ejecutar el siguiente comando:

```
$ python3 upload -n <archivoResultado> -s <archivoParaSubir> -P <numeroProtocolo>
```

Nota: El protocolo Stop and Wait se indica con numero de protocolo igual a 1 y el protocolo GBN se indica con numero de protocolo igual a 2

### Comando DOWNLOAD

1. Abrir dos terminales

2. En la primer terminal ejecutar el siguiente comando:

```
$ python3 start-server -P <numeroProtocolo>
```

3. En la segunda terminal ejecutar el siguiente comando:

```
$ python3 download -d <archivoResultado> -n <archivoParaDescargar> -P <numeroProtocolo>
```

Nota: El protocolo Stop and Wait se indica con numero de protocolo igual a 1 y el protocolo GBN se indica con numero de protocolo igual a 2