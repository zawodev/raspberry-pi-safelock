import sqlite3
from datetime import datetime
import json  # do serializacji safe_combination

def create_connection(db_file: str):
    """
    Tworzy i zwraca połączenie do bazy danych SQLite.
    Jeśli nie istnieje plik db_file, zostanie on utworzony.
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        print("Połączono z bazą danych:", db_file)

        # Włączenie wsparcia dla kluczy obcych (domyślnie w SQLite jest wyłączone)
        conn.execute("PRAGMA foreign_keys = ON;")

    except sqlite3.Error as e:
        print("Błąd podczas łączenia z bazą danych:", e)
    return conn

def create_tables(conn):
    """
    Tworzy tabele w bazie danych, jeśli jeszcze nie istnieją.
    Uwaga: user_id w tabeli Users jest typu TEXT, a w Ewidencja/Requests klucz obcy też jest TEXT.
    """
    try:
        cursor = conn.cursor()

        create_users_table = """
        CREATE TABLE IF NOT EXISTS Users (
            id TEXT PRIMARY KEY,
            login TEXT NOT NULL,
            password TEXT NOT NULL,
            -- Tutaj przechowujemy JSON z 8 liczbami z zakresu 0..255
            safe_combination TEXT
        );
        """
        cursor.execute(create_users_table)

        create_login_records_table = """
        CREATE TABLE IF NOT EXISTS LoginRecords (
            login_record_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date_time TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
        );
        """
        cursor.execute(create_login_records_table)

        create_requests_table = """
        CREATE TABLE IF NOT EXISTS Requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date_time TEXT NOT NULL
        );
        """
        cursor.execute(create_requests_table)

        conn.commit()
        print("Tabele zostały utworzone (lub już istniały).")
    except sqlite3.Error as e:
        print("Błąd podczas tworzenia tabel:", e)


# =================================
# Operacje CRUD na tabeli Users
# =================================

def add_user(conn, user_id: str, login: str, password: str, safe_combination: list):
    """
    Dodaje nowego użytkownika do tabeli Users.
    user_id: tekstowe ID użytkownika (np. numer karty, unikalny login)
    safe_combination: lista 8 liczb (każda 0..255).
    """
    try:
        cursor = conn.cursor()

        # Serializacja listy 8 liczb do JSON, np. [12, 255, 0, 128, ...] -> "[12, 255, 0, 128, ...]"
        safe_combination_json = json.dumps(safe_combination)

        query = """
        INSERT INTO Users (id, login, password, safe_combination)
        VALUES (?, ?, ?, ?)
        """
        cursor.execute(query, (user_id, login, password, safe_combination_json))
        conn.commit()
        print(f"Dodano użytkownika: {user_id} (login: {login})")
    except sqlite3.Error as e:
        print("Błąd podczas dodawania użytkownika:", e)

def get_all_users(conn):
    """
    Zwraca listę krotek (id, login, password, safe_combination) wszystkich użytkowników.
    Ponieważ safe_combination mamy jako TEXT (JSON), zwracamy to, co jest w bazie (jeszcze niesparsowane).
    """
    try:
        cursor = conn.cursor()
        query = "SELECT id, login, password, safe_combination FROM Users"
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.Error as e:
        print(e)
        return []

def delete_user(conn, user_id: str):
    """
    Usuwa użytkownika z tabeli Users po ID (TEXT).
    Bez ON DELETE CASCADE w definicji kluczy obcych, nie usunie powiązanych wpisów w Ewidencja/Requests.
    """
    try:
        cursor = conn.cursor()
        query = "DELETE FROM Users WHERE id = ?"
        cursor.execute(query, (user_id,))
        conn.commit()
        print(f"Usunięto użytkownika ID = {user_id} (z rekordami w LoginRecords).")
    except sqlite3.Error as e:
        print("Błąd podczas usuwania użytkownika:", e)

# =================================
# Operacje CRUD na tabeli LoginRecords
# =================================

def add_login_record(conn, user_id: str, status: str):
    """
    Dodaje wpis do tabeli LoginRecords.
    Wstawiamy aktualną datę/czas w polu date_time.
    user_id: tekstowe ID użytkownika (powiązane z Users.id)
    status: np. "ACCEPTED", "FAILED"
    """
    try:
        cursor = conn.cursor()
        now = datetime.now().isoformat(timespec='seconds')
        query = """
        INSERT INTO LoginRecords (user_id, date_time, status)
        VALUES (?, ?, ?)
        """
        cursor.execute(query, (user_id, now, status))
        conn.commit()
        print(f"Dodano wpis do LoginRecords z user_id = {user_id}, status = {status}")
    except sqlite3.Error as e:
        print("Błąd podczas dodawania wpisu do LoginRecords:", e)

def get_all_login_records(conn):
    """
    Pobiera wszystkie wpisy z tabeli LoginRecords.
    Zwraca listę krotek (login_record_id, user_id, date_time, status) lub pustą listę.
    """
    try:
        cursor = conn.cursor()
        query = "SELECT login_record_id, user_id, date_time, status FROM LoginRecords"
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print("Błąd podczas pobierania danych z LoginRecords:", e)
        return []

# =================================
# Operacje CRUD na tabeli Requests
# =================================

def add_request(conn, user_id: str):
    """
    Dodaje wpis do tabeli Requests.
    Wstawiamy aktualną datę/czas w polu date_time.
    user_id: tekstowe ID użytkownika (powiązane z Users.id)
    """
    try:
        cursor = conn.cursor()
        now = datetime.now().isoformat(timespec='seconds')
        query = """
        INSERT INTO Requests (user_id, date_time)
        VALUES (?, ?)
        """
        cursor.execute(query, (user_id, now))
        conn.commit()
        print(f"Dodano wpis do Requests z user_id = {user_id}")
    except sqlite3.Error as e:
        print("Błąd podczas dodawania wpisu do Requests:", e)

def get_all_requests(conn):
    """
    Pobiera wszystkie wpisy z tabeli Requests.
    Zwraca listę krotek (request_id, user_id, date_time) lub pustą listę.
    """
    try:
        cursor = conn.cursor()
        query = "SELECT request_id, user_id, date_time FROM Requests"
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    except sqlite3.Error as e:
        print("Błąd podczas pobierania danych z Requests:", e)
        return []

def delete_request(conn, request_id: int):
    """
    Usuwa rekord z tabeli Requests po request_id.
    """
    # try:
    #     cursor = conn.cursor()
    #     query = "DELETE FROM Requests WHERE request_id = ?"
    #     cursor.execute(query, (request_id,))
    #     conn.commit()
    # except sqlite3.Error as e:
    #     print(e)
    try:
        cursor = conn.cursor()

        # Najpierw ustal, jakiego user_id dotyczy prośba o request_id:
        cursor.execute("SELECT user_id FROM Requests WHERE request_id = ?", (request_id,))
        row = cursor.fetchone()

        if row is not None:
            user_id = row[0]

            # Teraz usuń *wszystkie* wiersze w Requests, gdzie user_id jest taki sam
            cursor.execute("DELETE FROM Requests WHERE user_id = ?", (user_id,))
            conn.commit()
            print(f"Usunięto wszystkie prośby w Requests związane z user_id = {user_id}.")
        else:
            print(f"Brak prośby o request_id={request_id} w tabeli Requests. Nic nie usuwam.")

    except sqlite3.Error as e:
        print("Błąd podczas usuwania requestu:", e)




if __name__ == "__main__":
    import os
    path = os.path.join(os.getcwd(), "database.db")
    connection = create_connection(path)
    
    import os
    print(os.getcwd())

    if connection:
        create_tables(connection)

        user_id_example = "CARD_001"
        user_login = "jan_kowalski"
        user_password = "haslo123"

        user_safe_combination = [255, 0, 100, 120, 200, 0, 0, 240]

        add_user(connection, user_id_example, user_login, user_password, user_safe_combination)

        add_login_record(connection, user_id_example, "ACCEPTED")

        add_request(connection, "CARD_002")

        login_record_rows = get_all_login_records(connection)
        print("Wszystkie wpisy Ewidencja:")
        for row in login_record_rows:
            print(row)

        requests_rows = get_all_requests(connection)
        print("Wszystkie wpisy Requests:")
        for row in requests_rows:
            print(row)

        connection.close()
