# Servidor web con contenedores Docker

Ejecutamos:

`docker compose -f docker-compose.yml up`

## A tener en cuenta antes de ejecutarlo:

- Revisar parámetros que se mandan como variables de entorno en las aplicaciones web.

- En el fichero docker-compose.yml (en el 'healthcheck' también está) revisar password de la base de datos y de Ethstats.

- Revisar los script de creación de las bases de datos de cada aplicación web por si se quieren modificar los usuarios o contraseñas iniciales.

- Revisar las URL de los ficheros de configuración del nginx (carpeta *conf.d*) por si se quieren modificar.

## Los servicios que se despliegan

- **ethstats**: el servidor de Ethereum Stats, situado en la carpeta **ethstats-server**. Estará accesible en el servidor accediendo al puerto definido en el fichero *docker-compose.yml*.
- **esploratzaile**: la aplicación Esploratzaile, situada en ../Pilotoak/EsploratzaileAPP. Estará accesible en el servidor accediendo con los nombres configurados en el fichero de la carpeta *nginx/conf.d/EsploratzaileAPP.conf*.
- **prometheus**: el recolector de métricas de monitorización. Permanece accesible solo dentro de la red Docker y obtiene métricas de los cuatro nodos Besu a través del puerto 9545.
- **grafana**: el panel de visualización de métricas. Se conecta automáticamente al Prometheus del stack y queda publicado detrás de Nginx en `http://monitorea.localhost`.
- **webserver**: el servidor nginx que hace de proxy para acceder a uno u otro servicio dependiendo del nombre con el que hayamos accedido. Escucha en el puerto 80.

## URLs principales

- `http://localhost` y `http://ethstats.localhost`: panel Ethstats.
- `http://esploratzaile.localhost`: explorador de bloques.
- `http://monitorea.localhost`: panel Grafana de monitorización (`admin` / `admin` en el primer acceso).

## Puertos Besu relevantes para este despliegue

- `8545`: JSON-RPC HTTP.
- `8546`: JSON-RPC WebSocket con JWT.
- `9545`: métricas Prometheus expuestas para el servidor de monitorización.