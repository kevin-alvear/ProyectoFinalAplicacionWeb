# library_project/backend/schemas.py
from pydantic import BaseModel, Field
from typing import Optional, List, Union
from datetime import date
from enum import Enum

# --- Enum para el estado del usuario ---
class EstadoUsuario(str, Enum):
    ACTIVO = "ACTIVO"
    MOROSO = "MOROSO"
    MULTADO = "MULTADO"

# --- Esquemas para Libro ---
class LibroBase(BaseModel):
    isbn: str = Field(..., example="978-3-16-148410-0", max_length=17, description="Número ISBN del libro (único)") # Obligatorio
    titulo: str = Field(..., example="Cien años de soledad", max_length=255)
    autor: str = Field(..., example="Gabriel García Márquez", max_length=255)
    numPaginas: int = Field(..., example=496, gt=0)
    portadaURI: Optional[str] = Field(None, example="https://example.com/portada.jpg", description="URI de la imagen de portada")

class LibroCreate(LibroBase):
    numEjemplares: int = Field(..., ge=0, example=5, description="Número total de ejemplares adquiridos inicialmente")

class Libro(LibroBase):
    id: int # El ID se genera en la base de datos
    numEjemplares: int # Número total de ejemplares comprados
    numEjemplaresDisponibles: int # Cambia con préstamos y devoluciones
    # Relación con ejemplares y recomendaciones (no se expone directamente en el esquema de salida de Libro para evitar recursión inmediata)

    class Config:
        from_attributes = True # Permite mapear de modelos SQLAlchemy a esquemas Pydantic

# --- Esquemas para Ejemplar ---
class EjemplarBase(BaseModel):
    id_libro: int = Field(..., example=1, description="Identificación del libro al que pertenece el ejemplar")
    codigoEjemplar: str = Field(..., example="EJ-CienAnos-001", max_length=50, description="Código único de identificación del ejemplar") # Obligatorio
    adquiridoEl: Optional[date] = Field(default_factory=date.today, description="Fecha de adquisición del ejemplar")
    observaciones: Optional[str] = Field(None, example="En perfecto estado", description="Texto sobre el estado del ejemplar")

class EjemplarCreate(EjemplarBase):
    pass

class Ejemplar(EjemplarBase):
    id: int
    # libro: Libro # Se podría incluir para anidar info del libro
    # prestamo_activo: Optional["Prestamo"] = None # Se podría incluir para anidar info del préstamo activo

    class Config:
        from_attributes = True

# --- Esquemas para Usuario (Base) ---
class UsuarioBase(BaseModel):
    login: str = Field(..., example="jdoe", max_length=50, description="Nombre de usuario para iniciar sesión (obligatorio)")
    # password: str = Field(..., example="passwordseguro", min_length=6, description="Contraseña del usuario") # ATENCIÓN: ¡No es seguro en texto plano!
    nombre: str = Field(..., example="John", max_length=100)
    apellidos: str = Field(..., example="Doe", max_length=100)
    email: str = Field(..., example="john.doe@example.com", max_length=150, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    calle: str = Field(..., example="Calle Principal", max_length=150)
    numero: str = Field(..., example="123", max_length=20)
    piso: Optional[str] = Field(None, example="A", max_length=20)
    ciudad: str = Field(..., example="Quito", max_length=100)
    codigo_postal: str = Field(..., example="170101", max_length=10)
    estado: EstadoUsuario = Field(default=EstadoUsuario.ACTIVO, description="Estado actual del usuario")

class UsuarioCreateBase(UsuarioBase):
    # Clase base para la creación de usuarios, útil para FastAPI Union de ProfesorCreate/AlumnoCreate
    pass

class Usuario(UsuarioBase):
    id: int # El ID se genera en la base de datos
    tipo_usuario: str # "profesor" o "alumno"
    # prestamos_actuales: List["Prestamo"] = [] # Lista de préstamos actuales
    # multa_actual: Optional["Multa"] = None # Multa actual (si existe)

    class Config:
        from_attributes = True

# --- Esquemas para Profesor ---
class ProfesorCreate(UsuarioCreateBase):
    departamento: str = Field(..., example="Informática", max_length=100)

class Profesor(Usuario):
    departamento: str

    class Config:
        from_attributes = True

# --- Esquemas para Alumno ---
class AlumnoCreate(UsuarioCreateBase):
    telefono_padres: str = Field(..., example="0991234567", max_length=20)

class Alumno(Usuario):
    telefono_padres: str

    class Config:
        from_attributes = True

# --- Esquemas para Préstamo ---
class PrestamoBase(BaseModel):
    id_ejemplar: int = Field(..., example=1, description="ID del ejemplar prestado")
    id_usuario: int = Field(..., example=1, description="ID del usuario que toma prestado")
    fecha_prestamo: Optional[date] = Field(default_factory=date.today, description="Fecha de préstamo")
    fecha_devolucion_esperada: date = Field(..., description="Fecha en la que debería devolverse")

class PrestamoCreate(PrestamoBase):
    pass

class Prestamo(PrestamoBase):
    id: int # El ID se genera en la base de datos
    # ejemplar: Ejemplar # Se podría incluir para anidar info del ejemplar
    # usuario: Usuario # Se podría incluir para anidar info del usuario

    class Config:
        from_attributes = True

# --- Esquemas para Multa ---
class MultaBase(BaseModel):
    id_usuario: int = Field(..., example=1, description="ID del usuario que tiene la multa")
    fecha_inicio: Optional[date] = Field(default_factory=date.today, description="Fecha de inicio de la multa")
    dias_acumulados: Optional[int] = Field(default=0, ge=0, description="Días de penalización acumulados")
    fecha_finalizacion: date = Field(..., description="Fecha de finalización de la multa")

class MultaCreate(MultaBase):
    # La creación de multas se hará internamente por el sistema, no directamente por un endpoint POST.
    # Sin embargo, definimos un Create para consistencia en la lógica.
    pass

class Multa(MultaBase):
    id: int # El ID se genera en la base de datos
    # usuario: Usuario # Se podría incluir para anidar info del usuario

    class Config:
        from_attributes = True

# --- Esquemas para Recomendacion ---
class RecomendacionBase(BaseModel):
    id_libro_origen: int = Field(..., example=1, description="ID del libro origen de la recomendación")
    id_libro_recomendado: int = Field(..., example=2, description="ID del libro recomendado")
    comentario: Optional[str] = Field(None, example="Similar en temática y estilo.", max_length=255)

class RecomendacionCreate(RecomendacionBase):
    pass

class Recomendacion(RecomendacionBase):
    id: int # El ID se genera en la base de datos
    # libro_origen: Libro # Se podría incluir para anidar info del libro origen
    # libro_recomendado: Libro # Se podría incluir para anidar info del libro recomendado

    class Config:
        from_attributes = True

# --- Esquemas para Históricos ---
class PrestamoHistoricoBase(BaseModel):
    id_ejemplar: int = Field(..., description="ID del ejemplar prestado históricamente")
    id_usuario: int = Field(..., description="ID del usuario del préstamo histórico")
    fecha_prestamo: date = Field(..., description="Fecha en que se realizó el préstamo histórico")
    fecha_devolucion_esperada: date = Field(..., description="Fecha esperada de devolución del préstamo histórico")
    fecha_devolucion_real: date = Field(..., description="Fecha real de devolución del ejemplar")
    id_multa: Optional[int] = Field(None, description="ID de la multa asociada a este préstamo histórico (si aplica)")

class PrestamoHistoricoCreate(PrestamoHistoricoBase):
    pass

class PrestamoHistorico(PrestamoHistoricoBase):
    id: int # El ID se genera en la base de datos

    class Config:
        from_attributes = True

class MultaHistoricaBase(BaseModel):
    id_usuario: int = Field(..., description="ID del usuario de la multa histórica")
    fecha_inicio: date = Field(..., description="Fecha de inicio de la multa histórica")
    dias_acumulados: int = Field(..., description="Días acumulados de penalización de la multa histórica")
    fecha_finalizacion: date = Field(..., description="Fecha de finalización de la multa histórica")

class MultaHistoricaCreate(MultaHistoricaBase):
    pass

class MultaHistorica(MultaHistoricaBase):
    id: int # El ID se genera en la base de datos

    class Config:
        from_attributes = True