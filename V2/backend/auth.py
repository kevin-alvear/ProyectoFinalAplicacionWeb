# library_project/backend/auth.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError
import jwt

# --- Configuración de Keycloak ---
KEYCLOAK_SERVER_URL = "http://keycloak:8080/"
KEYCLOAK_REALM = "master"
KEYCLOAK_CLIENT_ID = "fastapi-client"
# ¡IMPORTANTE! Necesitamos el secreto del cliente para obtener tokens.
# Búscalo en Keycloak -> Clients -> fastapi-client -> Credentials -> Client secret
KEYCLOAK_CLIENT_SECRET = "ytj93gqzZp7hErvDhOyvyUe2dxxaKz6F" # Reemplaza con tu secreto real

# --- Instancia de KeycloakOpenID ---
# Este único objeto se encargará tanto de obtener tokens como de validarlos.
keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_SERVER_URL,
    client_id=KEYCLOAK_CLIENT_ID,
    realm_name=KEYCLOAK_REALM,
    client_secret_key=KEYCLOAK_CLIENT_SECRET,
    verify=True
)

# Esquema de seguridad para la UI de FastAPI
oauth2_scheme = HTTPBearer()

# --- Funciones de Autenticación ---

def get_token(username, password) -> dict:
    """
    Obtiene un token de acceso de Keycloak para el usuario y contraseña proporcionados.
    """
    try:
        # La función .token() usa internamente el client_id y client_secret que ya configuramos.
        token = keycloak_openid.token(username=username, password=password)
        return token
    except KeycloakAuthenticationError as e:
        # Captura específicamente errores de autenticación (ej. usuario/pass incorrecto)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Credenciales inválidas: {e.error_description}",
        )
    except Exception as e:
        # Captura otros errores (ej. no se puede conectar a Keycloak)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de conexión con el servidor de autenticación: {e}",
        )

async def get_current_user(cred: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> dict:
    """
    Extrae el token del 'Bearer' y lo valida usando el endpoint de introspección de Keycloak.
    Este método es inmune a problemas de desfase de reloj.
    """
    token = cred.credentials
    try:
        # Usamos el endpoint de introspección. Keycloak nos dirá si el token es activo.
        token_info = keycloak_openid.introspect(token)

        if not token_info.get("active"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o inactivo",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Si el token es activo, devolvemos la información.
        # Podemos decodificarlo localmente (sin verificar la firma de tiempo) para obtener los claims.
        payload = jwt.decode(token, options={"verify_signature": False, "verify_aud": False})
        return payload

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido o error de validación: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
