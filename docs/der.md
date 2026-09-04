# Diagrama Entidad-Relacion - ms-residentes

> PLACEHOLDER. Reemplazar este archivo (o agregar `der.png` / `der.drawio`)
> con el diagrama ER definitivo antes de la primera entrega.

## Entidades previstas

- **edificios**: torres o bloques del condominio.
- **unidades**: departamentos, pertenecen a un edificio.
- **residentes**: personas que habitan o son propietarias de una unidad.

## Relaciones

```
edificios (1) ──< (N) unidades (1) ──< (N) residentes
```

- Un edificio tiene muchas unidades (`unidades.edificio_id` -> `edificios.id`).
- Una unidad tiene muchos residentes (`residentes.unidad_id` -> `unidades.id`).
- La relacion obligatoria del curso (minimo 2 tablas relacionadas) es
  **unidades <- residentes**.

## Imagen

<!-- ![Diagrama ER](der.png) -->
