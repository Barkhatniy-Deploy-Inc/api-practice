import json
import sqlite3
import os

def seed():
    print("🌱 Наполнение справочников из реального JSON...")
    db_path = "dtp.db"
    json_path = "regions_dict.json"
    
    if not os.path.exists(json_path):
        print(f"❌ Файл {json_path} не найден.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 1. Заполняем округа (базовый набор)
        districts = [
            (1, "ЦФО", "Центральный федеральный округ"),
            (2, "СЗФО", "Северо-Западный федеральный округ"),
            (3, "ЮФО", "Южный федеральный округ"),
            (4, "СКФО", "Северо-Кавказский федеральный округ"),
            (5, "ПФО", "Приволжский федеральный округ"),
            (6, "УФО", "Уральский федеральный округ"),
            (7, "СФО", "Сибирский федеральный округ"),
            (8, "ДФО", "Дальневосточный федеральный округ")
        ]
        cursor.executemany("INSERT OR IGNORE INTO districts (id, code, name) VALUES (?, ?, ?)", districts)
        
        # 2. Извлекаем регионы из сложной структуры JSON
        # results[0] -> dict_rows
        rows = data.get("results", [{}])[0].get("dict_rows", [])
        
        region_count = 0
        for row in rows:
            code = row.get("rows_code")
            name = row.get("rows_name")
            if code and name:
                # По умолчанию привязываем к 1 округу, если в JSON нет явной связи
                cursor.execute("INSERT OR IGNORE INTO regions (code, name, district_id) VALUES (?, ?, ?)", (code, name, 1))
                region_count += 1
            
        conn.commit()
        print(f"✅ Импортировано регионов: {region_count}")
        print("✅ База данных полностью инициализирована.")
    except Exception as e:
        print(f"❌ Ошибка при импорте: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    seed()
