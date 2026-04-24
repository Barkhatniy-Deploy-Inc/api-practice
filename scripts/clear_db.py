import sqlite3
import os

DB_PATH = 'DTP_DB.db'

def clear_database():
    print(f"ВНИМАНИЕ! Вы собираетесь безвозвратно удалить ВСЕ данные из базы '{DB_PATH}'.")
    print("Структура таблиц (колонки и связи) будет сохранена.")
    
    confirm = input("Продолжить очистку? (y/n): ")
    if confirm.lower() != 'y':
        print("🛑 Очистка отменена. Данные в безопасности.")
        return

    if not os.path.exists(DB_PATH):
        print(f"❌ Файл {DB_PATH} не найден!")
        return

    try:
        # Замеряем размер до очистки
        size_before = os.path.getsize(DB_PATH) / (1024 * 1024)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Отключаем проверку внешних ключей
        cursor.execute("PRAGMA foreign_keys = OFF;")

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        tables = [row[0] for row in cursor.fetchall()]

        if not tables:
            print("База данных пуста (в ней еще нет таблиц).")
            return

        for table in tables:
            print(f"🧹 Очистка таблицы: {table}...")
            cursor.execute(f"DELETE FROM {table};")

        # Сбрасываем счетчики AUTOINCREMENT
        try:
            cursor.execute("DELETE FROM sqlite_sequence;")
        except sqlite3.OperationalError:
            pass

        conn.commit()

        # --- МАГИЯ СЖАТИЯ ФАЙЛА ---
        print("🗜 Сжатие файла базы данных (VACUUM)...")
        cursor.execute("VACUUM;")
        # --------------------------

        # Замеряем размер после
        size_after = os.path.getsize(DB_PATH) / (1024 * 1024)

        print(f"\n✅ База данных идеально очищена!")
        print(f"📉 Размер файла уменьшен с {size_before:.2f} МБ до {size_after:.2f} МБ.")

    except sqlite3.Error as e:
        print(f"❌ Произошла ошибка БД: {e}")
    finally:
        if 'conn' in locals() and conn:
            cursor.execute("PRAGMA foreign_keys = ON;")
            conn.close()

if __name__ == "__main__":
    clear_database()