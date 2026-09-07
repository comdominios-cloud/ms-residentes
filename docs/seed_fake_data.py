"""Carga masiva de datos fake para ms-residentes.

PLACEHOLDER. Objetivo del curso: insertar al menos 20,000 registros
distribuidos entre edificios, unidades y residentes.

Uso previsto:
    python docs/seed_fake_data.py --total 20000

Dependencias sugeridas: faker, psycopg (o sqlalchemy).
"""

TOTAL_REGISTROS = 20_000


def main() -> None:
    # TODO: 1. Leer configuracion de conexion desde variables de entorno.
    # TODO: 2. Generar N edificios.
    # TODO: 3. Generar unidades por edificio.
    # TODO: 4. Generar residentes por unidad hasta completar TOTAL_REGISTROS.
    # TODO: 4b. Generar un usuario por residente con el password ya hasheado.
    # TODO: 5. Insertar por lotes (execute_values / bulk_insert) para no saturar la BD.
    raise NotImplementedError("Pendiente de implementar en la fase de carga de datos.")


if __name__ == "__main__":
    main()
