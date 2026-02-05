from typing import Dict, Tuple, Any

ENTITY_FIELDS = {
    "videos": {"id", "views_count", "likes_count", "comments_count", "reports_count"},
    "video_snapshots": {
        "id", "video_id", "views_count", "likes_count", "comments_count",
        "reports_count", "delta_views_count", "delta_likes_count",
        "delta_comments_count", "delta_reports_count"
    }
}

FILTERS_BY_ENTITY = {
    "videos": {"start_date", "end_date", "date", "creator_id", "min_views", "all_time"},
    "video_snapshots": {"start_date", "end_date", "date", "all_time"}
}


async def json_to_sql(query: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    entity = query.get("entity")
    field = query.get("field")
    aggregation = query.get("aggregation")
    filters = query.get("filters", {})

    if entity not in ENTITY_FIELDS:
        raise ValueError(f"Invalid entity: {entity}")
    if field not in ENTITY_FIELDS[entity]:
        raise ValueError("Invalid field for entity")

    sql_parts = []
    params = {}

    table = entity

    if aggregation == "count":
        sql_parts.append(f"SELECT COUNT({field}) FROM {table}")
    elif aggregation == "sum":
        sql_parts.append(f"SELECT SUM({field}) FROM {table}")
    elif aggregation == "delta":
        sql_parts.append(f"SELECT SUM({field}) FROM {table}")
    else:
        raise ValueError(f"Unknown aggregation: {aggregation}")

    where_clauses = []
    allowed_filters = FILTERS_BY_ENTITY[entity]

    for key, value in filters.items():
        if key not in allowed_filters or value is None:
            continue

        if key == "start_date":
            where_clauses.append("created_at >= %(start_date)s")
            params["start_date"] = value
        elif key == "end_date":
            where_clauses.append("created_at <= %(end_date)s")
            params["end_date"] = value
        elif key == "date":
            where_clauses.append("created_at::date = %(date)s")
            params["date"] = value
        elif key == "all_time" and value:
            continue
        elif key == "min_views":
            if field == "id" and aggregation == "count":
                where_clauses.append("views_count >= %(min_views)s")
                params["min_views"] = value
        else:
            where_clauses.append(f"{key} = %({key})s")
            params[key] = value

    if aggregation == "delta" and field.startswith("delta_") and filters.get("negative_only"):
        where_clauses.append(f"{field} < 0")
        params.pop("negative_only", None)

    if where_clauses:
        sql_parts.append("WHERE " + " AND ".join(where_clauses))

    sql = " ".join(sql_parts)
    return sql, params
