# Integrante responsable

| | |
|---|---|
| **Repositorio** | `ms-residentes` |
| **Integrante** | [@Osomar1705](https://github.com/Osomar1705) |
| **Rol** | API con base de datos (Python / PostgreSQL) |
| **Puerto** | 9001 publicado, 8000 interno |

## Alcance

`ms-residentes`: edificios, unidades, residentes y **usuarios** (register, login, crear, eliminar), en Python/FastAPI sobre PostgreSQL.

> ### Camino critico
>
> Este repositorio **bloquea a otros dos integrantes**:
>
> - @carloscondor1610 necesita tu **PostgreSQL con datos** para su contenedor de ingesta.
> - @alxgr-08 necesita tu **API arriba y el `POST /auth/login`** para el frontend.
>
> Es lo primero que tiene que estar funcionando de todo el proyecto.

## Avance del 50% — entrega del 6 al 12 de septiembre

- [ ] Contenedor de **PostgreSQL 5432** levantado en la VM de base de datos, con volumen para que la data persista
- [ ] Tablas `edificios`, `unidades`, `residentes`, `usuarios` creadas ([docs/schema.sql](docs/schema.sql))
- [ ] **Algo de data** cargada (el ACL dijo que no hace falta mucha: el seed de 20k es para despues)
- [ ] `POST /auth/register` y `POST /auth/login` funcionando
- [ ] Al menos 2 `GET` de residentes/unidades funcionando
- [ ] Microservicio publicado en el puerto **9001** de la VM de produccion
- [ ] Persistencia real: reiniciar el contenedor y que los datos sigan
- [ ] **Coleccion de Postman** lista para la demo
- [ ] Imagen en **Docker Hub** para que las 2 VM gemelas hagan pull
- [ ] Pasar a @carloscondor1610 el host/puerto/credenciales de la BD
- [ ] Pasar a @alxgr-08 la URL de la API y el contrato de login

---

## Como trabajamos

Cada repositorio pertenece a un integrante y se desarrolla de forma
**independiente**: las APIs con base de datos no se llaman entre si. La unica
integracion entre microservicios vive en `ms-ficha-residente`, y la del lado del
usuario en `web-condominio`.

Los cambios a este repositorio los define su responsable. Si otro integrante
necesita algo de esta API, se pide via issue en vez de tocar el codigo.

## Equipo

| Repositorio | Integrante | Rol | Puerto |
|---|---|---|---|
| [ms-residentes](https://github.com/comdominios-cloud/ms-residentes) | @Osomar1705 | API con BD - Python / PostgreSQL | 9001 |
| [ms-pagos](https://github.com/comdominios-cloud/ms-pagos) | @sebastianperez72 | API con BD - Java / MySQL | 9002 |
| [ms-incidencias](https://github.com/comdominios-cloud/ms-incidencias) | @fabianbot1331 | API con BD - lenguaje por definir / MongoDB | 9003 |
| [ms-ficha-residente](https://github.com/comdominios-cloud/ms-ficha-residente) | @Brisseth-raton | Backend / Infraestructura | 9004 |
| [web-condominio](https://github.com/comdominios-cloud/web-condominio) | @alxgr-08 | Frontend / Amplify | 5173 (dev) |
| [ms-analitico](https://github.com/comdominios-cloud/ms-analitico) | @carloscondor1610 | Data Science | 9005 |
| [ingesta-datos](https://github.com/comdominios-cloud/ingesta-datos) | @carloscondor1610 | Data Science | — |

> CS2032 Cloud Computing - UTEC | Sistema de Administracion de Condominios
