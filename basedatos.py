import sqlite3



## Funciones para manipular la base de datos


def crear_conexion ():
    base_datos = sqlite3.connect('integracion.db')
    cursor = base_datos.cursor()
    return base_datos, cursor


def cerrar_conexion (conexion: sqlite3.Connection):
    conexion.commit()
    conexion.close()





def incializar_db ():
    conexion, cursor = crear_conexion()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sistema (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL,
        sede TEXT,
        dispositivo TEXT,
        ip TEXT,
        html TEXT NOT NULL
    );
    ''')

    cerrar_conexion(conexion)





def guardar_resultados (fecha, sede, dispositivo, ip, html):
    conexion, cursor = crear_conexion()
    
    cursor.execute(
        '''
        INSERT INTO sistema (fecha, sede, dispositivo, ip , html) 
        VALUES (?, ?, ?, ?, ?)''',
        (fecha, sede, dispositivo, ip, html)
        )

    cerrar_conexion(conexion)





def obtener_todos ():
    conexion, cursor = crear_conexion()
    cursor.execute("SELECT * FROM sistema")

    datos = cursor.fetchall()
    cerrar_conexion(conexion)

    return datos

    

def eliminar_datos_fecha_superior ():
    conexion, cursor = crear_conexion()

    cursor.execute('''
        DELETE FROM usuarios
        WHERE fecha < datetime('now', '-3 months')
    ''')

    cerrar_conexion(conexion)




def datos_pdf ():
    conexion, cursor = crear_conexion()

    cursor.execute("SELECT fecha, dispositivo, ip, html FROM sistema ORDER BY fecha DESC LIMIT 10")
    registros = cursor.fetchall()

    cerrar_conexion(conexion)

    return registros