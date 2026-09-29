# FastAPI en EC2

Esta copia ejecuta únicamente la API. No inicia PostgreSQL, no crea tablas al arrancar y no ejecuta migraciones. Los endpoints de productos conservan su comportamiento y consultan una instancia PostgreSQL remota; la base de datos y la tabla `app_inv_products` deben existir antes de usar las operaciones CRUD.

## Configuración

Define `DATABASE_URL` con la dirección privada del EC2 que aloja PostgreSQL:

```text
postgresql+psycopg2://USUARIO:CONTRASENA@IP_PRIVADA_POSTGRES:5432/NOMBRE_BASE
```

Si la contraseña contiene caracteres especiales, codifícala para URL. En AWS, permite el tráfico TCP por el puerto `5432` en el grupo de seguridad de PostgreSQL únicamente desde el grupo de seguridad del EC2 de la API. No expongas PostgreSQL a internet.

Para desarrollo local, copia `.env.example` a `.env` y reemplaza sus valores. El archivo `.env` está excluido de Git y de la imagen Docker.

## Ejecutar

Con Python y uv:

```powershell
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

Con Docker Compose, después de configurar `.env`:

```powershell
docker compose up --build -d
```

La API queda disponible en el puerto `8000`. Swagger UI: `/docs`.
