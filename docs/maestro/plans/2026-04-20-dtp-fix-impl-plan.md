---
task_complexity: medium
---

# Implementation Plan: Backend Refactoring

## 1. Plan Overview
Этот план направлен на устранение технических долгов, дублирования кода и улучшение безопасности системы.

## 2. Execution Strategy
| Step | Files | Agent |
| :--- | :--- | :--- |
| **1. Data & CRUD** | `session.py`, `crud_accidents.py`, `base.py` | `refactor` |
| **2. Logic Move** | `analytics.py` (Service & Endpoint) | `refactor` |
| **3. Core Polish** | `main.py`, `endpoints/accidents.py` | `refactor` |
| **4. Validation** | `tests/` | `tester` |

## 3. Phase Details

### Phase 1: Data Layer DRY
- **Task**: Создать `CRUDBase` и вынести фильтрацию. Убрать авто-коммит.
- **Validation**: Проверка чтения данных из эндпоинта `/accidents`.

### Phase 2: Analytics Service
- **Task**: Инкапсулировать всю логику в `AnalyticsService`.
- **Validation**: Проверка прогнозов и корреляций.

### Phase 3: Core & Security
- **Task**: Надежная локализация ошибок и удаление мусора.
- **Validation**: Вызов 422 ошибки (некорректный JSON) и проверка перевода.

## 4. Risks
- Изменение структуры сессий может повлиять на транзакционность (в будущем).
