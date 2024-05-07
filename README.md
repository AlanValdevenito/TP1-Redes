# TP1 Redes

Trabajo practico basado en la implementacion de un File Transfer.

## Grupo 6
- **Integrante 1** - [Alan Valdevenito](https://github.com/AlanValdevenito)
- **Integrante 2** - [Mateo Julián Rico](https://github.com/ricomateo)
- **Integrante 3** - [Mariana Galdo Martinez](https://github.com/marg30)
- **Integrante 4** - [José Manuel Dieguez](https://github.com/jmdieguez)
- **Integrante 5** - [Manuel Rivera Villatte](https://github.com/ManusaRivi)

## Ejecucion de UPLOAD

En una primera terminal ejecutar

```
$ ./start-server -P 1
```

En una segunda terminal ejecutar

```
$ python3 upload -n result.txt -s seq.txt -P 1
```

Nota 1: Se debe generar el archivo seq.txt.
Nota 2: Si se desea utilizar GBN se debe indicar con el flag '-P 2'.

## Ejecucion de DOWNLOAD

En una primera terminal ejecutar

```
$ python3 start-server -P 1
```

En una segunda terminal ejecutar

```
$ python3 download -d result.txt -n seq.txt -P 1
```

Nota 1: Se debe generar el archivo seq.txt.
Nota 2: Si se desea utilizar GBN se debe indicar con el flag '-P 2'.