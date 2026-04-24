from typing import Optional, Any
from datetime import date
from sqlalchemy import and_
from app.models.dtp import Accident

class CRUDBase:
    @staticmethod
    def _apply_accident_filters(
        query: Any,
        *,
        region_code: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        has_children: Optional[bool] = None,
        has_drunk: Optional[bool] = None,
    ) -> Any:
        """
        Применение общих фильтров для запросов ДТП.
        """
        filters = []
        if region_code:
            filters.append(Accident.region_code == region_code)
        if date_from:
            filters.append(Accident.date_dtp >= date_from)
        if date_to:
            filters.append(Accident.date_dtp <= date_to)
        if has_children is not None:
            filters.append(Accident.has_children == has_children)
        if has_drunk is not None:
            filters.append(Accident.has_drunk == has_drunk)
            
        if filters:
            query = query.where(and_(*filters))
        return query
