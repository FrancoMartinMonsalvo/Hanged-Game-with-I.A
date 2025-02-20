import json
import random
import requests
import os
import sqlite3

# Directorio actual del script (backend/game)
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construir la ruta al archivo diccionario.txt de forma relativa
file_path = os.path.join(script_dir, "..", "dictionary", "diccionario.txt")

# Conectar a la base de datos SQLite de forma relativa
def connect_db():
    db_path = os.path.join(script_dir, "..", "dbase", "hangedDB.db")
    db_path = os.path.abspath(db_path)  # Convertir a ruta absoluta
    return sqlite3.connect(db_path)

# Función para agregar la columna 'remaining_lives' a la tabla 'game_step'
def add_remaining_lives_column():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("ALTER TABLE game_step ADD COLUMN remaining_lives INTEGER")
        conn.commit()
    except sqlite3.OperationalError as e:
        print("Error al agregar la columna:", e)
    finally:
        conn.close()

# Llamar a la función para agregar la columna solo una vez al iniciar el script
add_remaining_lives_column()

# Registrar la palabra en la tabla 'word'
def register_word(word_to_guess, language):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM word WHERE word = ? AND language = ?", (word_to_guess, language))
    word = cursor.fetchone()

    if not word:
        cursor.execute("INSERT INTO word (word, language, letters) VALUES (?, ?, ?)",
                       (word_to_guess, language, len(word_to_guess)))
        conn.commit()
    conn.close()

# Registrar el resultado del juego en la tabla 'game_result'
def register_game_result(execution_id, word_id, remaining_lives, won, used_letters):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO game_result (execution_id, word_to_guess, remaining_lives, used_letters, won) VALUES (?, ?, ?, ?, ?)",
                   (execution_id, word_id, remaining_lives, ",".join(used_letters), won))
    conn.commit()
    conn.close()

# Registrar la ejecución del juego en la tabla 'execution'
def register_execution(games_to_play, min_letters, max_letters, language):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("INSERT INTO execution (games_to_play, min_letters, max_letters, language) VALUES (?, ?, ?, ?)",
                   (games_to_play, min_letters, max_letters, language))
    conn.commit()
    execution_id = cursor.lastrowid  # Obtener el ID de la ejecución recién insertada
    conn.close()
    return execution_id

# Registrar un paso del juego en la tabla 'game_step'
def register_game_step(execution_id, guess, remaining_lives, used_letters):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(""" 
    INSERT INTO game_step (execution_id, guess, remaining_lives, used_letters) 
    VALUES (?, ?, ?, ?) 
    """, (execution_id, guess, remaining_lives, ",".join(used_letters)))

    conn.commit()
    conn.close()

# Obtener los pasos del juego
def get_game_steps(execution_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT game_step_id, guess, remaining_lives, used_letters FROM game_step WHERE execution_id = ? ORDER BY game_step_id", (execution_id,))
    steps = cursor.fetchall()
    conn.close()

    return steps

# Definir la palabra
def random_word():
    with open(file_path, "r", encoding="utf-8") as file:
        word_list = file.read().splitlines()
        return random.choice(word_list).lower()

# Crear el cuerpo para la petición de la IA
def get_body(word_to_guess, language, lives, used_letters):
    content = (
        f"You are playing a hanged man game. Your word to guess is: {word_to_guess} "
        f"The word is in {language}. You have {lives} lives left. "
        f"You have used the following letters already: {used_letters} "
        "return only a letter with your guess and say nothing else and provide no explanation. Be concise."
    )
    data = {
        "messages": [
            {
                "role": "user",
                "content": content
            }
        ],
        "max_tokens": 50
    }
    return json.dumps(data)

# Función para actualizar la palabra en pantalla
def update_word_display(correct_letters, word_to_guess):
    return "".join(letter if letter in correct_letters else "._." for letter in word_to_guess).split(".")

# Función principal para jugar
def play():
    word_to_guess = random_word()
    lives = 5
    used_letters = set()  # Usar un set para las letras usadas
    correct_letters = set()  # Usar un set para las letras correctas
    word_display = ["._." for _ in word_to_guess]  # Estado inicial de la palabra
    language = "spanish (argentina)"
    guessed = False

    # Registrar la palabra en la base de datos
    register_word(word_to_guess, language)

    # Registrar la ejecución del juego
    execution_id = register_execution(games_to_play=1, min_letters=3, max_letters=10, language=language)

    url = 'http://localhost:1234/v1/chat/completions'
    headers = {"Content-Type": "application/json"}

    game_step_id = 1  # Contador de pasos del juego

    while lives > 0 and not guessed:
        body = get_body(word_display, language, lives, list(used_letters))  # Convertir set a lista para el cuerpo de la petición
        res = requests.post(url, data=body, headers=headers)
        data = json.loads(res.content)
        guess = data["choices"][0]["message"]["content"]

        if guess in word_to_guess:
            if guess not in correct_letters:  # Evitar agregar letras repetidas
                correct_letters.add(guess)  # Agregar al set de letras correctas
                word_display = update_word_display(correct_letters, word_to_guess)
                if "_" not in word_display:  # Si no quedan guiones bajos, ganaste
                    guessed = True
                    won = True
        else:
            if guess not in used_letters:
                used_letters.add(guess)  # Añadir la letra a las usadas solo si no fue usada antes
                lives -= 1
            if lives == 0:
                guessed = True
                won = False

        # Registrar el paso del juego
        register_game_step(execution_id, guess, lives, list(used_letters))  # Corrigiendo la llamada
        game_step_id += 1

    # Obtener el ID de la palabra
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT word_id FROM word WHERE word = ? AND language = ?", (word_to_guess, language))
    word_id = cursor.fetchone()[0]
    conn.close()

    # Registrar el resultado del juego en la base de datos
    register_game_result(execution_id, word_id, lives, won, list(used_letters))

    # Mostrar los pasos del juego
    steps = get_game_steps(execution_id)
    for step in steps:
        print(f"Step {step[0]}: Guess: {step[1]}, Remaining Lives: {step[2]}, Used Letters: {step[3]}")

