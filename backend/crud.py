from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models, schemas
from typing import List, Optional, Union
from datetime import date, timedelta

# --- CRUD para Libros ---

def get_libro(db: Session, libro_id: int):
    return db.query(models.Libro).filter(models.Libro.id == libro_id).first()

def get_libro_by_isbn(db: Session, isbn: str):
    return db.query(models.Libro).filter(models.Libro.isbn == isbn).first()

def get_libros(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Libro).offset(skip).limit(limit).all()

def create_libro(db: Session, libro: schemas.LibroCreate):
    db_libro = models.Libro(
        isbn=libro.isbn,
        titulo=libro.titulo,
        autor=libro.autor,
        numPaginas=libro.numPaginas,
        numEjemplares=libro.numEjemplares,
        numEjemplaresDisponibles=libro.numEjemplares, # Inicialmente, todos los ejemplares están disponibles
        portadaURI=libro.portadaURI
    )
    db.add(db_libro)
    db.commit()
    db.refresh(db_libro)
    return db_libro

def update_libro(db: Session, db_libro: models.Libro, libro_update: schemas.LibroBase):
    for key, value in libro_update.model_dump(exclude_unset=True).items():
        setattr(db_libro, key, value)
    db.add(db_libro)
    db.commit()
    db.refresh(db_libro)
    return db_libro

def delete_libro(db: Session, db_libro: models.Libro):
    # Asegúrate de que no haya ejemplares asociados (la verificación se hace en el endpoint)
    db.delete(db_libro)
    db.commit()


# --- CRUD para Ejemplares ---

def get_ejemplar(db: Session, ejemplar_id: int):
    return db.query(models.Ejemplar).filter(models.Ejemplar.id == ejemplar_id).first()

def get_ejemplar_by_codigo(db: Session, codigoEjemplar: str):
    return db.query(models.Ejemplar).filter(models.Ejemplar.codigoEjemplar == codigoEjemplar).first()

def get_ejemplares(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Ejemplar).offset(skip).limit(limit).all()

def get_ejemplares_by_libro(db: Session, libro_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Ejemplar).filter(models.Ejemplar.id_libro == libro_id).offset(skip).limit(limit).all()

def create_ejemplar(db: Session, ejemplar: schemas.EjemplarCreate):
    db_ejemplar = models.Ejemplar(
        id_libro=ejemplar.id_libro,
        codigoEjemplar=ejemplar.codigoEjemplar,
        adquiridoEl=ejemplar.adquiridoEl,
        observaciones=ejemplar.observaciones
    )
    db.add(db_ejemplar)
    # También debemos incrementar el numEjemplares y numEjemplaresDisponibles del libro asociado
    db_libro = get_libro(db, ejemplar.id_libro)
    if db_libro:
        db_libro.numEjemplares += 1
        db_libro.numEjemplaresDisponibles += 1
    db.commit()
    db.refresh(db_ejemplar)
    if db_libro:
        db.refresh(db_libro)
    return db_ejemplar

def update_ejemplar(db: Session, db_ejemplar: models.Ejemplar, ejemplar_update: schemas.EjemplarBase):
    # Si se cambia el libro asociado, ajustar contadores del libro antiguo y nuevo
    original_id_libro = db_ejemplar.id_libro
    updated_id_libro = ejemplar_update.id_libro

    for key, value in ejemplar_update.model_dump(exclude_unset=True).items():
        setattr(db_ejemplar, key, value)
    
    # Manejar cambios en el id_libro
    if updated_id_libro is not None and updated_id_libro != original_id_libro:
        # Decrementar del libro antiguo
        old_libro = get_libro(db, original_id_libro)
        if old_libro:
            old_libro.numEjemplares -= 1
            # Cuidado: solo decrementa disponibles si el ejemplar NO estaba prestado
            if not db_ejemplar.prestamo_activo: # Si el ejemplar no está prestado actualmente
                old_libro.numEjemplaresDisponibles -= 1
            db.add(old_libro) # Marcar para guardar cambios

        # Incrementar en el libro nuevo
        new_libro = get_libro(db, updated_id_libro)
        if new_libro:
            new_libro.numEjemplares += 1
            # Cuidado: solo incrementa disponibles si el ejemplar NO estaba prestado
            if not db_ejemplar.prestamo_activo:
                new_libro.numEjemplaresDisponibles += 1
            db.add(new_libro) # Marcar para guardar cambios

    db.add(db_ejemplar)
    db.commit()
    db.refresh(db_ejemplar)
    # Refrescar los libros si se modificaron
    if updated_id_libro is not None and updated_id_libro != original_id_libro:
        if old_libro: db.refresh(old_libro)
        if new_libro: db.refresh(new_libro)
    return db_ejemplar

def delete_ejemplar(db: Session, db_ejemplar: models.Ejemplar):
    # Asegúrate de que no haya préstamos activos (la verificación se hace en el endpoint)
    # Decrementar numEjemplares y numEjemplaresDisponibles del libro asociado
    db_libro = get_libro(db, db_ejemplar.id_libro)
    if db_libro:
        db_libro.numEjemplares -= 1
        if not db_ejemplar.prestamo_activo: # Solo si no está prestado, estaba disponible
            db_libro.numEjemplaresDisponibles -= 1
        db.add(db_libro) # Marcar el libro para guardar cambios
        
    db.delete(db_ejemplar)
    db.commit()
    if db_libro:
        db.refresh(db_libro) # Refrescar libro para reflejar cambios
    return db_ejemplar


# --- CRUD para Usuarios ---

def get_usuario(db: Session, usuario_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

def get_usuario_by_login(db: Session, login: str):
    return db.query(models.Usuario).filter(models.Usuario.login == login).first()

def get_usuario_by_email(db: Session, email: str):
    return db.query(models.Usuario).filter(models.Usuario.email == email).first()

def get_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).offset(skip).limit(limit).all()

def create_usuario(db: Session, usuario: Union[schemas.ProfesorCreate, schemas.AlumnoCreate]):
    # Aquí es donde diferenciamos entre Profesor y Alumno
    if isinstance(usuario, schemas.ProfesorCreate):
        db_usuario = models.Profesor(
            login=usuario.login,
            #password=usuario.password, # ¡Recuerda hashear en un entorno real!
            nombre=usuario.nombre,
            apellidos=usuario.apellidos,
            email=usuario.email,
            calle=usuario.calle,
            numero=usuario.numero,
            piso=usuario.piso,
            ciudad=usuario.ciudad,
            codigo_postal=usuario.codigo_postal,
            estado=usuario.estado,
            departamento=usuario.departamento
        )
    elif isinstance(usuario, schemas.AlumnoCreate):
        db_usuario = models.Alumno(
            login=usuario.login,
            #password=usuario.password, # ¡Recuerda hashear en un entorno real!
            nombre=usuario.nombre,
            apellidos=usuario.apellidos,
            email=usuario.email,
            calle=usuario.calle,
            numero=usuario.numero,
            piso=usuario.piso,
            ciudad=usuario.ciudad,
            codigo_postal=usuario.codigo_postal,
            estado=usuario.estado,
            telefono_padres=usuario.telefono_padres
        )
    else:
        raise ValueError("Tipo de usuario no reconocido")

    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def update_usuario(db: Session, db_usuario: models.Usuario, usuario_update: Union[schemas.ProfesorCreate, schemas.AlumnoCreate]):
    # Usa model_dump(exclude_unset=True) para actualizar solo los campos proporcionados
    update_data = usuario_update.model_dump(exclude_unset=True)

    # Si se actualiza un profesor, asegúrate de que el modelo sea Profesor
    if isinstance(db_usuario, models.Profesor) and "departamento" in update_data:
        db_usuario.departamento = update_data["departamento"]
    # Si se actualiza un alumno, asegúrate de que el modelo sea Alumno
    elif isinstance(db_usuario, models.Alumno) and "telefono_padres" in update_data:
        db_usuario.telefono_padres = update_data["telefono_padres"]
    
    # Actualizar campos comunes
    for key, value in update_data.items():
        if key not in ["departamento", "telefono_padres"]: # Evitar reasignar si ya se hizo para subtipo
            setattr(db_usuario, key, value)
    
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

def delete_usuario(db: Session, db_usuario: models.Usuario):
    # La verificación de préstamos/multas activas se hace en el endpoint
    db.delete(db_usuario)
    db.commit()

# --- CRUD para Préstamos ---

def get_prestamo(db: Session, prestamo_id: int):
    return db.query(models.Prestamo).filter(models.Prestamo.id == prestamo_id).first()

def get_prestamos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Prestamo).offset(skip).limit(limit).all()

def get_prestamos_by_usuario(db: Session, usuario_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Prestamo).filter(models.Prestamo.id_usuario == usuario_id).offset(skip).limit(limit).all()

def get_prestamo_by_ejemplar(db: Session, ejemplar_id: int):
    # Un ejemplar solo puede tener un préstamo activo
    return db.query(models.Prestamo).filter(models.Prestamo.id_ejemplar == ejemplar_id).first()

def create_prestamo(db: Session, prestamo: schemas.PrestamoCreate):
    db_ejemplar = get_ejemplar(db, prestamo.id_ejemplar)
    db_libro = get_libro(db, db_ejemplar.id_libro) if db_ejemplar else None # Mejor cargar con join si se puede
    db_usuario = get_usuario(db, prestamo.id_usuario)

    if not db_ejemplar or not db_libro or not db_usuario:
        raise ValueError("Ejemplar, libro o usuario no encontrado.")
    if db_ejemplar.prestamo_activo:
        raise ValueError("Este ejemplar ya está prestado.")
    if db_libro.numEjemplaresDisponibles <= 0:
        raise ValueError("No hay ejemplares disponibles de este libro.")
    if db_usuario.estado != schemas.EstadoUsuario.ACTIVO:
        raise ValueError(f"El usuario no puede realizar préstamos, su estado es {db_usuario.estado.value}.")

    # --- Lógica de Límite de Préstamos por Usuario (CRQ 2.5.5) ---
    num_prestamos_actuales = db.query(models.Prestamo).filter(models.Prestamo.id_usuario == db_usuario.id).count()

    max_prestamos = 0
    if db_usuario.tipo_usuario == "alumno":
        max_prestamos = 5
    elif db_usuario.tipo_usuario == "profesor":
        max_prestamos = 8
    
    if num_prestamos_actuales >= max_prestamos:
        raise ValueError(f"El usuario ya tiene el máximo de {max_prestamos} libros prestados.")
    # --- FIN Lógica de Límite de Préstamos por Usuario ---

    # Lógica para determinar fecha_devolucion_esperada (ej. 15 días, o más para profesor)
    if not prestamo.fecha_devolucion_esperada: # Si no se especifica, calcular
        if db_usuario.tipo_usuario == "profesor":
            dias_prestamo = 30 # 30 días para profesores (IRQ 2.5.3, punto 40)
        else: # alumno
            dias_prestamo = 7 # 7 días para alumnos (IRQ 2.5.3, punto 40)
        fecha_devolucion_esperada = date.today() + timedelta(days=dias_prestamo)
    else:
        # Si se proporciona, usarla (aunque el requisito dice que el sistema lo calcula)
        # Esto permite flexibilidad, pero puedes eliminar el else y siempre calcularla.
        fecha_devolucion_esperada = prestamo.fecha_devolucion_esperada

    db_prestamo = models.Prestamo(
        id_ejemplar=prestamo.id_ejemplar,
        id_usuario=prestamo.id_usuario,
        fecha_prestamo=date.today(),
        fecha_devolucion_esperada=fecha_devolucion_esperada
    )
    db.add(db_prestamo)

    # Actualizar disponibilidad del libro
    db_libro.numEjemplaresDisponibles -= 1
    db.commit()
    db.refresh(db_prestamo)
    db.refresh(db_libro) # Refrescar el libro para reflejar el cambio en disponibles
    return db_prestamo

def delete_prestamo(db: Session, prestamo_id: int):
    db_prestamo = db.query(models.Prestamo).filter(models.Prestamo.id == prestamo_id).first()
    if not db_prestamo:
        return None # Dejar que el endpoint maneje el 404
    
    # Decrementar numEjemplaresDisponibles al eliminar el préstamo activo (solo si se eliminó, no si se devolvió)
    # Esta función delete_prestamo se usaría para "deshacer" un préstamo, no para la devolución normal.
    # En la devolución normal, ya se maneja el numEjemplaresDisponibles.
    db_ejemplar = get_ejemplar(db, db_prestamo.id_ejemplar)
    if db_ejemplar and db_ejemplar.libro: # Acceder a la relación cargada
        db_ejemplar.libro.numEjemplaresDisponibles += 1
        db.add(db_ejemplar.libro) # Marcar el libro para guardar cambios

    db.delete(db_prestamo)
    db.commit()
    if db_ejemplar and db_ejemplar.libro:
        db.refresh(db_ejemplar.libro)
    return db_prestamo


# --- CRUD para Multas ---

def get_multa(db: Session, multa_id: int):
    return db.query(models.Multa).filter(models.Multa.id == multa_id).first()

def get_multa_by_usuario(db: Session, usuario_id: int):
    # Un usuario solo puede tener una multa activa a la vez
    return db.query(models.Multa).filter(models.Multa.id_usuario == usuario_id).first()

def create_multa(db: Session, multa: schemas.MultaCreate):
    db_multa = models.Multa(
        id_usuario=multa.id_usuario,
        fecha_inicio=multa.fecha_inicio,
        dias_acumulados=multa.dias_acumulados,
        fecha_finalizacion=multa.fecha_finalizacion
    )
    db.add(db_multa)
    # Actualizar el estado del usuario a "Multado"
    db_usuario = get_usuario(db, multa.id_usuario)
    if db_usuario:
        db_usuario.estado = schemas.EstadoUsuario.MULTADO
    db.commit()
    db.refresh(db_multa)
    if db_usuario:
        db.refresh(db_usuario)
    return db_multa

def resolver_multa(db: Session, multa_id: int):
    db_multa = get_multa(db, multa_id)
    if not db_multa:
        return None
    
    db_usuario = get_usuario(db, db_multa.id_usuario)
    
    # Crear un registro histórico de la multa
    db_multa_historica = models.MultaHistorica(
        id_usuario=db_multa.id_usuario,
        fecha_inicio=db_multa.fecha_inicio,
        dias_acumulados=db_multa.dias_acumulados,
        fecha_finalizacion=db_multa.fecha_finalizacion
    )
    db.add(db_multa_historica)
    db.flush() # Flush para que db_multa_historica.id esté disponible

    # Eliminar la multa activa
    db.delete(db_multa)
    
    # Actualizar el estado del usuario a "Activo" (o "Moroso" si hay otros factores)
    if db_usuario:
        # Si un usuario tiene múltiples préstamos atrasados y solo resuelve una multa,
        # podría seguir siendo moroso. Para simplificar, asumimos que al resolver la
        # multa, su estado vuelve a ACTIVO. Un sistema más complejo podría re-evaluar.
        db_usuario.estado = schemas.EstadoUsuario.ACTIVO
        db.refresh(db_usuario)

    db.commit()
    db.refresh(db_multa_historica)
    return db_multa_historica


# --- CRUD para Recomendaciones ---

def get_recomendacion(db: Session, recomendacion_id: int):
    return db.query(models.Recomendacion).filter(models.Recomendacion.id == recomendacion_id).first()

def get_recomendaciones_by_libro_origen(db: Session, libro_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Recomendacion).filter(models.Recomendacion.id_libro_origen == libro_id).offset(skip).limit(limit).all()

def get_recomendaciones_by_libro_recomendado(db: Session, libro_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Recomendacion).filter(models.Recomendacion.id_libro_recomendado == libro_id).offset(skip).limit(limit).all()

def create_recomendacion(db: Session, recomendacion: schemas.RecomendacionCreate):
    # Asegurarse de que los libros existan
    libro_origen = get_libro(db, recomendacion.id_libro_origen)
    libro_recomendado = get_libro(db, recomendacion.id_libro_recomendado)
    if not libro_origen or not libro_recomendado:
        raise ValueError("Libro origen o libro recomendado no encontrado.")
    if recomendacion.id_libro_origen == recomendacion.id_libro_recomendado:
        raise ValueError("Un libro no puede recomendarse a sí mismo.")

    db_recomendacion = models.Recomendacion(
        id_libro_origen=recomendacion.id_libro_origen,
        id_libro_recomendado=recomendacion.id_libro_recomendado,
        comentario=recomendacion.comentario
    )
    db.add(db_recomendacion)
    db.commit()
    db.refresh(db_recomendacion)
    return db_recomendacion

def delete_recomendacion(db: Session, db_recomendacion: models.Recomendacion):
    db.delete(db_recomendacion)
    db.commit()
    return db_recomendacion # Retorna el objeto eliminado (opcional)


# --- CRUD para Préstamos Históricos ---

def get_prestamo_historico(db: Session, prestamo_historico_id: int):
    return db.query(models.PrestamoHistorico).filter(models.PrestamoHistorico.id == prestamo_historico_id).first()

def get_prestamos_historicos_by_usuario(db: Session, usuario_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.PrestamoHistorico).filter(models.PrestamoHistorico.id_usuario == usuario_id).offset(skip).limit(limit).all()

def get_prestamos_historicos_by_ejemplar(db: Session, ejemplar_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.PrestamoHistorico).filter(models.PrestamoHistorico.id_ejemplar == ejemplar_id).offset(skip).limit(limit).all()

def create_prestamo_historico(db: Session, prestamo_historico: schemas.PrestamoHistoricoCreate):
    db_prestamo_historico = models.PrestamoHistorico(
        id_ejemplar=prestamo_historico.id_ejemplar,
        id_usuario=prestamo_historico.id_usuario,
        fecha_prestamo=prestamo_historico.fecha_prestamo,
        fecha_devolucion_esperada=prestamo_historico.fecha_devolucion_esperada,
        fecha_devolucion_real=prestamo_historico.fecha_devolucion_real,
        id_multa=prestamo_historico.id_multa
    )
    db.add(db_prestamo_historico)
    db.commit()
    db.refresh(db_prestamo_historico)
    return db_prestamo_historico

# --- CRUD para Multas Históricas ---

def get_multa_historica(db: Session, multa_historica_id: int):
    return db.query(models.MultaHistorica).filter(models.MultaHistorica.id == multa_historica_id).first()

def get_multas_historicas_by_usuario(db: Session, usuario_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.MultaHistorica).filter(models.MultaHistorica.id_usuario == usuario_id).offset(skip).limit(limit).all()

def create_multa_historica(db: Session, multa_historica: schemas.MultaHistoricaCreate):
    db_multa_historica = models.MultaHistorica(
        id_usuario=multa_historica.id_usuario,
        fecha_inicio=multa_historica.fecha_inicio,
        dias_acumulados=multa_historica.dias_acumulados,
        fecha_finalizacion=multa_historica.fecha_finalizacion
    )
    db.add(db_multa_historica)
    db.commit()
    db.refresh(db_multa_historica)
    return db_multa_historica

# --- Funciones de lógica de negocio adicionales (ej. Devolución de ejemplar) ---

def devolver_ejemplar(db: Session, ejemplar_id: int):
    db_prestamo = get_prestamo_by_ejemplar(db, ejemplar_id)
    if not db_prestamo:
        raise ValueError("Este ejemplar no está actualmente prestado.")

    db_usuario = get_usuario(db, db_prestamo.id_usuario)
    db_ejemplar = get_ejemplar(db, ejemplar_id)
    db_libro = get_libro(db, db_ejemplar.id_libro) if db_ejemplar else None

    if not db_usuario or not db_ejemplar or not db_libro:
        raise ValueError("Error interno: usuario, ejemplar o libro no encontrado durante la devolución.")

    fecha_devolucion_real = date.today()
    dias_atraso = (fecha_devolucion_real - db_prestamo.fecha_devolucion_esperada).days
    
    multa_id = None
    if dias_atraso > 0:
        # Calcular o crear multa
        db_multa_activa = get_multa_by_usuario(db, db_usuario.id)
        if db_multa_activa:
            # Si ya tiene una multa activa, acumular días
            db_multa_activa.dias_acumulados += dias_atraso
            db_multa_activa.fecha_finalizacion = fecha_devolucion_real + timedelta(days=db_multa_activa.dias_acumulados)
            db.add(db_multa_activa)
        else:
            # Crear nueva multa
            nueva_multa_data = schemas.MultaCreate(
                id_usuario=db_usuario.id,
                fecha_inicio=fecha_devolucion_real,
                dias_acumulados=dias_atraso,
                fecha_finalizacion=fecha_devolucion_real + timedelta(days=dias_atraso)
            )
            db_multa_activa = create_multa(db, nueva_multa_data) # Esta función ya actualiza el estado del usuario

        multa_id = db_multa_activa.id # Guardar el ID de la multa para el histórico del préstamo
    
    # Registrar el préstamo en el histórico
    db_prestamo_historico = models.PrestamoHistorico(
        id_ejemplar=db_prestamo.id_ejemplar,
        id_usuario=db_prestamo.id_usuario,
        fecha_prestamo=db_prestamo.fecha_prestamo,
        fecha_devolucion_esperada=db_prestamo.fecha_devolucion_esperada,
        fecha_devolucion_real=fecha_devolucion_real,
        id_multa=multa_id
    )
    db.add(db_prestamo_historico)

    # Eliminar el préstamo activo
    db.delete(db_prestamo)

    # Actualizar disponibilidad del libro
    db_libro.numEjemplaresDisponibles += 1
    
    db.commit()
    db.refresh(db_prestamo_historico)
    db.refresh(db_libro)
    db.refresh(db_usuario) # Refrescar el usuario para ver su estado actual (Multado o Activo)
    return db_prestamo_historico