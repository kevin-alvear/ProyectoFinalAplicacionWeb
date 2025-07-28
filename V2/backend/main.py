from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Union, Optional
from datetime import date
from . import auth

from . import models, schemas, crud, database
from .auth import get_current_user  # Importa la dependencia de autenticación

app = FastAPI(
    title="API de Gestión de Biblioteca (Protegida por Keycloak)",
    description="API RESTful para la gestión de libros, ejemplares, usuarios, préstamos y multas en una biblioteca escolar.",
    version="1.0.0",
)

# --- NUEVO ENDPOINT DE LOGIN ---
@app.post("/login", tags=["Autenticación"])
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Recibe un usuario y contraseña y devuelve un token de acceso de Keycloak.
    """
    token_data = auth.get_token(username=form_data.username, password=form_data.password)
    return {"access_token": token_data['access_token'], "refresh_token": token_data['refresh_token'], "token_type": "bearer"}

# Crea todas las tablas en la base de datos (solo si no existen)
@app.on_event("startup")
def create_tables():
    print("Intentando crear tablas en la base de datos...")
    models.Base.metadata.create_all(bind=database.engine)
    print("Tablas creadas (o ya existentes) en PostgreSQL.")

# Dependency para obtener la sesión de la base de datos
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Endpoints para Libros (Protegidos) ---

@app.post("/libros/", response_model=schemas.Libro, status_code=status.HTTP_201_CREATED, tags=["Libros"])
def crear_libro(libro: schemas.LibroCreate, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    print(f"Petición para crear libro recibida del usuario: {usuario_actual.get('preferred_username')}")
    db_libro = crud.get_libro_by_isbn(db, isbn=libro.isbn)
    if db_libro:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un libro con este ISBN")
    try:
        return crud.create_libro(db=db, libro=libro)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Error de integridad: el ISBN ya existe.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/libros/", response_model=List[schemas.Libro], tags=["Libros"])
def leer_libros(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    libros = crud.get_libros(db, skip=skip, limit=limit)
    return libros

@app.get("/libros/{libro_id}", response_model=schemas.Libro, tags=["Libros"])
def leer_libro(libro_id: int, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_libro = crud.get_libro(db, libro_id=libro_id)
    if db_libro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    return db_libro

@app.put("/libros/{libro_id}", response_model=schemas.Libro, tags=["Libros"])
def actualizar_libro(libro_id: int, libro: schemas.LibroBase, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_libro = crud.get_libro(db, libro_id=libro_id)
    if db_libro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    if libro.isbn != db_libro.isbn:
        existing_isbn_libro = crud.get_libro_by_isbn(db, isbn=libro.isbn)
        if existing_isbn_libro:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nuevo ISBN ya está en uso por otro libro.")
    try:
        return crud.update_libro(db=db, db_libro=db_libro, libro_update=libro)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.delete("/libros/{libro_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Libros"])
def eliminar_libro(libro_id: int, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_libro = crud.get_libro(db, libro_id=libro_id)
    if db_libro is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    if db_libro.ejemplares:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede eliminar un libro con ejemplares asociados.")
    crud.delete_libro(db=db, db_libro=db_libro)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Endpoints para Ejemplares (Protegidos) ---

@app.post("/ejemplares/", response_model=schemas.Ejemplar, status_code=status.HTTP_201_CREATED, tags=["Ejemplares"])
def crear_ejemplar(ejemplar: schemas.EjemplarCreate, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_libro = crud.get_libro(db, libro_id=ejemplar.id_libro)
    if not db_libro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro al que pertenece el ejemplar no encontrado")
    db_ejemplar = crud.get_ejemplar_by_codigo(db, codigoEjemplar=ejemplar.codigoEjemplar)
    if db_ejemplar:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ya existe un ejemplar con este código.")
    try:
        return crud.create_ejemplar(db=db, ejemplar=ejemplar)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Error de integridad: el código de ejemplar ya existe.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/ejemplares/", response_model=List[schemas.Ejemplar], tags=["Ejemplares"])
def leer_ejemplares(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    ejemplares = crud.get_ejemplares(db, skip=skip, limit=limit)
    return ejemplares

@app.get("/ejemplares/{ejemplar_id}", response_model=schemas.Ejemplar, tags=["Ejemplares"])
def leer_ejemplar(ejemplar_id: int, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_ejemplar = crud.get_ejemplar(db, ejemplar_id=ejemplar_id)
    if db_ejemplar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ejemplar no encontrado")
    return db_ejemplar

@app.get("/libros/{libro_id}/ejemplares/", response_model=List[schemas.Ejemplar], tags=["Ejemplares"])
def leer_ejemplares_por_libro(libro_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_libro = crud.get_libro(db, libro_id=libro_id)
    if not db_libro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    ejemplares = crud.get_ejemplares_by_libro(db, libro_id=libro_id, skip=skip, limit=limit)
    return ejemplares

@app.put("/ejemplares/{ejemplar_id}", response_model=schemas.Ejemplar, tags=["Ejemplares"])
def actualizar_ejemplar(ejemplar_id: int, ejemplar: schemas.EjemplarBase, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_ejemplar = crud.get_ejemplar(db, ejemplar_id=ejemplar_id)
    if db_ejemplar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ejemplar no encontrado")
    if ejemplar.id_libro != db_ejemplar.id_libro:
        db_libro_new = crud.get_libro(db, libro_id=ejemplar.id_libro)
        if not db_libro_new:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nuevo libro para el ejemplar no encontrado.")
    if ejemplar.codigoEjemplar != db_ejemplar.codigoEjemplar:
        existing_ejemplar_codigo = crud.get_ejemplar_by_codigo(db, codigoEjemplar=ejemplar.codigoEjemplar)
        if existing_ejemplar_codigo:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nuevo código de ejemplar ya está en uso.")
    try:
        return crud.update_ejemplar(db=db, db_ejemplar=db_ejemplar, ejemplar_update=ejemplar)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.delete("/ejemplares/{ejemplar_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Ejemplares"])
def eliminar_ejemplar(ejemplar_id: int, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_ejemplar = crud.get_ejemplar(db, ejemplar_id=ejemplar_id)
    if db_ejemplar is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ejemplar no encontrado")
    if db_ejemplar.prestamo_activo:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede eliminar un ejemplar que está actualmente prestado.")
    crud.delete_ejemplar(db=db, db_ejemplar=db_ejemplar)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Endpoints para Usuarios (Protegidos) ---
# Nota: La creación de usuarios ahora debería hacerse en Keycloak.
# Estos endpoints sirven para gestionar el perfil del usuario en la base de datos local.

@app.post("/usuarios/profesor/", response_model=schemas.Profesor, status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
def crear_profesor(profesor: schemas.ProfesorCreate, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    # Idealmente, solo un admin podría crear perfiles de usuario locales.
    db_usuario = crud.get_usuario_by_login(db, login=profesor.login)
    if db_usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login ya registrado en la base de datos local")
    try:
        db_usuario = crud.create_usuario(db=db, usuario=profesor)
        return schemas.Profesor.model_validate(db_usuario)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Error de integridad: el login o email ya existen.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.post("/usuarios/alumno/", response_model=schemas.Alumno, status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
def crear_alumno(alumno: schemas.AlumnoCreate, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_usuario = crud.get_usuario_by_login(db, login=alumno.login)
    if db_usuario:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Login ya registrado en la base de datos local")
    try:
        db_usuario = crud.create_usuario(db=db, usuario=alumno)
        return schemas.Alumno.model_validate(db_usuario)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Error de integridad: el login o email ya existen.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/usuarios/", response_model=List[Union[schemas.Profesor, schemas.Alumno]], tags=["Usuarios"])
def leer_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    usuarios = crud.get_usuarios(db, skip=skip, limit=limit)
    response_users = []
    for user in usuarios:
        if user.tipo_usuario == "profesor":
            response_users.append(schemas.Profesor.model_validate(user))
        elif user.tipo_usuario == "alumno":
            response_users.append(schemas.Alumno.model_validate(user))
    return response_users

@app.get("/usuarios/{usuario_id}", response_model=Union[schemas.Profesor, schemas.Alumno], tags=["Usuarios"])
def leer_usuario(usuario_id: int, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_usuario = crud.get_usuario(db, usuario_id=usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    if db_usuario.tipo_usuario == "profesor":
        return schemas.Profesor.model_validate(db_usuario)
    elif db_usuario.tipo_usuario == "alumno":
        return schemas.Alumno.model_validate(db_usuario)
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Tipo de usuario desconocido")

@app.put("/usuarios/{usuario_id}", response_model=Union[schemas.Profesor, schemas.Alumno], tags=["Usuarios"])
def actualizar_usuario(usuario_id: int, usuario_update: Union[schemas.ProfesorCreate, schemas.AlumnoCreate], db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_usuario = crud.get_usuario(db, usuario_id=usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    if usuario_update.login != db_usuario.login:
        existing_login_user = crud.get_usuario_by_login(db, login=usuario_update.login)
        if existing_login_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nuevo login ya está en uso.")
    if usuario_update.email != db_usuario.email:
        existing_email_user = crud.get_usuario_by_email(db, email=usuario_update.email)
        if existing_email_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nuevo email ya está en uso.")
    try:
        updated_user = crud.update_usuario(db=db, db_usuario=db_usuario, usuario_update=usuario_update)
        if updated_user.tipo_usuario == "profesor":
            return schemas.Profesor.model_validate(updated_user)
        elif updated_user.tipo_usuario == "alumno":
            return schemas.Alumno.model_validate(updated_user)
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Tipo de usuario desconocido después de la actualización.")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Error de integridad al actualizar el usuario (login o email duplicado).")

@app.delete("/usuarios/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Usuarios"])
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_usuario = crud.get_usuario(db, usuario_id=usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    if db_usuario.prestamos_actuales:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede eliminar un usuario con préstamos activos.")
    if db_usuario.multa_actual:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede eliminar un usuario con una multa activa.")
    crud.delete_usuario(db=db, db_usuario=db_usuario)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Endpoints para Préstamos (Protegidos) ---

@app.post("/prestamos/", response_model=schemas.Prestamo, status_code=status.HTTP_201_CREATED, tags=["Préstamos"])
def crear_prestamo(prestamo: schemas.PrestamoCreate, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    try:
        db_prestamo = crud.create_prestamo(db=db, prestamo=prestamo)
        return db_prestamo
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Error de integridad: este ejemplar ya está prestado.")

@app.get("/prestamos/", response_model=List[schemas.Prestamo], tags=["Préstamos"])
def leer_prestamos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    prestamos = crud.get_prestamos(db, skip=skip, limit=limit)
    return prestamos

@app.get("/prestamos/{prestamo_id}", response_model=schemas.Prestamo, tags=["Préstamos"])
def leer_prestamo(prestamo_id: int, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_prestamo = crud.get_prestamo(db, prestamo_id=prestamo_id)
    if db_prestamo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo no encontrado")
    return db_prestamo

@app.delete("/prestamos/{prestamo_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Préstamos"])
def eliminar_prestamo(prestamo_id: int, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_prestamo = crud.get_prestamo(db, prestamo_id=prestamo_id)
    if db_prestamo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo no encontrado")
    crud.delete_prestamo(db=db, prestamo_id=prestamo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post("/ejemplares/{ejemplar_id}/devolver/", response_model=schemas.PrestamoHistorico, tags=["Préstamos"])
def devolver_ejemplar_api(ejemplar_id: int, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    try:
        db_prestamo_historico = crud.devolver_ejemplar(db, ejemplar_id=ejemplar_id)
        return db_prestamo_historico
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# --- Endpoints para Multas (Protegidos) ---

@app.get("/multas/{multa_id}", response_model=schemas.Multa, tags=["Multas"])
def leer_multa(multa_id: int, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_multa = crud.get_multa(db, multa_id=multa_id)
    if db_multa is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Multa no encontrada")
    return db_multa

@app.get("/usuarios/{usuario_id}/multa_activa/", response_model=Optional[schemas.Multa], tags=["Multas"])
def leer_multa_activa_usuario(usuario_id: int, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_usuario = crud.get_usuario(db, usuario_id=usuario_id)
    if not db_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    db_multa = crud.get_multa_by_usuario(db, usuario_id=usuario_id)
    if db_multa is None:
        return None
    return db_multa

@app.post("/multas/{multa_id}/resolver/", response_model=schemas.MultaHistorica, tags=["Multas"])
def resolver_multa_api(multa_id: int, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    try:
        db_multa_historica = crud.resolver_multa(db, multa_id=multa_id)
        if db_multa_historica is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Multa activa no encontrada para resolver")
        return db_multa_historica
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

# --- Endpoints para Recomendaciones (Protegidos) ---

@app.post("/recomendaciones/", response_model=schemas.Recomendacion, status_code=status.HTTP_201_CREATED, tags=["Recomendaciones"])
def crear_recomendacion(recomendacion: schemas.RecomendacionCreate, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    try:
        db_recomendacion = crud.create_recomendacion(db=db, recomendacion=recomendacion)
        return db_recomendacion
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Error de integridad al crear la recomendación.")

@app.get("/libros/{libro_id}/recomendaciones/", response_model=List[schemas.Recomendacion], tags=["Recomendaciones"])
def leer_recomendaciones_por_libro(libro_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_libro = crud.get_libro(db, libro_id=libro_id)
    if not db_libro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Libro no encontrado")
    recomendaciones = crud.get_recomendaciones_by_libro_origen(db, libro_id=libro_id, skip=skip, limit=limit)
    return recomendaciones

@app.delete("/recomendaciones/{recomendacion_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Recomendaciones"])
def eliminar_recomendacion(recomendacion_id: int, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_recomendacion = crud.get_recomendacion(db, recomendacion_id=recomendacion_id)
    if db_recomendacion is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recomendación no encontrada")
    crud.delete_recomendacion(db=db, db_recomendacion=db_recomendacion)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# --- Endpoints para Históricos (Protegidos) ---

@app.get("/historial/prestamos/{prestamo_historico_id}", response_model=schemas.PrestamoHistorico, tags=["Históricos"])
def leer_prestamo_historico(prestamo_historico_id: int, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_prestamo_historico = crud.get_prestamo_historico(db, prestamo_historico_id=prestamo_historico_id)
    if db_prestamo_historico is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Préstamo histórico no encontrado")
    return db_prestamo_historico

@app.get("/usuarios/{usuario_id}/historial/prestamos/", response_model=List[schemas.PrestamoHistorico], tags=["Históricos"])
def leer_historial_prestamos_usuario(usuario_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_usuario = crud.get_usuario(db, usuario_id=usuario_id)
    if not db_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    historial = crud.get_prestamos_historicos_by_usuario(db, usuario_id=usuario_id, skip=skip, limit=limit)
    return historial

@app.get("/historial/multas/{multa_historica_id}", response_model=schemas.MultaHistorica, tags=["Históricos"])
def leer_multa_historica(multa_historica_id: int, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_multa_historica = crud.get_multa_historica(db, multa_historica_id=multa_historica_id)
    if db_multa_historica is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Multa histórica no encontrada")
    return db_multa_historica

@app.get("/usuarios/{usuario_id}/historial/multas/", response_model=List[schemas.MultaHistorica], tags=["Históricos"])
def leer_historial_multas_usuario(usuario_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_current_user)):
    db_usuario = crud.get_usuario(db, usuario_id=usuario_id)
    if not db_usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    historial = crud.get_multas_historicas_by_usuario(db, usuario_id=usuario_id, skip=skip, limit=limit)
    return historial
