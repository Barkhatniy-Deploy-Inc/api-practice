# Проектирование Pydantic-схем (Data Models & DTO)

В данном документе описаны структуры данных, используемые для валидации входных параметров и формирования выходных JSON-ответов. Все схемы базируются на `pydantic.BaseModel`.

---

## 1. Справочные модели (Dictionary Schemas)

Используются для эндпоинтов группы `/dictionaries/*`.

### RegionSchema
*   **region_code**: `str` (Пример: "77")
*   **region_name**: `str` (Пример: "г. Москва")
*   **district_name**: `str` (Пример: "Центральный федеральный округ")
*   **population**: `int` (Численность населения)
*   **vehicles_count**: `int` (Кол-во зарегистрированных ТС)

### BaseDictionarySchema
Универсальная схема для простых справочников (Weather, RoadConditions, AccidentTypes).
*   **id**: `int` | `str`
*   **name**: `str`

---

## 2. Модели реестра ДТП (Accident Schemas)

### AccidentShortSchema
Краткая карточка ДТП для списков.
*   **id**: `int` (Внутренний ID БД)
*   **empt_number**: `str` (Системный номер ГИБДД)
*   **date**: `date` (ГГГГ-ММ-ДД)
*   **time**: `time` (ЧЧ:ММ)
*   **region_code**: `str`
*   **fatalities**: `int` (Кол-во погибших)
*   **injured**: `int` (Кол-во раненых)
*   **address**: `str` (Человекочитаемый адрес)

### AccidentDetailSchema
Полная информация по конкретному случаю.
*   **id**: `int`
*   **main_info**: `MainInfoSchema` (Вложенный объект с гео и условиями)
*   **vehicles**: `List[VehicleSchema]` (Массив ТС)
*   **participants**: `List[ParticipantSchema]` (Массив участников)

#### MainInfoSchema (Вложенная в Detail)
*   **coords**: `Tuple[float, float]` (Широта, Долгота)
*   **weather**: `str`
*   **road_condition**: `str`
*   **locality**: `str`
*   **road_name**: `Optional[str]`
*   **road_km**: `Optional[int]`

---

## 3. Модели участников и ТС (Sub-Schemas)

### VehicleSchema
*   **type**: `str` (Легковой, грузовой и т.д.)
*   **brand**: `str`
*   **model**: `str`
*   **year**: `int`
*   **is_defective**: `bool`

### ParticipantSchema
*   **role**: `str` (Водитель, Пешеход)
*   **gender**: `str` (М/Ж)
*   **age**: `int`
*   **health_status**: `str` (Тяжкий вред, погиб и т.д.)
*   **experience**: `Optional[int]` (Стаж для водителей)
*   **is_drunk**: `bool`

---

## 4. Аналитические модели (Analytics Schemas)

### SummaryStatsSchema
*   **total_accidents**: `int`
*   **total_fatalities**: `int`
*   **total_injured**: `int`
*   **period**: `PeriodSchema`

### TimelineItemSchema
*   **label**: `str` (Например, "2026-03")
*   **accidents**: `int`
*   **fatalities**: `int`

### TrendSchema
*   **month**: `str`
*   **change_pct**: `float` (Процент изменения)

---

## 5. Системные и общие модели

### ResponseEnvelope (Универсальная обертка)
*   **status**: `str` ("success" / "error")
*   **data**: `Any` (Тело ответа)
*   **meta**: `Optional[Dict]` (Пагинация, время обработки)

### ErrorSchema
*   **error_code**: `int`
*   **message**: `str` (На русском языке)
*   **details**: `Optional[Any]`
