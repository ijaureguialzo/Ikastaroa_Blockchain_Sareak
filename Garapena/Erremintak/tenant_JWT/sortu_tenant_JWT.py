
"""
Genera un conjunto completo de claves de tenant y su JWT asociado.

Uso:
    python sortu_tenant_JWT.py 1

Salida en la carpeta actual:
    ./1/
        tenantKey1.key
        tenantKey1.pub
        privateRSAKeyOperator1.pem
        publicRSAKeyOperator1.pem
        JWT_1
"""
"""
pip install pyjwt[crypto]

Uso:
Cada usuario tiene una lista de cadenas de permisos que definen los métodos a los que puede acceder. Para otorgar acceso:

    Para todos los métodos de la API, especifica ["*:*"].
    Para todos los métodos de un grupo específico de la API, especifica ["<api_group>:*"]. Por ejemplo, ["eth:*"].
    Para métodos específicos de la API, especifica ["<api_group>:<method_name>"]. Por ejemplo, ["admin:peers"].

Con la autenticación habilitada, para indicar explícitamente que un usuario no puede acceder a ningún método, incluye al usuario con una lista de permisos vacía ([]). Los usuarios con una lista de permisos vacía no pueden acceder a ningún método JSON-RPC.
"""

import argparse
import base64
from pathlib import Path

import jwt
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, x25519
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import NoEncryption
from cryptography.hazmat.primitives.serialization import PrivateFormat
from cryptography.hazmat.primitives.serialization import PublicFormat


def parse_args() -> int:
    """Lee el identificador numérico del tenant desde la línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Genera claves de tenant, claves RSA y un JWT firmado."
    )
    parser.add_argument(
        "tenant_number",
        type=int,
        help="Número del tenant que se usará para nombrar la carpeta y los ficheros.",
    )
    args = parser.parse_args()
    return args.tenant_number


def generate_tenant_keys(tenant_number: int, output_dir: Path) -> str:
    """Genera la pareja X25519 del tenant y devuelve la clave pública en base64."""
    tenant_private_key = x25519.X25519PrivateKey.generate()
    tenant_public_key = tenant_private_key.public_key()

    tenant_private_bytes = tenant_private_key.private_bytes(
        encoding=Encoding.Raw,
        format=PrivateFormat.Raw,
        encryption_algorithm=NoEncryption(),
    )
    tenant_public_bytes = tenant_public_key.public_bytes(
        encoding=Encoding.Raw,
        format=PublicFormat.Raw,
    )

    tenant_private_b64 = base64.b64encode(tenant_private_bytes).decode("ascii")
    tenant_public_b64 = base64.b64encode(tenant_public_bytes).decode("ascii")

    # Se guardan en base64 para que el formato sea fácil de reutilizar.
    (output_dir / f"tenantKey{tenant_number}.key").write_text(
        tenant_private_b64,
        encoding="utf-8",
    )
    (output_dir / f"tenantKey{tenant_number}.pub").write_text(
        tenant_public_b64,
        encoding="utf-8",
    )

    return tenant_public_b64


def generate_rsa_keys(tenant_number: int, output_dir: Path) -> bytes:
    """Genera la pareja RSA usada para firmar y validar el JWT."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()

    private_pem = private_key.private_bytes(
        encoding=Encoding.PEM,
        format=PrivateFormat.PKCS8,
        encryption_algorithm=NoEncryption(),
    )
    public_pem = public_key.public_bytes(
        encoding=Encoding.PEM,
        format=PublicFormat.SubjectPublicKeyInfo,
    )

    (output_dir / f"privateRSAKeyOperator{tenant_number}.pem").write_bytes(private_pem)
    (output_dir / f"publicRSAKeyOperator{tenant_number}.pem").write_bytes(public_pem)

    return private_pem


def generate_jwt(
    tenant_number: int,
    output_dir: Path,
    private_pem: bytes,
    privacy_public_key: str,
) -> str:
    """Crea el JWT manteniendo los mismos parámetros base del fichero original."""
    payload = {
        "permissions": ["*:*"],
        "privacyPublicKey": privacy_public_key,
        "exp": 1600899999002,
    }
    headers = {"alg": "RS256", "typ": "JWT"}

    encoded_jwt = jwt.encode(payload, key=private_pem, algorithm="RS256", headers=headers)
    (output_dir / f"JWT_{tenant_number}").write_text(encoded_jwt, encoding="utf-8")

    return encoded_jwt


def main() -> None:
    """Crea la carpeta del tenant y genera todos los ficheros relacionados."""
    tenant_number = parse_args()
    output_dir = Path.cwd() / str(tenant_number)
    output_dir.mkdir(parents=True, exist_ok=True)

    privacy_public_key = generate_tenant_keys(tenant_number, output_dir)
    private_pem = generate_rsa_keys(tenant_number, output_dir)
    jwt_token = generate_jwt(
        tenant_number,
        output_dir,
        private_pem,
        privacy_public_key,
    )

    print(f"Ficheros generados en: {output_dir}")
    print(f"- tenantKey{tenant_number}.key")
    print(f"- tenantKey{tenant_number}.pub")
    print(f"- privateRSAKeyOperator{tenant_number}.pem")
    print(f"- publicRSAKeyOperator{tenant_number}.pem")
    print(f"- JWT_{tenant_number}")
    print()
    print("JWT generado:")
    print(jwt_token)


if __name__ == "__main__":
    main()