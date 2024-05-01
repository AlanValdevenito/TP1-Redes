# Informe

## Introducción

Este trabajo práctico se plantea como objetivo la comprensión y la puesta en práctica de los conceptos y herramientas
necesarias para la implementación de un protocolo RDT. Para lograr este objetivo, se deberá desarrollar una aplicación
de arquitectura cliente-servidor que implemente la funcionalidad de transferencia de archivos mediante las siguientes
operaciones:
- UPLOAD: Transferencia de un archivo del cliente hacia el servidor
- DOWNLOAD: Transferencia de un archivo del servidor hacia el cliente

Dada las diferentes operaciones que pueden realizarse entre el cliente y el servidor, se requiere del diseño e implemen-
tación de un protocolo de aplicación básico que especifique los mensajes intercambiados entre los distintos procesos.

La implementación de las aplicaciones solicitadas deben cumplir los siguientes requisitos:
- La aplicaciones deben ser desarrolladas en lenguaje Python utilizando la librería estandard de sockets.
- La comunicación entre los procesos se debe implementar utilizando UDP como protocolo de capa de transporte.
- Las aplicaciones cliente/servidor pueden ser desplegadas en localhost.
- Para lograr una transferencia confiable al utilizar el protocolo UDP, se pide implementar una versión utilizando el
protocolo Stop & Wait y otra versión utilizando el protocolo Go-BACK-N.
- El servidor debe ser capaz de procesar de manera concurrente la transferencia de archivos con múltiples clientes.

## Hipótesis y suposiciones realizadas

...

## Implementación

...

## Pruebas

...

## Preguntas a responder

1. Describa la arquitectura Cliente-Servidor.
2. ¿Cuál es la función de un protocolo de capa de aplicación?.
3. Detalle el protocolo de aplicación desarrollado en este trabajo.
4. La capa de transporte del stack TCP/IP ofrece dos protocolos: TCP y UDP. ¿Qué servicios proveen dichos protocolos?. ¿Cuáles son sus características? ¿Cuando es apropiado utilizar cada uno?.

## Dificultades encontradas

...

## Conclusión

...