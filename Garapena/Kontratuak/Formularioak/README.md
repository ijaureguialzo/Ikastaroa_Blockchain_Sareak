# Smart Contract baten hedapen eta erabilera adibidea

Proiektu honek Ethereum blockchain-ean formularioak kudeatzeko sistema bat eskaintzen du. Proiektuaren osagaiak: Solidity smart contract bat, Python script bat kontratua hedatzeko eta erabiltzeko, eta web interfaze bat trazabilitatea kontsultatzeko.

## Proiektuaren Deskribapena

Proiektu hau formularioen kudeaketa eta trazabilitatea blockchain-ean gordetzeko sistema bat da. Smart Contract baten bidez, formularioak sortu, eguneratu eta kontsultatu daitezke, eta guzti hori blockchain-ean erregistratzen da, trazabilitatea bermatuz.

## Fitxategien Azalpena

### `Formularioak.sol`
Solidity smart contract nagusia. Formularioak kudeatzeko funtzionalitateak eskaintzen ditu:
- **createForm()**: Formulario berri bat sortzen du `datu1` eta `datu2` datuekin
- **updateForm()**: Existitzen den formulario bat eguneratzen du
- **getForm()**: Formulario baten datuak kontsultatzen ditu
- **getFormCount()**: Sortu diren formulario kopurua itzultzen du

Kontratuak bi event emititzen ditu:
- `FormCreated`: Formulario berri bat sortzen denean
- `FormUpdated`: Formulario bat eguneratzen denean

### `hedatu_erabili.py`
Python script bat, Web3.py liburutegia erabiliz smart contract-a hedatzeko eta erabiltzeko. Script honek:
- Ethereum nodo batekin konektatzen da (IP zerrenda batetik)
- Kontratuaren bytecode eta ABI fitxategiak kargatzen ditu
- Kontratua blockchain-ean hedatzen du
- Formularioak sortzen eta eguneratzen ditu
- Formularioen datuak kontsultatzen ditu
- Blockchain-eko event-ak kontsultatzen ditu trazabilitatea erakusteko

### `trazabilitatea.html`
Web interfaze bat, formularioen historia kontsultatzeko. Interfaze honek:
- Ethereum nodo batekin konektatzen da
- Kontratuaren helbidea eta formulario zenbakia sartuz, formulario baten historia erakusten du
- `FormCreated` eta `FormUpdated` event-ak kontsultatzen ditu
- Event-ak taula batean erakusten ditu, bloke zenbakia, transakzio hash-a, datuak eta denbora-marka barne

### `Formularioak.abi` eta `Formularioak.bytecode`
Kontratuaren ABI (Application Binary Interface) eta bytecode fitxategiak. Hauek beharrezkoak dira kontratua hedatzeko eta erabiltzeko.

## Beharrezkoak

### Python Script-a erabiltzeko:
- Python 3.x
- `web3` liburutegia: `pip install web3==7.14.0`
- `eth-account` liburutegia: `pip install eth-account==0.13.7`
- Ethereum nodo bat konektagarri (adibidez, Blockchain FP Euskadi sareko nodo bat)

### Web interfazea erabiltzeko:
- Web nabigatzaile moderno bat
- Ethereum nodo bat konektagarri (adibidez, Besu nodo bat)
- Internet konexioa (ethers.js CDN-etik kargatzeko)

## Erabilera

### 1. Python Script-a exekutatu

```bash
python hedatu_erabili.py
```

Script-ak automatikoki:
1. Ethereum nodo batekin konektatuko da
2. Kontratua blockchain-ean hedatuko du
3. Formulario bat sortuko du
4. Formularioa eguneratuko du
5. Event-ak kontsultatuko ditu

### 2. Web interfazea erabili

1. `trazabilitatea.html` fitxategia nabigatzaile batean ireki
2. Kontratuaren helbidea sartu (Python script-ak terminalean erakutsiko du)
3. Formulario zenbakia sartu (adibidez, 1)
4. "Retrieve Events" botoia sakatu
5. Formularioaren historia taula batean erakutsiko da

## Konfigurazioa

### IP Zerrenda Aldatu

Emanda datorren IP helbidearekin Blockchain FP Euskadi sarean hedatuko da proiektua baina Python script-ean eta HTML fitxategian IP zerrenda alda dezakezu zure Ethereum nodoaren helbidea sartzeko edo nodo berriak gehitzeko:

**hedatu_erabili.py**:
```python
IP_LIST = [
    "192.168.100.1",  # Zure nodoaren IP helbidea
    "192.168.100.2",
    "192.168.100.3",
    "192.168.100.4",
    # Gehiago gehitu ditzakezu
]
```

**trazabilitatea.html**:
```javascript
const IP_LIST = ["192.168.100.1","192.168.100.2","192.168.100.3","192.168.100.4"];  // Zure nodoen IP helbideak
```

## Segurtasuna

- Kontratuak `onlyOwner` modifikadorea erabiltzen du, beraz soilik kontratuaren jabeak (hedatzailea) sortu eta eguneratu ditzake formularioak
- Kontratuaren jabea konstruktorean zehazten da (`msg.sender`)
- Formularioak kontsultatzeko (`getForm()`) ez da beharrezkoa jabea izatea

## Teknologia Stack-a

- **Solidity**: Smart contract-ak garatzeko lengoaia
- **Python**: Backend script-ak garatzeko
- **Web3.py**: Python-etik Ethereum-rekin komunikatzeko
- **JavaScript/HTML**: Web interfazea garatzeko
- **ethers.js**: JavaScript-etik Ethereum-rekin komunikatzeko

## Oharrak

- Proiektu hau Besu sare pribatu batekin (Blockchain FP Euskadi) probatua izan da, zero-gas konfigurazioarekin. Sarea pribatua da nodoen parte hartzearen aldetik baina publikoa erabilera aldetik.
- Kontratua Solidity 0.8.19 bertsioarekin konpilatu da
- EVM London bertsioa erabili da konpilazioan
- Aurreko puntuak kontutan izanda, kontratu berriak sortu eta konpilatzeko erreminta erraz bat [Remix](https://remix.ethereum.org) izan daiteke
## Lizentzia

MIT Lizentzia

---

# Ejemplo de despliegue y uso de un Smart Contract

Este proyecto ofrece un sistema para gestionar formularios en la blockchain de Ethereum. Los componentes del proyecto son: un smart contract en Solidity, un script en Python para desplegar y usar el contrato, y una interfaz web para consultar la trazabilidad.

## Descripcion del proyecto

Este proyecto es un sistema para la gestion de formularios y el almacenamiento de su trazabilidad en la blockchain. Mediante un Smart Contract, se pueden crear, actualizar y consultar formularios, y todo ello queda registrado en la blockchain, garantizando la trazabilidad.

## Explicacion de los archivos

### `Formularioak.sol`
Smart contract principal en Solidity. Ofrece funcionalidades para gestionar formularios:
- **createForm()**: Crea un nuevo formulario con los datos `datu1` y `datu2`
- **updateForm()**: Actualiza un formulario existente
- **getForm()**: Consulta los datos de un formulario
- **getFormCount()**: Devuelve la cantidad de formularios creados

El contrato emite dos eventos:
- `FormCreated`: Cuando se crea un nuevo formulario
- `FormUpdated`: Cuando se actualiza un formulario

### `hedatu_erabili.py`
Script en Python para desplegar y utilizar el smart contract usando la libreria Web3.py. Este script:
- Se conecta a un nodo de Ethereum (desde una lista de IP)
- Carga los archivos bytecode y ABI del contrato
- Despliega el contrato en la blockchain
- Crea y actualiza formularios
- Consulta los datos de los formularios
- Consulta los eventos de la blockchain para mostrar la trazabilidad

### `trazabilitatea.html`
Interfaz web para consultar el historial de formularios. Esta interfaz:
- Se conecta a un nodo de Ethereum
- Introduciendo la direccion del contrato y el numero de formulario, muestra el historial de un formulario
- Consulta los eventos `FormCreated` y `FormUpdated`
- Muestra los eventos en una tabla, incluyendo numero de bloque, hash de transaccion, datos y marca temporal

### `Formularioak.abi` y `Formularioak.bytecode`
Archivos ABI (Application Binary Interface) y bytecode del contrato. Son necesarios para desplegar y utilizar el contrato.

## Requisitos

### Para usar el script de Python:
- Python 3.x
- Libreria `web3`: `pip install web3==7.14.0`
- Libreria `eth-account`: `pip install eth-account==0.13.7`
- Un nodo de Ethereum accesible (por ejemplo, un nodo de la red Blockchain FP Euskadi)

### Para usar la interfaz web:
- Un navegador web moderno
- Un nodo de Ethereum accesible (por ejemplo, un nodo Besu)
- Conexion a Internet (para cargar desde el CDN de ethers.js)

## Uso

### 1. Ejecutar el script de Python

```bash
python hedatu_erabili.py
```

El script automaticamente:
1. Se conectara a un nodo de Ethereum
2. Desplegara el contrato en la blockchain
3. Creara un formulario
4. Actualizara el formulario
5. Consultara los eventos

### 2. Usar la interfaz web

1. Abre el archivo `trazabilitatea.html` en un navegador
2. Introduce la direccion del contrato (el script de Python la mostrara en la terminal)
3. Introduce el numero de formulario (por ejemplo, 1)
4. Pulsa el boton "Retrieve Events"
5. El historial del formulario se mostrara en una tabla

## Configuracion

### Cambiar la lista de IP

Con la direccion IP proporcionada, el proyecto se desplegara en la red Blockchain FP Euskadi, pero puedes cambiar la lista de IP en el script de Python y en el archivo HTML para introducir la direccion de tu nodo de Ethereum o anadir nuevos nodos:

**hedatu_erabili.py**:
```python
IP_LIST = [
    "192.168.100.1",  # Direccion IP de tu nodo
    "192.168.100.2",
    "192.168.100.3",
    "192.168.100.4",
    # Puedes anadir mas
]
```

**trazabilitatea.html**:
```javascript
const IP_LIST = ["192.168.100.1","192.168.100.2","192.168.100.3","192.168.100.4"];  // Direcciones IP de tus nodos
```

## Seguridad

- El contrato usa el modificador `onlyOwner`, por lo que solo el propietario del contrato (quien lo despliega) puede crear y actualizar formularios
- El propietario del contrato se define en el constructor (`msg.sender`)
- Para consultar formularios (`getForm()`) no es necesario ser el propietario

## Stack tecnologico

- **Solidity**: Lenguaje para desarrollar smart contracts
- **Python**: Para desarrollar scripts backend
- **Web3.py**: Para comunicarse con Ethereum desde Python
- **JavaScript/HTML**: Para desarrollar la interfaz web
- **ethers.js**: Para comunicarse con Ethereum desde JavaScript

## Notas

- Este proyecto ha sido probado con una red privada Besu (Blockchain FP Euskadi), con configuracion zero-gas. La red es privada desde el punto de vista de la participacion de nodos, pero publica desde el punto de vista de su uso.
- El contrato se ha compilado con la version 0.8.19 de Solidity
- En la compilacion se ha usado la version London de la EVM
- Teniendo en cuenta los puntos anteriores, una herramienta sencilla para crear y compilar nuevos contratos puede ser [Remix](https://remix.ethereum.org)

## Licencia

Licencia MIT
