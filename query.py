import asyncio
from typing import Dict, Any, Tuple, List

ALLOWED_ENTITIES = {"videos", "video_snapshots"}
ALLOWED_FIELDS = {
    "id", "creator_id", "views_count", "likes_count", "comments_count", "reports_count",
    "delta_views_count", "delta_likes_count", "delta_comments_count", "delta_reports_count"
}
ALLOWED_AGGR = {"count", "sum", "avg", "max", "min"}


def json_to_sql(data: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    if "error" in data:
        raise ValueError(f"LLM returned error: {data['error']}")

    entity = data.get("entity")
    aggregation = data.get("aggregation", "count").lower()
    field = data.get("field", "id")
    filters = data.get("filters", {})

    if entity not in ALLOWED_ENTITIES:
        raise ValueError(f"Invalid entity: {entity}")
    if aggregation not in ALLOWED_AGGR:
        raise ValueError(f"Invalid aggregation: {aggregation}")
    if field not in ALLOWED_FIELDS and field != "*":
        raise ValueError(f"Invalid field: {field}")

    if aggregation == "count":
        sql_select = f"SELECT COUNT({field})"
    else:
        sql_select = f"SELECT {aggregation.upper()}({field})"

    sql_from = f"FROM {entity}"

    where_clauses = []
    params = {}

    date_column = "created_at" if entity == "video_snapshots" else "video_created_at"
    filters = data.get("filters", {})

    if not filters.get("all_time"):
        if filters.get("date"):
            where_clauses.append(f"DATE({date_column}) = %(date)s")
            params["date"] = filters["date"]
        elif filters.get("start_date") and filters.get("end_date"):
            where_clauses.append(f"DATE({date_column}) BETWEEN %(start_date)s AND %(end_date)s")
            params["start_date"] = filters["start_date"]
            params["end_date"] = filters["end_date"]

    if filters.get("creator_id"):
        where_clauses.append("creator_id = %(creator_id)s")
        params["creator_id"] = str(filters["creator_id"])

    if filters.get("min_views"):
        where_clauses.append("views_count >= %(min_views)s")
        params["min_views"] = int(filters["min_views"])

    if filters.get("negative_only"):
        if entity == "video_snapshots":
            target_filter_field = field if "delta" in str(field) else "delta_views_count"
            where_clauses.append(f"{target_filter_field} < 0")
        else:
            where_clauses.append("views_count < 0")

    where_str = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"SELECT {aggregation.upper()}({field}) FROM {entity}{where_str};"

    return query, params
