import sqlite3
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import random
import logging
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)

DB_PATH = 'DTP_DB.db'
API_URL = 'http://stat.gibdd.ru/opendataapi/v1/kartdtp/rows'

REGION_TO_DISTRICT = {
    "1145": 1, "1117": 1, "1115": 1, "1120": 1, "1124": 1, "1129": 1, "1134": 1, "1142": 1, "1146": 1, "1154": 1, "1161": 1, "1166": 1, "1170": 1, "1178": 1, "1180": 1, "1114": 1,
    "1140": 2, "1111": 2, "1118": 2, "1119": 2, "1127": 2, "1133": 2, "1141": 2, "1147": 2, "1153": 2, "1110": 2,
    "1103": 3, "1112": 3, "1137": 3, "1160": 3, "1113": 3, "1132": 3,
    "1107": 4, "1123": 4, "1125": 4, "1128": 4, "1130": 4, "1183": 4, "1106": 4,
    "1136": 5, "1116": 5, "1122": 5, "1131": 5, "1143": 5, "1152": 5, "1156": 5, "1157": 5, "1158": 5, "1163": 5, "1171": 5, "1173": 5, "1108": 5,
    "1165": 6, "1175": 6, "1150": 6, "1174": 6, "1172": 6,
    "1104": 7, "1138": 7, "1144": 7, "1151": 7, "1169": 7, "1184": 7, "1195": 7, "1102": 7,
    "1105": 8, "1109": 8, "1121": 8, "1164": 8, "1176": 8, "1177": 8, "1179": 8, "1185": 8, "1186": 8, "1187": 8, "1188": 8, "1189": 8, "1190": 8, "1191": 8, "1192": 8, "1193": 8, "1194": 8, "1196": 8, "1197": 8, "1198": 8, "1199": 8
}

REGIONS = list(REGION_TO_DISTRICT.keys())
YEARS_TO_PARSE = [2023, 2024]
MONTHS = list(range(1, 13))

def create_robust_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'application/json'
    })
    retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def heal_districts(conn):
    """Функция самолечения: заполняет пустую таблицу округов, чтобы не падали внешние ключи"""
    cursor = conn.cursor()
    districts_data = [
        (1, 'CFO', 'Центральный федеральный округ'), (2, 'SZFO', 'Северо-Западный федеральный округ'),
        (3, 'UFO', 'Южный федеральный округ'), (4, 'SKFO', 'Северо-Кавказский федеральный округ'),
        (5, 'PFO', 'Приволжский федеральный округ'), (6, 'URFO', 'Уральский федеральный округ'),
        (7, 'SFO', 'Сибирский федеральный округ'), (8, 'DFO', 'Дальневосточный федеральный округ')
    ]
    try:
        cursor.executemany("INSERT OR IGNORE INTO districts (id, code, name) VALUES (?, ?, ?)", districts_data)
        conn.commit()
    except sqlite3.OperationalError:
        pass

def get_or_create_dict(cursor, table_name, value):
    if not value: return 0
    clean_value = value[0] if isinstance(value, list) and value else str(value)
    cursor.execute(f'SELECT id FROM {table_name} WHERE name = ?', (clean_value,))
    row = cursor.fetchone()
    if row: return row[0]
    cursor.execute(f'INSERT INTO {table_name} (name) VALUES (?)', (clean_value,))
    return cursor.lastrowid

def get_or_create_car_model(cursor, model_name, brand_id):
    if not model_name: return 0
    cursor.execute('SELECT id FROM car_models WHERE name = ?', (model_name,))
    row = cursor.fetchone()
    if row: return row[0]
    cursor.execute('INSERT INTO car_models (name, brand) VALUES (?, ?)', (model_name, brand_id))
    return cursor.lastrowid

def fetch_and_save(session, conn, region, year, month):
    cursor = conn.cursor()
    
    cursor.execute('SELECT 1 FROM sync_history WHERE region_code=? AND year=? AND month=?', (region, year, month))
    if cursor.fetchone() is not None:
        logging.info(f"Пропуск: Регион {region} за {month}/{year}")
        return

    params = {"pok": "1", "dat": f"{month}.{year}", "reg": str(region)}

    try:
        logging.info(f"Запрос: Регион {region} | {month}/{year}...")
        response = session.get(API_URL, params=params, timeout=30)
        
        if response.status_code != 200:
            logging.error(f"Ошибка сервера ГИБДД: {response.status_code}")
            return

        data = response.json()
        dtp_cards = []
        
        try:
            region_list = data.get('results', {}).get('region_list', [])
            if region_list:
                reg_code_api = str(region_list[0].get('reg_code', region))
                reg_name_api = region_list[0].get('reg_name', f'Регион {region}')
                dist_id = REGION_TO_DISTRICT.get(reg_code_api)
                
                cursor.execute('''
                    INSERT OR IGNORE INTO regions (code, name, district_id)
                    VALUES (?, ?, ?)
                ''', (reg_code_api, reg_name_api, dist_id))

                pok_list = region_list[0].get('pok_list', [])
                if pok_list:
                    result_array = pok_list[0].get('result', [])
                    if result_array:
                        dtpcardlist = result_array[0].get('dtpcardlist', {})
                        if dtpcardlist:
                            dtp_cards = dtpcardlist.get('info_dtp', [])
        except Exception as e:
            logging.warning(f"Ошибка разбора JSON: {e}")
            pass

        records_count = len(dtp_cards)
        
        if records_count > 0:
            for card in dtp_cards:
                empt_number = card.get('empt_number')
                if not empt_number: continue
                
                date_dtp_raw = card.get('date_dtp', '')
                if '.' in date_dtp_raw:
                    d, m, y = date_dtp_raw.split('.')
                    date_dtp = f"{y}-{m}-{d}"
                else:
                    date_dtp = f"{year}-{month:02d}-01"
                
                lighting = card.get('osv') or 'Не указано'
                road_type = card.get('k_dor') or card.get('dor_k') or 'Не указано'
                
                ndu_list = card.get('ndu', [])
                has_road_defect = 1 if ndu_list else 0
                road_defect_desc = ", ".join(ndu_list) if ndu_list else ""

                pog_data = card.get('s_pog')
                weather_name = pog_data[0] if isinstance(pog_data, list) and pog_data else 'Не указано'
                weather_id = get_or_create_dict(cursor, 'weather_types', weather_name)
                
                pch_data = card.get('s_pch')
                road_cond_name = pch_data[0] if isinstance(pch_data, list) and pch_data else 'Не указано'
                road_cond_id = get_or_create_dict(cursor, 'road_conditions', road_cond_name)

                f_skr = str(card.get('f_skr', '')).lower()
                driver_fled = 1 if 'да' in f_skr or f_skr == '1' else 0

                child_pog = int(card.get('k_d_pog', 0)) if str(card.get('k_d_pog')).isdigit() else 0
                child_ran = int(card.get('k_d_ran', 0)) if str(card.get('k_d_ran')).isdigit() else 0
                has_children = 1 if (child_pog + child_ran) > 0 else 0

                np_alc = str(card.get('np_alc', '')).lower()
                has_drunk = 1 if 'да' in np_alc or card.get('f_alc') == '1' else 0
                
                is_railway = 1 if 'жд' in str(card.get('f_zhd', '')).lower() else 0

                accident_type_id = get_or_create_dict(cursor, 'accident_types', card.get('dtpv') or 'Не указано')

                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO accidents (
                            empt_number, accident_type_id, date_dtp, time_dtp,
                            region_code, coord_lat, coord_lon, locality, road_name, road_km,
                            is_city, road_category, weather_id, road_cond_id,
                            lighting, has_road_defect, road_type, road_defect_desc,
                            fatalities, injured, vehicles_count, participants_count, 
                            has_children, driver_fled, has_drunk, is_railway
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        empt_number, accident_type_id, date_dtp, card.get('time', '00:00'),
                        region, float(card.get('coord_w') or 0), float(card.get('coord_l') or 0),
                        card.get('n_p', 'Не указано'), card.get('dor') or card.get('k_ul') or 'Не указана',
                        int(card.get('km')) if str(card.get('km')).isdigit() else 0,
                        1 if card.get('n_p') else 0, card.get('k_dor_zn', 'Не указано'),
                        weather_id, road_cond_id, lighting, has_road_defect, road_type, road_defect_desc,
                        card.get('pog', 0), card.get('ran', 0), card.get('k_ts', 1), card.get('k_uch', 1),
                        has_children, driver_fled, has_drunk, is_railway
                    ))
                    
                    cursor.execute('SELECT id FROM accidents WHERE empt_number = ?', (empt_number,))
                    acc_row = cursor.fetchone()
                    if not acc_row: continue
                    accident_id = acc_row[0]
                    
                except sqlite3.Error as e:
                    logging.error(f"Ошибка БД (ДТП {empt_number}): {e}")
                    continue

                ts_info = card.get('ts_info', [])
                for ts in ts_info:
                    c_brand_id = get_or_create_dict(cursor, 'car_brands', ts.get('marka_ts') or 'Не указан')
                    c_model_id = get_or_create_car_model(cursor, ts.get('m_ts') or 'Не указана', c_brand_id)
                    c_type_id = get_or_create_dict(cursor, 'car_types', ts.get('t_ts') or 'Не указан')

                    cursor.execute('''
                        INSERT INTO vehicles (accident_id, car_type_id, car_brand_id, car_model_id, year_release)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (accident_id, c_type_id, c_brand_id, c_model_id, int(ts.get('g_v') or 0)))
                    vehicle_id = cursor.lastrowid

                    ts_uch = ts.get('ts_uch', [])
                    for uch in ts_uch:
                        raw_gender = str(uch.get('pol') or uch.get('POL') or '').strip().lower()
                        if raw_gender.startswith('м'):
                            gender = 'Мужской'
                        elif raw_gender.startswith('ж'):
                            gender = 'Женский'
                        else:
                            gender = 'Не указан'
                        
                        raw_age = str(uch.get('v_r') or uch.get('V_R') or '')
                        age_digits = ''.join(filter(str.isdigit, raw_age))
                        age = int(age_digits) if age_digits else None
                        
                        raw_exp = str(uch.get('v_st') or uch.get('V_ST') or '')
                        exp_digits = ''.join(filter(str.isdigit, raw_exp))
                        experience = int(exp_digits) if exp_digits else None
                        
                        cursor.execute('''
                            INSERT INTO participants (
                                accident_id, vehicle_id, role, gender, age, experience, 
                                is_drunk, is_culprit, health_status, first_aid
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            accident_id, vehicle_id, uch.get('kt_uch', 'Неизвестно'), 
                            gender, age, experience, 
                            1 if 'опьянени' in str(uch.get('alco', '')).lower() else 0,
                            1 if uch.get('NPDD') else 0, uch.get('S_P', 'Не указано'),
                            1 if uch.get('MED_P') else 0
                        ))

            conn.commit()
            cursor.execute('INSERT OR REPLACE INTO sync_history (region_code, year, month, records_downloaded) VALUES (?, ?, ?, ?)', (region, year, month, records_count))
            conn.commit()
            logging.info(f"✅ Синхронизация: {region} за {month}/{year} — OK.")
        else:
            cursor.execute('INSERT OR REPLACE INTO sync_history (region_code, year, month, records_downloaded) VALUES (?, ?, ?, ?)', (region, year, month, 0))
            conn.commit()

        time.sleep(random.uniform(0.3, 0.6))

    except Exception as e:
        logging.error(f"❌ Критическая ошибка в регионе {region}: {e}")

def main():
    if not os.path.exists(DB_PATH):
        logging.error(f"Файл базы данных '{DB_PATH}' не найден! Выполните setup_db.py.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    
    # --- МАГИЯ САМОЛЕЧЕНИЯ ---
    heal_districts(conn)
    # -------------------------

    session = create_robust_session()
    
    logging.info("🚀 Синхронизация запущена (Версия с авто-лечением базы)...")
    
    try:
        for year in YEARS_TO_PARSE:
            for month in MONTHS:
                for r_code in REGIONS:
                    fetch_and_save(session, conn, r_code, year, month)
    finally:
        session.close()
        conn.close()

if __name__ == "__main__":
    main()
