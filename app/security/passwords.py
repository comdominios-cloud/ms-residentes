"""Hash y verificacion de passwords con bcrypt.

Nunca se guarda la password en claro: solo el hash, que es de una sola via.
bcrypt incluye la sal dentro del propio hash, por eso no hay que guardarla aparte.
"""

import bcrypt

# Costo del hash. Mas alto = mas lento de calcular = mas caro de atacar.
ROUNDS = 12
# bcrypt solo considera los primeros 72 bytes de la password.
MAX_BYTES = 72


def hash_password(password: str) -> str:
    pwd = password.encode()[:MAX_BYTES]
    return bcrypt.hashpw(pwd, bcrypt.gensalt(rounds=ROUNDS)).decode()


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode()[:MAX_BYTES], password_hash.encode())
    except ValueError:
        # Hash con formato invalido en la BD: se trata como credencial incorrecta.
        return False
