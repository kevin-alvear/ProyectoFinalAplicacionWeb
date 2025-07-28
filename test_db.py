import psycopg2

try:
    conn = psycopg2.connect(
        dbname="librarydb",
        user="postgres",
        password="admin",
        host="localhost",
        port="5433"
    )
    print("Conexión exitosa")
    conn.close()
except Exception as e:
    print("Error al conectar:", e)
