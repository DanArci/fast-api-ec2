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

Configura el archivo `.env` con la URL de PostgreSQL y las credenciales de AWS:

```text
DATABASE_URL=postgresql+psycopg2://USER:PASSWORD@POSTGRES_PRIVATE_IP:5432/DATABASE_NAME
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name
```

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

### Endpoints adicionales

- `GET /health`: indica que la API está funcionando.
- `POST /images`: recibe una imagen, valida el tipo, la sube a Amazon S3 con Boto3 y devuelve la respuesta de éxito.
