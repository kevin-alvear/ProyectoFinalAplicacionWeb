# library_project/backend/database.py
import os # ¡Importa el módulo os!
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# --- INICIO DEL CAMBIO ---
# Lee la URL de la base de datos desde una variable de entorno.
# Si la variable no existe, usa la URL de localhost como un valor por defecto.
# Esto hace que tu código funcione tanto en Docker como en local.
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:admin@localhost:5433/librarydb"
)

# Agregamos un print para saber a qué base de datos se está conectando, ¡muy útil para depurar!
print(f"INFO:     Conectando a la base de datos en: {SQLALCHEMY_DATABASE_URL}")
# --- FIN DEL CAMBIO ---

# El resto del archivo no cambia
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()