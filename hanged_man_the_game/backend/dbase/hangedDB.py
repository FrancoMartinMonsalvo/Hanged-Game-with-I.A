import sqlite3

# Conectarse a la base de datos (puedes usar ':memory:' para bases de datos en memoria)
conn = sqlite3.connect('hangedDB.db')
cursor = conn.cursor()

# Crear la tabla de palabras
cursor.execute('''
CREATE TABLE IF NOT EXISTS word (
    word_id INTEGER PRIMARY KEY AUTOINCREMENT,  
    word TEXT NOT NULL,                         
    language TEXT NOT NULL,                     
    letters INTEGER NOT NULL                    
)
''')

# Crear la tabla de ejecución de juegos
cursor.execute('''
CREATE TABLE IF NOT EXISTS execution (
    execution_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    games_to_play INTEGER NOT NULL,                 
    min_letters INTEGER NOT NULL,                   
    max_letters INTEGER NOT NULL,                   
    language TEXT NOT NULL                          
)
''')

# Crear la tabla de pasos del juego
cursor.execute('''
CREATE TABLE IF NOT EXISTS game_step (
    game_step_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    execution_id INTEGER,                            
    guess TEXT NOT NULL,                             
    remaining_lives INTEGER NOT NULL,                
    used_letters TEXT NOT NULL,                     
    FOREIGN KEY (execution_id) REFERENCES execution(execution_id)
)
''')

# Crear la tabla de resultados del juego
cursor.execute('''
CREATE TABLE IF NOT EXISTS game_result (
    game_result_id INTEGER PRIMARY KEY AUTOINCREMENT,  
    execution_id INTEGER,                              
    word_to_guess INTEGER,                             
    remaining_lives INTEGER NOT NULL,                  
    used_letters TEXT NOT NULL,                       
    won BOOLEAN NOT NULL,                              
    FOREIGN KEY (execution_id) REFERENCES execution(execution_id),  
    FOREIGN KEY (word_to_guess) REFERENCES word(word_id) 
)
''')

# Para agregar la columna 'remaining_lives' a la tabla 'game_step' si no existe en SQLite,
# primero debes crear una nueva tabla temporal con la columna añadida,
# copiar los datos de la tabla original a la nueva tabla, eliminar la tabla original,
# y renombrar la nueva tabla.

# Crear la tabla temporal con la columna 'remaining_lives'
cursor.execute('''
CREATE TABLE IF NOT EXISTS game_step_temp (
    game_step_id INTEGER PRIMARY KEY AUTOINCREMENT, 
    execution_id INTEGER,
    guess TEXT NOT NULL,
    remaining_lives INTEGER NOT NULL,                
    used_letters TEXT NOT NULL,
    FOREIGN KEY (execution_id) REFERENCES execution(execution_id)
)
''')

# Copiar los datos de la tabla original a la tabla temporal
cursor.execute('''
INSERT INTO game_step_temp (game_step_id, execution_id, guess, used_letters)
SELECT game_step_id, execution_id, guess, used_letters FROM game_step
''')

# Eliminar la tabla original
cursor.execute('DROP TABLE game_step')

# Renombrar la tabla temporal a la tabla original
cursor.execute('ALTER TABLE game_step_temp RENAME TO game_step')

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()
