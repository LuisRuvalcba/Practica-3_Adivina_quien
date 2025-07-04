import sqlite3

# Conectar a la base de datos o crearla si no existe
conn = sqlite3.connect('batman_game.db')
cursor = conn.cursor()

# Crear la tabla para almacenar las respuestas
cursor.execute('''CREATE TABLE IF NOT EXISTS respuestas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pregunta TEXT,
                    respuesta TEXT)''')

# Crear la tabla para los personajes y sus características
cursor.execute('''CREATE TABLE IF NOT EXISTS personajes (
                    nombre TEXT PRIMARY KEY,
                    humano BOOLEAN,
                    villano BOOLEAN,
                    arma TEXT,
                    poderes BOOLEAN)''')

# Función para agregar personajes iniciales en la base de datos si no existen
def agregar_personajes_iniciales():
    personajes_iniciales = {
        "Batman": {"humano": True, "villano": False, "arma": "batarang", "poderes": False},
        "Joker": {"humano": True, "villano": True, "arma": "gas venenoso", "poderes": False},
        "Harley Quinn": {"humano": True, "villano": True, "arma": "martillo", "poderes": False},
        "Bane": {"humano": True, "villano": True, "arma": "fuerza bruta", "poderes": True},
        "Mr. Freeze": {"humano": True, "villano": True, "arma": "hielo", "poderes": True},
        "Superman": {"humano": False, "villano": False, "arma": "fuerza", "poderes": True},
    }

    for nombre, caracteristicas in personajes_iniciales.items():
        cursor.execute('''INSERT OR IGNORE INTO personajes (nombre, humano, villano, arma, poderes)
                          VALUES (?, ?, ?, ?, ?)''',
                       (nombre, caracteristicas['humano'], caracteristicas['villano'], caracteristicas['arma'], caracteristicas['poderes']))
    conn.commit()

# Función para hacer preguntas al usuario
def hacer_pregunta(pregunta):
    respuesta = input(pregunta + " (sí/no): ").lower()
    while respuesta not in ['sí', 'no']:
        respuesta = input("Por favor responde 'sí' o 'no': ").lower()
    
    # Guardar la respuesta en la base de datos
    cursor.execute("INSERT INTO respuestas (pregunta, respuesta) VALUES (?, ?)", (pregunta, respuesta))
    conn.commit()
    
    return respuesta == 'sí'

# Función para agregar un nuevo personaje a la base de datos
def agregar_personaje():
    nombre = input("¿Cuál era el personaje correcto?: ").capitalize()
    if cursor.execute("SELECT * FROM personajes WHERE nombre = ?", (nombre,)).fetchone():
        print("Este personaje ya está registrado.")
        return

    humano = hacer_pregunta(f"¿{nombre} es un humano?")
    villano = hacer_pregunta(f"¿{nombre} es un villano?")
    arma = input(f"¿Cuál es el arma principal de {nombre}?: ")
    poderes = hacer_pregunta(f"¿{nombre} tiene poderes?")
    
    cursor.execute('''INSERT INTO personajes (nombre, humano, villano, arma, poderes)
                      VALUES (?, ?, ?, ?, ?)''', (nombre, humano, villano, arma, poderes))
    conn.commit()
    print(f"{nombre} ha sido agregado a la base de datos.")

# Encadenamiento hacia adelante con recuperación desde la base de datos
def encadenamiento_adelante():
    cursor.execute("SELECT * FROM personajes")
    personajes = cursor.fetchall()
    
    posibles = {p[0]: {"humano": p[1], "villano": p[2], "arma": p[3], "poderes": p[4]} for p in personajes}

    # Aplicar reglas según las respuestas
    if hacer_pregunta("¿El personaje es un humano?"):
        posibles = {k: v for k, v in posibles.items() if v["humano"]}
    else:
        posibles = {k: v for k, v in posibles.items() if not v["humano"]}

    if hacer_pregunta("¿Es un villano?"):
        posibles = {k: v for k, v in posibles.items() if v["villano"]}
    else:
        posibles = {k: v for k, v in posibles.items() if not v["villano"]}

    if hacer_pregunta("¿Tiene poderes?"):
        posibles = {k: v for k, v in posibles.items() if v["poderes"]}
    else:
        posibles = {k: v for k, v in posibles.items() if not v["poderes"]}

    # Si quedan más de un personaje, preguntar sobre el arma para afinar
    if len(posibles) > 1:
        print("Todavía quedan varios personajes posibles. Vamos a hacer más preguntas.")
        armas_posibles = list(set(v["arma"] for v in posibles.values()))  # Obtener armas distintas de los personajes restantes
        
        # Hacer preguntas sobre las armas solo si hay más de un arma posible
        for arma in armas_posibles:
            if hacer_pregunta(f"¿El personaje usa {arma} como arma principal?"):
                posibles = {k: v for k, v in posibles.items() if v["arma"] == arma}
                break
    
    # Mostrar resultado si queda solo uno
    if len(posibles) == 1:
        personaje_adivinado = list(posibles.keys())[0]
        print(f"¿Tu personaje es {personaje_adivinado}?")
        if hacer_pregunta("¿Es correcto?"):
            print("¡He adivinado correctamente!")
        else:
            print("Vaya, no lo adiviné.")
            agregar_personaje()
    elif len(posibles) > 1:
        print(f"Algo salió mal, todavía hay varios personajes: {', '.join(posibles.keys())}")
    else:
        print("No se pudo determinar el personaje.")
        agregar_personaje()

# Lógica del juego
def juego():
    print("¡Bienvenido al juego de Adivina Quién!")
    agregar_personajes_iniciales()  # Asegurar que los personajes iniciales estén cargados en la base de datos
    encadenamiento_adelante()
    
# Ejecutar el juego
juego()

# Cerrar la conexión a la base de datos al final
conn.close()
