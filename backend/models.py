# library_project/backend/models.py
from sqlalchemy import Column, Integer, String, Date, ForeignKey, Enum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from datetime import date
import enum
from typing import Optional
# Define la base declarativa para tus modelos SQLAlchemy
Base = declarative_base()

# --- Enum para el estado del usuario (IRQ 2.5.3, punto 39) ---
class EstadoUsuario(str, enum.Enum):
    ACTIVO = "ACTIVO"
    MOROSO = "MOROSO"
    MULTADO = "MULTADO"

# --- Modelo para Libro (IRQ 2.5.3, punto 43) ---
class Libro(Base):
    __tablename__ = "libros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True) # IRQ 2.5.4, punto 92
    isbn: Mapped[str] = mapped_column(String, unique=True, index=True) # IRQ 2.5.3, punto 44
    titulo: Mapped[str] = mapped_column(String) # IRQ 2.5.3, punto 45
    autor: Mapped[str] = mapped_column(String) # IRQ 2.5.3, punto 45
    numPaginas: Mapped[int] = mapped_column(Integer) # IRQ 2.5.3, punto 46
    numEjemplares: Mapped[int] = mapped_column(Integer, default=0) # IRQ 2.5.3, punto 47
    numEjemplaresDisponibles: Mapped[int] = mapped_column(Integer, default=0) # IRQ 2.5.3, punto 48
    portadaURI: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relación uno a muchos con Ejemplar
    ejemplares: Mapped[list["Ejemplar"]] = relationship("Ejemplar", back_populates="libro")
    # Relación uno a muchos con Recomendacion (como libro origen)
    recomendaciones_origen: Mapped[list["Recomendacion"]] = relationship("Recomendacion", foreign_keys="[Recomendacion.id_libro_origen]", back_populates="libro_origen")
    # Relación uno a muchos con Recomendacion (como libro recomendado)
    recomendaciones_destino: Mapped[list["Recomendacion"]] = relationship("Recomendacion", foreign_keys="[Recomendacion.id_libro_recomendado]", back_populates="libro_recomendado")


# --- Modelo para Ejemplar (IRQ 2.5.3, punto 52) ---
class Ejemplar(Base):
    __tablename__ = "ejemplares"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True) # IRQ 2.5.4, punto 92
    id_libro: Mapped[int] = mapped_column(Integer, ForeignKey("libros.id")) # IRQ 2.5.3, punto 54
    codigoEjemplar: Mapped[str] = mapped_column(String, unique=True, index=True) # IRQ 2.5.3, punto 53
    adquiridoEl: Mapped[date] = mapped_column(Date, default=date.today) # IRQ 2.5.3, punto 55
    observaciones: Mapped[str] = mapped_column(String, nullable=True) # IRQ 2.5.3, punto 56

    # Relación muchos a uno con Libro
    libro: Mapped["Libro"] = relationship("Libro", back_populates="ejemplares")
    # Relación uno a uno con Prestamo (un ejemplar puede tener un préstamo activo)
    prestamo_activo: Mapped[Optional["Prestamo"]] = relationship("Prestamo", back_populates="ejemplar_rel", uselist=False)
    # Relación uno a muchos con PrestamoHistorico
    prestamos_historicos: Mapped[list["PrestamoHistorico"]] = relationship("PrestamoHistorico", back_populates="ejemplar_rel")


# --- Modelo para Usuario (Base) (IRQ 2.5.3, punto 29) ---
class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True) # IRQ 2.5.4, punto 92
    login: Mapped[str] = mapped_column(String, unique=True, index=True) # IRQ 2.5.3, punto 31
    #password: Mapped[str] = mapped_column(String) # IRQ 2.5.3, punto 31 (Nota: se almacenaría hash, no texto plano)
    nombre: Mapped[str] = mapped_column(String) # IRQ 2.5.3, punto 32
    apellidos: Mapped[str] = mapped_column(String) # IRQ 2.5.3, punto 32
    email: Mapped[str] = mapped_column(String, unique=True, index=True) # IRQ 2.5.3, punto 33
    calle: Mapped[str] = mapped_column(String) # IRQ 2.5.3, punto 36
    numero: Mapped[str] = mapped_column(String) # IRQ 2.5.3, punto 36
    piso: Mapped[str] = mapped_column(String, nullable=True) # IRQ 2.5.3, punto 36
    ciudad: Mapped[str] = mapped_column(String) # IRQ 2.5.3, punto 36
    codigo_postal: Mapped[str] = mapped_column(String) # IRQ 2.5.3, punto 36
    tipo_usuario: Mapped[str] = mapped_column(String) # Para la herencia (Profesor o Alumno)
    estado: Mapped[EstadoUsuario] = mapped_column(Enum(EstadoUsuario), default=EstadoUsuario.ACTIVO) # IRQ 2.5.3, punto 39

    # Relaciones
    prestamos_actuales: Mapped[list["Prestamo"]] = relationship("Prestamo", back_populates="usuario_rel") # IRQ 2.5.3, punto 34
    multa_actual: Mapped[Optional["Multa"]] = relationship("Multa", back_populates="usuario_rel", uselist=False) # IRQ 2.5.3, punto 35
    prestamos_historicos: Mapped[list["PrestamoHistorico"]] = relationship("PrestamoHistorico", back_populates="usuario_rel")
    multas_historicas: Mapped[list["MultaHistorica"]] = relationship("MultaHistorica", back_populates="usuario_rel")

    __mapper_args__ = {
        "polymorphic_identity": "usuario",
        "polymorphic_on": tipo_usuario,
    }

# --- Modelos para Profesor (Herencia de Usuario) (IRQ 2.5.3, punto 38) ---
class Profesor(Usuario):
    __tablename__ = "profesores" # Aunque hereda, se puede usar para uniones en consultas si se desea

    id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    departamento: Mapped[str] = mapped_column(String) # IRQ 2.5.3, punto 38

    __mapper_args__ = {
        "polymorphic_identity": "profesor",
    }

# --- Modelos para Alumno (Herencia de Usuario) (IRQ 2.5.3, punto 37) ---
class Alumno(Usuario):
    __tablename__ = "alumnos" # Aunque hereda, se puede usar para uniones en consultas si se desea

    id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), primary_key=True)
    telefono_padres: Mapped[str] = mapped_column(String) # IRQ 2.5.3, punto 37

    __mapper_args__ = {
        "polymorphic_identity": "alumno",
    }


# --- Modelo para Préstamo (activo) (IRQ 2.5.3, punto 57) ---
class Prestamo(Base):
    __tablename__ = "prestamos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True) # IRQ 2.5.4, punto 92
    id_ejemplar: Mapped[int] = mapped_column(Integer, ForeignKey("ejemplares.id"), unique=True) # Un ejemplar solo puede estar prestado una vez activamente
    id_usuario: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id")) #
    fecha_prestamo: Mapped[date] = mapped_column(Date, default=date.today) # IRQ 2.5.3, punto 59
    fecha_devolucion_esperada: Mapped[date] = mapped_column(Date) # IRQ 2.5.3, punto 59

    # Relaciones
    ejemplar_rel: Mapped["Ejemplar"] = relationship("Ejemplar", back_populates="prestamo_activo")
    usuario_rel: Mapped["Usuario"] = relationship("Usuario", back_populates="prestamos_actuales")


# --- Modelo para Multa (activa) (IRQ 2.5.3, punto 60) ---
class Multa(Base):
    __tablename__ = "multas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True) # IRQ 2.5.4, punto 92
    id_usuario: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), unique=True) # Un usuario solo puede tener una multa activa a la vez
    fecha_inicio: Mapped[date] = mapped_column(Date, default=date.today) # IRQ 2.5.3, punto 63
    dias_acumulados: Mapped[int] = mapped_column(Integer, default=0) # IRQ 2.5.3, punto 64
    fecha_finalizacion: Mapped[date] = mapped_column(Date) # IRQ 2.5.3, punto 65

    # Relación
    usuario_rel: Mapped["Usuario"] = relationship("Usuario", back_populates="multa_actual")


# --- Modelo para Recomendacion (IRQ 2.5.3, punto 50) ---
class Recomendacion(Base):
    __tablename__ = "recomendaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True) # IRQ 2.5.4, punto 92
    id_libro_origen: Mapped[int] = mapped_column(Integer, ForeignKey("libros.id"))
    id_libro_recomendado: Mapped[int] = mapped_column(Integer, ForeignKey("libros.id"))
    comentario: Mapped[str] = mapped_column(String, nullable=True) # IRQ 2.5.3, punto 51

    # Relaciones
    libro_origen: Mapped["Libro"] = relationship("Libro", foreign_keys=[id_libro_origen], back_populates="recomendaciones_origen")
    libro_recomendado: Mapped["Libro"] = relationship("Libro", foreign_keys=[id_libro_recomendado], back_populates="recomendaciones_destino")


# --- Modelo para Préstamo Histórico (IRQ 2.5.3, punto 66) ---
class PrestamoHistorico(Base):
    __tablename__ = "prestamos_historicos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True) # IRQ 2.5.4, punto 92
    id_ejemplar: Mapped[int] = mapped_column(Integer, ForeignKey("ejemplares.id")) # IRQ 2.5.3, punto 67
    id_usuario: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id")) # IRQ 2.5.3, punto 67
    fecha_prestamo: Mapped[date] = mapped_column(Date)
    fecha_devolucion_esperada: Mapped[date] = mapped_column(Date)
    fecha_devolucion_real: Mapped[date] = mapped_column(Date) # IRQ 2.5.3, punto 68
    id_multa: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("multas_historicas.id"), nullable=True) # IRQ 2.5.3, punto 67

    # Relaciones
    ejemplar_rel: Mapped["Ejemplar"] = relationship("Ejemplar", back_populates="prestamos_historicos")
    usuario_rel: Mapped["Usuario"] = relationship("Usuario", back_populates="prestamos_historicos")
    multa_rel: Mapped[Optional["MultaHistorica"]] = relationship("MultaHistorica", back_populates="prestamos_historicos_rel")


# --- Modelo para Multa Histórica (IRQ 2.5.3, punto 66) ---
class MultaHistorica(Base):
    __tablename__ = "multas_historicas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True) # IRQ 2.5.4, punto 92
    id_usuario: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id")) # IRQ 2.5.3, punto 67
    fecha_inicio: Mapped[date] = mapped_column(Date)
    dias_acumulados: Mapped[int] = mapped_column(Integer)
    fecha_finalizacion: Mapped[date] = mapped_column(Date)

    # Relaciones
    usuario_rel: Mapped["Usuario"] = relationship("Usuario", back_populates="multas_historicas")
    prestamos_historicos_rel: Mapped[list["PrestamoHistorico"]] = relationship("PrestamoHistorico", back_populates="multa_rel")