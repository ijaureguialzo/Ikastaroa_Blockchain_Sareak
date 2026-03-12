"""
Aplicacion en Python para desplegar e interactuar con el contrato inteligente Formularioak.
Este script se conecta a nodos de Ethereum, despliega el contrato y realiza operaciones.
"""

import json
import os
from web3 import Web3
from eth_account import Account

# Lista fija de direcciones IP para intentar la conexion (puerto 8545)
IP_LIST = [
    "192.168.100.1",
    "192.168.100.2",
    "192.168.100.3",
    "192.168.100.4",
    # Anade mas direcciones IP si es necesario
]

def connect_to_provider(ip_list):
    """
    Intenta conectarse a un proveedor web3 de la lista de IP.
    Devuelve una instancia de Web3 si la conexion tiene exito.
    """
    for ip in ip_list:
        try:
            provider_url = f"http://{ip}:8545"
            print(f"Intentando conectar con {provider_url}...")
            w3 = Web3(Web3.HTTPProvider(provider_url))
            
            # Comprueba la conexion verificando si podemos obtener el ultimo bloque
            if w3.is_connected():
                print(f"Conexion establecida correctamente con {provider_url}")
                return w3
            else:
                print(f"Fallo la conexion con {provider_url}: no conectado")
        except Exception as e:
            print(f"Fallo la conexion con {provider_url}: {str(e)}")
            continue
    
    raise Exception("No se pudo conectar con ningun proveedor de la lista de IP")

def create_private_key():
    """
    Genera una nueva clave privada de Ethereum y devuelve la cuenta.
    Devuelve el objeto de cuenta con la direccion y la clave privada.
    """
    # Crea una nueva cuenta con una clave privada aleatoria
    account = Account.create()
    print(f"\nNueva cuenta de Ethereum generada:")
    print(f"  Direccion: {account.address}")
    print(f"  Clave privada: {account.key.hex()}")
    return account

def load_contract_files():
    """
    Carga el bytecode y el ABI del contrato desde archivos.
    Devuelve la tupla (bytecode, abi).
    """
    # Obtiene el directorio donde se encuentra este script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Carga el bytecode
    bytecode_path = os.path.join(script_dir, "Formularioak.bytecode")
    with open(bytecode_path, "r") as f:
        bytecode_raw = f.read().strip()
    
    # Limpia y valida el bytecode
    # Elimina cualquier espacio en blanco y asegura que sea hexadecimal valido
    bytecode_clean = ''.join(bytecode_raw.split())
    
    # Comprueba si empieza por 0x; si no, lo anade
    if not bytecode_clean.startswith("0x"):
        bytecode_clean = "0x" + bytecode_clean
    
    # Valida que todos los caracteres sean hexadecimales
    hex_part = bytecode_clean[2:] if bytecode_clean.startswith("0x") else bytecode_clean
    if not all(c in '0123456789abcdefABCDEF' for c in hex_part):
        raise Exception("Bytecode invalido: contiene caracteres no hexadecimales")
    
    # Comprueba si la longitud del bytecode es par (cada byte son 2 caracteres hex)
    if len(hex_part) % 2 != 0:
        raise Exception("Bytecode invalido: numero impar de caracteres hexadecimales")
    
    bytecode = bytecode_clean
    
    # Carga el ABI
    abi_path = os.path.join(script_dir, "Formularioak.abi")
    with open(abi_path, "r") as f:
        abi = json.load(f)
    
    # Valida el formato del bytecode
    bytecode_bytes = len(hex_part) // 2
    print(f"\nArchivos del contrato cargados:")
    print(f"  Longitud del bytecode: {len(hex_part)} caracteres hexadecimales ({bytecode_bytes} bytes)")
    print(f"  El bytecode empieza por: {bytecode[:20]}...")
    print(f"  ABI cargado correctamente")
    
    # Comprueba si el bytecode parece valido (deberia empezar por patrones comunes de Solidity)
    if not bytecode.startswith("0x6080"):
        print(f"  Advertencia: el bytecode no empieza por el patron esperado de Solidity (0x6080)")
    
    # Inspecciona el bytecode en busca de problemas de compatibilidad con la version de la EVM
    # Comprueba si existe PUSH0 (0x5f), que requiere Shanghai EVM o posterior
    push0_found = []
    for i in range(min(100, bytecode_bytes)):  # Comprueba los primeros 100 bytes
        byte_val = hex_part[i*2:(i*2)+2].upper()
        if byte_val == '5F':  # Opcode PUSH0
            push0_found.append(f"posicion {i}")
    
    if push0_found:
        print(f"  ADVERTENCIA: el bytecode contiene el opcode PUSH0 (0x5f) en: {', '.join(push0_found[:5])}")
        print(f"  PUSH0 requiere la actualizacion Shanghai de la EVM (EIP-3855) o posterior")
        print(f"  Si tu red Besu usa una version antigua de la EVM, esto provocara errores INVALID_OPERATION")
        print(f"  Solucion: recompila el contrato con una version anterior de Solidity (por ejemplo, 0.8.19) orientada a una EVM mas antigua")
        print(f"  O configura Besu para usar la version Shanghai/Cancun de la EVM")
    
    # Comprueba si existe el opcode INVALID (0xFE) en los primeros 50 bytes
    invalid_found = []
    for i in range(min(50, bytecode_bytes)):
        byte_val = hex_part[i*2:(i*2)+2].upper()
        if byte_val == 'FE':
            invalid_found.append(f"0xFE en la posicion {i}")
    
    if invalid_found:
        print(f"  ADVERTENCIA: se encontro el opcode INVALID (0xFE) en: {', '.join(invalid_found)}")
        print(f"  Esto sugiere que el bytecode puede estar corrupto o contener datos no validos")
    
    return bytecode, abi

def deploy_contract(w3, account, bytecode, abi):
    """
    Despliega el contrato en la blockchain.
    Devuelve la instancia del contrato desplegado y su direccion.
    """
    # Establece la cuenta por defecto para las transacciones
    w3.eth.default_account = account.address
    
    # Obtiene informacion de la red
    try:
        chain_id = w3.eth.chain_id
        print(f"  chainId de la red: {chain_id}")
    except Exception as e:
        print(f"  Advertencia: no se pudo obtener el chainId de la red: {e}")
        chain_id = 1337  # Valor por defecto para redes privadas
        print(f"  Usando el chainId por defecto: {chain_id}")
    
    # Comprueba el saldo de la cuenta (solo informativo; no se necesita en una red sin gas)
    balance = w3.eth.get_balance(account.address)
    print(f"  Saldo de la cuenta: {balance} wei ({w3.from_wei(balance, 'ether')} ETH)")
    print(f"  Nota: se usa una configuracion sin gas para una red privada de Besu")
    
    # Obtiene el nonce de la cuenta
    nonce = w3.eth.get_transaction_count(account.address)
    print(f"  Nonce de la cuenta: {nonce}")
    
    # Crea la transaccion de despliegue del contrato
    contract = w3.eth.contract(bytecode=bytecode, abi=abi)
    
    # Calcula el gas intrinseco minimo necesario segun el tamano del bytecode
    # Gas intrinseco = 21000 (base) + 32000 (creacion de contrato) + 200 por cada byte del bytecode
    bytecode_size = len(bytecode) - 2 if bytecode.startswith("0x") else len(bytecode)  # Resta 2 por el prefijo "0x"
    bytecode_bytes = bytecode_size // 2  # Cada caracter hexadecimal representa 4 bits, asi que 2 caracteres = 1 byte
    intrinsic_gas = 21000 + 32000 + (200 * bytecode_bytes)
    print(f"  Tamano del bytecode: {bytecode_bytes} bytes")
    print(f"  Gas intrinseco minimo: {intrinsic_gas}")
    
    # Construye la transaccion
    # Usa el chainId de la red y gasPrice 0 para la red privada de Besu sin gas
    print(f"\nDesplegando contrato...")
    transaction = contract.constructor().build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 0x7FFFFFFF, # Limite maximo de gas para el despliegue
        "gasPrice": 0,   # Sin gas para la red privada de Besu
        "chainId": chain_id,
    })
    
    # Firma la transaccion
    signed_txn = account.sign_transaction(transaction)
    
    # Envia la transaccion
    print(f"  Hash de la transaccion: {signed_txn.hash.hex()}")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    
    # Espera la confirmacion de la transaccion
    print(f"  Esperando la confirmacion de la transaccion...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=90)
    
    # Comprueba si la transaccion se completo correctamente
    if tx_receipt.status != 1:
        # Intenta obtener mas informacion sobre el fallo
        error_msg = f"El despliegue del contrato fallo con estado: {tx_receipt.status}"
        
        # Comprueba si hay una razon de revert en el recibo
        if hasattr(tx_receipt, 'revertReason') and tx_receipt.revertReason:
            error_msg += f"\n  Motivo del revert: {tx_receipt.revertReason}"
        
        # Comprueba el gas usado
        if hasattr(tx_receipt, 'gasUsed'):
            error_msg += f"\n  Gas usado: {tx_receipt.gasUsed}"
        
        raise Exception(error_msg)
    
    # Obtiene la direccion del contrato desde el recibo
    contract_address = tx_receipt.contractAddress
    print(f"  Contrato desplegado en la direccion: {contract_address}")
    print(f"  Numero de bloque: {tx_receipt.blockNumber}")
    print(f"  Estado de la transaccion: exito")
    
    # Crea la instancia del contrato
    deployed_contract = w3.eth.contract(address=contract_address, abi=abi)
    
    return deployed_contract, contract_address

def send_transaction(w3, account, contract, function_call, description):
    """
    Funcion generica para enviar una transaccion al contrato.
    Args:
        w3: Instancia de Web3
        account: Objeto de cuenta
        contract: Instancia del contrato
        function_call: Llamada a la funcion del contrato (por ejemplo, contract.functions.createForm(...))
        description: Descripcion de lo que hace la transaccion
    Returns:
        Recibo de la transaccion
    """
    print(f"\n{description}...")
    
    # Obtiene el nonce de la cuenta
    nonce = w3.eth.get_transaction_count(account.address)
    
    # Obtiene el chainId desde la red
    try:
        chain_id = w3.eth.chain_id
    except Exception as e:
        print(f"  Advertencia: no se pudo obtener el chainId de la red: {e}")
        chain_id = 1337  # Valor por defecto para redes privadas
    
    # Construye la transaccion
    transaction = function_call.build_transaction({
        "from": account.address,
        "nonce": nonce,
        "gas": 0x7FFFFFFF,  # Limite maximo de gas para llamadas a funciones
        "gasPrice": 0,      # Sin gas para la red privada de Besu
        "chainId": chain_id,
    })
    
    # Firma la transaccion
    signed_txn = account.sign_transaction(transaction)
    
    # Envia la transaccion
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"  Hash de la transaccion: {tx_hash.hex()}")
    
    # Espera la confirmacion de la transaccion
    print(f"  Esperando la confirmacion de la transaccion...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=90)
    print(f"  Transaccion confirmada en el bloque: {tx_receipt.blockNumber}")
    
    # Comprueba si la transaccion se completo correctamente
    if tx_receipt.status != 1:
        raise Exception(f"La transaccion fallo con estado: {tx_receipt.status}")
    print(f"  Estado de la transaccion: exito")
    
    return tx_receipt

def create_form(w3, account, contract, datu1, datu2):
    """
    Crea un nuevo formulario usando la funcion createForm.
    Devuelve la tupla (transaction_receipt, form_number).
    form_number es el zenbakia asignado al formulario recien creado.
    Extrae el numero de formulario del evento FormCreated en el recibo de la transaccion.
    """
    function_call = contract.functions.createForm(datu1, datu2)
    receipt = send_transaction(w3, account, contract, function_call, f"Creando formulario con datu1='{datu1}', datu2='{datu2}'")
    
    # Extrae el numero de formulario (zenbakia) del evento FormCreated
    # El evento se emite con formCount como zenbakia
    form_number = None
    for log in receipt['logs']:
        try:
            # Intenta decodificar el log como un evento FormCreated
            decoded_event = contract.events.FormCreated().process_log(log)
            form_number = decoded_event['args']['zenbakia']
            print(f"  Formulario creado con zenbakia: {form_number}")
            break
        except:
            # No es un evento FormCreated, continua
            continue
    
    if form_number is None:
        raise Exception("No se pudo extraer el numero de formulario del evento FormCreated")
    
    return receipt, form_number

def update_form(w3, account, contract, zenbakia, datu1, datu2):
    """
    Actualiza un formulario existente usando la funcion updateForm.
    Devuelve el recibo de la transaccion.
    """
    function_call = contract.functions.updateForm(zenbakia, datu1, datu2)
    return send_transaction(w3, account, contract, function_call, f"Actualizando el formulario {zenbakia} con datu1='{datu1}', datu2='{datu2}'")

def get_form(contract, zenbakia):
    """
    Recupera los datos del formulario usando la funcion getForm (funcion view, no necesita transaccion).
    Devuelve la tupla (datu1, datu2).
    """
    print(f"\nRecuperando los datos del formulario (zenbakia = {zenbakia})...")
    try:
        form_data = contract.functions.getForm(zenbakia).call()
        print(f"  Datos del formulario recuperados:")
        print(f"    datu1: {form_data[0]}")
        print(f"    datu2: {form_data[1]}")
        return form_data
    except Exception as e:
        raise Exception(f"No se pudo recuperar el formulario {zenbakia}: {str(e)}")

def get_events(w3, contract, contract_address, zenbakia, from_block=0):
    """
    Recupera los eventos FormCreated y FormUpdated de la blockchain para un formulario concreto.
    Usa el campo indexado zenbakia para filtrar eventos de forma eficiente.
    Args:
        w3: Instancia de Web3
        contract: Instancia del contrato
        contract_address: Direccion del contrato
        zenbakia: Numero de formulario por el que filtrar eventos (campo indexado)
        from_block: Numero de bloque inicial desde el que buscar
    Returns:
        Tupla con las listas (form_created_events, form_updated_events)
    """
    print(f"\nRecuperando eventos del formulario zenbakia={zenbakia} desde el bloque {from_block}...")
    
    # Obtiene el numero del ultimo bloque
    latest_block = w3.eth.block_number
    print(f"  Buscando desde el bloque {from_block} hasta el bloque {latest_block}")
    
    try:
        # Usa argument_filters para filtrar por el campo indexado zenbakia
        # Esto es mas eficiente que recuperar todos los eventos y filtrarlos en Python
        argument_filters = {'zenbakia': zenbakia}
        
        # Obtiene los eventos FormCreated filtrados por zenbakia
        # Nota: web3.py usa snake_case para los parametros (from_block, to_block)
        form_created_events = contract.events.FormCreated.get_logs(
            from_block=from_block, 
            to_block=latest_block,
            argument_filters=argument_filters
        )
        
        # Obtiene los eventos FormUpdated filtrados por zenbakia
        form_updated_events = contract.events.FormUpdated.get_logs(
            from_block=from_block, 
            to_block=latest_block,
            argument_filters=argument_filters
        )
        
        print(f"  Se encontraron {len(form_created_events)} eventos FormCreated para el formulario {zenbakia}")
        print(f"  Se encontraron {len(form_updated_events)} eventos FormUpdated para el formulario {zenbakia}")
        
        return form_created_events, form_updated_events
    except Exception as e:
        print(f"  Error al recuperar los eventos: {e}")
        # Devuelve listas vacias si falla la recuperacion de eventos
        return [], []

def display_events(form_created_events, form_updated_events):
    """
    Muestra los eventos recuperados con un formato legible.
    """
    print(f"\n{'='*60}")
    print(f"REGISTRO DE EVENTOS")
    print(f"{'='*60}")
    
    if form_created_events:
        print(f"\nEventos FormCreated:")
        for i, event in enumerate(form_created_events, 1):
            print(f"  Evento {i}:")
            print(f"    Bloque: {event.blockNumber}")
            print(f"    Transaccion: {event.transactionHash.hex()}")
            print(f"    zenbakia: {event.args.zenbakia}")
            print(f"    datu1: {event.args.datu1}")
            print(f"    datu2: {event.args.datu2}")
    else:
        print(f"\nNo se encontraron eventos FormCreated")
    
    if form_updated_events:
        print(f"\nEventos FormUpdated:")
        for i, event in enumerate(form_updated_events, 1):
            print(f"  Evento {i}:")
            print(f"    Bloque: {event.blockNumber}")
            print(f"    Transaccion: {event.transactionHash.hex()}")
            print(f"    zenbakia: {event.args.zenbakia}")
            print(f"    datu1: {event.args.datu1}")
            print(f"    datu2: {event.args.datu2}")
    else:
        print(f"\nNo se encontraron eventos FormUpdated")
    
    print(f"{'='*60}")

def main():
    """
    Funcion principal que orquesta todo el proceso.
    """
    try:
        # Paso 1: Conectarse al proveedor web3
        w3 = connect_to_provider(IP_LIST)
        
        # Paso 2: Crear una clave privada de Ethereum
        account = create_private_key()
        
        # Paso 3: Cargar los archivos del contrato
        bytecode, abi = load_contract_files()
        
        # Paso 4: Desplegar el contrato
        contract, contract_address = deploy_contract(w3, account, bytecode, abi)
        
        # Obtener el numero de bloque tras el despliegue para filtrar eventos despues
        deployment_block = w3.eth.block_number
        
        # Paso 5: Crear un formulario
        create_receipt, form_zenbakia = create_form(w3, account, contract, "Dato de ejemplo 1", "Dato de ejemplo 2")
        print(f"  Formularios totales: {form_zenbakia}")
        
        # Paso 6: Obtener los datos del formulario usando el numero devuelto
        form_data = get_form(contract, form_zenbakia)
        
        # Paso 7: Actualizar el formulario (primera vez)
        update_form(w3, account, contract, form_zenbakia, "Dato actualizado 1", "Dato actualizado 2")
        
        # Paso 8: Actualizar el formulario (segunda vez)
        update_form(w3, account, contract, form_zenbakia, "Dato final 1", "Dato final 2")
        
        # Paso 9: Recuperar y mostrar los eventos del formulario que hemos creado
        form_created_events, form_updated_events = get_events(
            w3, contract, contract_address, 
            zenbakia=form_zenbakia, 
            from_block=deployment_block
        )
        display_events(form_created_events, form_updated_events)
        
        print(f"\n[EXITO] Todas las operaciones se completaron correctamente")
        
    except Exception as e:
        print(f"\n[ERROR] Se produjo un error: {str(e)}")
        raise

if __name__ == "__main__":
    main()

