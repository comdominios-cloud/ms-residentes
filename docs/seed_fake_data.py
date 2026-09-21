"""Carga masiva de datos ficticios para ms-residentes (PostgreSQL).

El curso pide insertar como minimo 20,000 registros en al menos una tabla de
cada base. Aca la tabla masiva es `residentes`.

Uso:
    python docs/seed_fake_data.py                 # 20,000 residentes
    python docs/seed_fake_data.py --total 50000
    python docs/seed_fake_data.py --limpiar       # borra antes de insertar

Lee la conexion de las variables de entorno (o del .env):
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD

Dependencias:
    pip install faker psycopg[binary] python-dotenv
"""

import argparse
import os
import random
import sys
from datetime import datetime, timedelta

try:
    import psycopg
    from dotenv import load_dotenv
    from faker import Faker
except ImportError as e:
    sys.exit(f"Falta una dependencia: {e}\n  pip install faker psycopg[binary] python-dotenv")

TOTAL_POR_DEFECTO = 20_000
LOTE = 5_000

# Cuantas unidades por edificio y cuantos residentes por unidad, en promedio.
UNIDADES_POR_EDIFICIO = 40
RESIDENTES_POR_UNIDAD = 2.5

TIPOS = ("PROPIETARIO", "INQUILINO")

fake = Faker("es_ES")
Faker.seed(2026)
random.seed(2026)


def conexion():
    load_dotenv()
    faltantes = [
        v for v in ("POSTGRES_HOST", "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD")
        if not os.getenv(v)
    ]
    if faltantes:
        sys.exit(f"Faltan variables de entorno: {', '.join(faltantes)}")

    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def limpiar(conn) -> None:
    """Borra en orden inverso a las claves foraneas."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM residentes")
        cur.execute("DELETE FROM unidades")
        cur.execute("DELETE FROM edificios")
        cur.execute("ALTER SEQUENCE residentes_id_seq RESTART WITH 1")
        cur.execute("ALTER SEQUENCE unidades_id_seq RESTART WITH 1")
        cur.execute("ALTER SEQUENCE edificios_id_seq RESTART WITH 1")
    conn.commit()
    print("  Tablas vaciadas")


def insertar_edificios(conn, cantidad: int) -> list[int]:
    filas = [
        (
            f"Torre {fake.unique.last_name()}",
            fake.street_address()[:255],
            random.randint(5, 20),
        )
        for _ in range(cantidad)
    ]

    with conn.cursor() as cur:
        # `copy` es el camino rapido de PostgreSQL para cargas masivas: evita
        # el ida y vuelta de un INSERT por fila.
        with cur.copy(
            "COPY edificios (nombre, direccion, num_pisos) FROM STDIN"
        ) as copia:
            for fila in filas:
                copia.write_row(fila)

        cur.execute("SELECT id FROM edificios ORDER BY id")
        ids = [r[0] for r in cur.fetchall()]

    conn.commit()
    print(f"  edificios:  {len(filas):>7,} insertados")
    return ids


def insertar_unidades(conn, edificios: list[int], cantidad: int) -> list[int]:
    usados: set[tuple[int, str]] = set()
    filas = []

    while len(filas) < cantidad:
        edificio_id = random.choice(edificios)
        piso = random.randint(1, 20)
        codigo = f"{random.choice('ABCD')}-{piso}{random.randint(1, 9):02d}"

        if (edificio_id, codigo) in usados:
            continue

        usados.add((edificio_id, codigo))
        filas.append((edificio_id, codigo, piso, round(random.uniform(45, 180), 2)))

    with conn.cursor() as cur:
        with cur.copy(
            "COPY unidades (edificio_id, codigo, piso, area_m2) FROM STDIN"
        ) as copia:
            for fila in filas:
                copia.write_row(fila)

        cur.execute("SELECT id FROM unidades ORDER BY id")
        ids = [r[0] for r in cur.fetchall()]

    conn.commit()
    print(f"  unidades:   {len(filas):>7,} insertadas")
    return ids


def insertar_residentes(conn, unidades: list[int], total: int) -> None:
    documentos: set[str] = set()
    insertados = 0
    hoy = datetime.now()

    with conn.cursor() as cur:
        while insertados < total:
            cantidad = min(LOTE, total - insertados)
            lote = []

            while len(lote) < cantidad:
                documento = str(random.randint(10_000_000, 99_999_999))
                if documento in documentos:
                    continue
                documentos.add(documento)

                nombres = fake.first_name()
                apellidos = f"{fake.last_name()} {fake.last_name()}"
                lote.append(
                    (
                        random.choice(unidades),
                        nombres[:120],
                        apellidos[:120],
                        documento,
                        f"{documento}@example.com",
                        f"9{random.randint(10_000_000, 99_999_999)}",
                        random.choices(TIPOS, weights=(70, 30))[0],
                        random.random() > 0.05,  # 5% dados de baja
                        hoy - timedelta(days=random.randint(0, 1460)),
                    )
                )

            with cur.copy(
                "COPY residentes "
                "(unidad_id, nombres, apellidos, documento, email, telefono, "
                " tipo, activo, creado_en) FROM STDIN"
            ) as copia:
                for fila in lote:
                    copia.write_row(fila)

            conn.commit()
            insertados += cantidad
            print(f"  residentes: {insertados:>7,} / {total:,}", end="\r", flush=True)

    print(f"  residentes: {insertados:>7,} insertados          ")


def main() -> None:
    parser = argparse.ArgumentParser(description="Carga masiva para ms-residentes")
    parser.add_argument("--total", type=int, default=TOTAL_POR_DEFECTO,
                        help=f"Residentes a generar (por defecto {TOTAL_POR_DEFECTO:,})")
    parser.add_argument("--limpiar", action="store_true",
                        help="Vaciar las tablas antes de insertar")
    args = parser.parse_args()

    n_unidades = max(1, int(args.total / RESIDENTES_POR_UNIDAD))
    n_edificios = max(1, int(n_unidades / UNIDADES_POR_EDIFICIO))

    print(f"Generando {args.total:,} residentes en {n_unidades:,} unidades "
          f"de {n_edificios:,} edificios")

    with conexion() as conn:
        if args.limpiar:
            limpiar(conn)

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM residentes")
            existentes = cur.fetchone()[0]

        if existentes and not args.limpiar:
            print(f"  Aviso: ya hay {existentes:,} residentes. Se agregan encima.")
            print("  Usa --limpiar para empezar de cero.")

        edificios = insertar_edificios(conn, n_edificios)
        unidades = insertar_unidades(conn, edificios, n_unidades)
        insertar_residentes(conn, unidades, args.total)

        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM residentes")
            print(f"\nTotal en la tabla residentes: {cur.fetchone()[0]:,}")


if __name__ == "__main__":
    main()
