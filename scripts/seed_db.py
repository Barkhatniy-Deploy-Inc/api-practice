import json
import os
import sqlite3
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parents[1])
if project_root not in sys.path:
    # Позволяет запускать скрипт как `python scripts/seed_db.py` и как `python -m scripts.seed_db`.
    sys.path.insert(0, project_root)

from scripts.region_catalog import DISTRICTS, REGION_TO_DISTRICT


def resolve_db_path() -> Path:
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./dtp.db")
    prefixes = ("sqlite+aiosqlite:///", "sqlite:///")

    for prefix in prefixes:
        if database_url.startswith(prefix):
            return Path(database_url[len(prefix):])

    raise ValueError(f"Неподдерживаемый DATABASE_URL для seed_db.py: {database_url}")


def seed():
    print("Наполнение справочников из regions_dict.json...")
    db_path = resolve_db_path()
    json_path = Path(__file__).with_name("regions_dict.json")

    if not json_path.exists():
        print(f"Файл {json_path} не найден.")
        return

    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        with json_path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        cursor.executemany(
            "INSERT OR IGNORE INTO districts (id, code, name) VALUES (?, ?, ?)",
            DISTRICTS,
        )

        rows = data.get("results", [{}])[0].get("dict_rows", [])
        region_count = 0

        for row in rows:
            code = str(row.get("rows_code", "")).strip()
            name = str(row.get("rows_name", "")).strip()
            if not code or not name:
                continue

            # В справочнике ГИБДД есть агрегированная строка по всей РФ, это не отдельный регион.
            if code == "1100":
                continue

            district_id = REGION_TO_DISTRICT.get(code)
            if not district_id:
                print(f"Пропускаю регион без district mapping: {code} {name}")
                continue

            cursor.execute(
                "INSERT OR IGNORE INTO regions (code, name, district_id) VALUES (?, ?, ?)",
                (code, name, district_id),
            )
            region_count += 1

        conn.commit()
        print(f"Импортировано или подтверждено регионов: {region_count}")
        print(f"Использована база данных: {db_path}")
    except Exception as exc:
        print(f"Ошибка при импорте: {exc}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    seed()
