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
        # Включаем проверку внешних ключей для безопасности
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()

        # Список таблиц в порядке, учитывающем зависимости (от дочерних к родительским)
        # Это позволяет избежать ошибок внешних ключей без отключения PRAGMA
        tables_to_clear = [
            'participants',
            'vehicles',
            'accidents',
            'sync_history',
            'regions',
            'districts',
            'car_models',
            'car_brands',
            'car_types',
            'road_conditions',
            'weather_types',
            'accident_types'
        ]

        print("🚀 Начало процесса полной очистки базы данных...")

        # Используем транзакцию для обеспечения целостности
        try:
            for table in tables_to_clear:
                # Проверяем существование таблицы перед удалением
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table,))
                if cursor.fetchone():
                    print(f"🧹 Очистка таблицы: {table}...")
                    cursor.execute(f"DELETE FROM {table};")
            
            # Сбрасываем счетчики AUTOINCREMENT
            try:
                cursor.execute("DELETE FROM sqlite_sequence;")
            except sqlite3.OperationalError:
                # Таблица sqlite_sequence может отсутствовать, если нет AUTOINCREMENT
                pass

            conn.commit()
            print("✅ Все данные успешно удалены и транзакция зафиксирована.")

        except Exception as e:
            conn.rollback()
            print(f"❌ Ошибка во время очистки, изменения отменены: {e}")
            return

        # --- СЖАТИЕ ФАЙЛА ---
        print("🗜 Выполнение VACUUM для оптимизации места...")
        conn.execute("VACUUM;")
        # --------------------------

        # Замеряем размер после
        size_after = os.path.getsize(DB_PATH) / (1024 * 1024)

        print(f"\n✨ База данных успешно очищена!")
        print(f"📉 Размер файла: {size_before:.2f} МБ -> {size_after:.2f} МБ.")

    except sqlite3.Error as e:
        print(f"❌ Критическая ошибка SQLite: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    clear_database()