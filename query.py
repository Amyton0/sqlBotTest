from typing import Dict, Any, Tuple, List

AGGREGATIONS = {"count", "sum", "delta"}

TABLES = {
    "videos": "videos",
    "video_snapshots": "video_snapshots"
}

FIELDS = {
    "videos": {
        "id",
        "views_count",
        "likes_count",
        "comments_count",
        "reports_count"
    },
    "video_snapshots": {
        "delta_views_count",
        "delta_likes_count",
        "delta_comments_count",
        "delta_reports_count"
    }
}


async def validate_query(query: Dict[str, Any]) -> None:
    if "aggregation" not in query:
        raise ValueError("Missing aggregation")

    if query["aggregation"] not in AGGREGATIONS:
        raise ValueError("Invalid aggregation")

    if "entity" not in query:
        raise ValueError("Missing entity")

    if query["entity"] not in TABLES:
        raise ValueError("Invalid entity")

    if "field" not in query:
        raise ValueError("Missing field")

    if query["field"] not in FIELDS[query["entity"]]:
        raise ValueError("Invalid field for entity")

    if "filters" in query and not isinstance(query["filters"], dict):
        raise ValueError("Filters must be an object")


async def build_where(entity: str, filters: Dict[str, Any]) -> Tuple[str, List[Any]]:
    clauses = []
    params = []

    if not filters:
        return "", []

    if "creator_id" in filters:
        clauses.append("creator_id = %s")
        params.append(filters["creator_id"])

    if "start_date" in filters:
        column = "video_created_at" if entity == "videos" else "created_at"
        clauses.append(f"{column} >= %s")
        params.append(filters["start_date"])

    if "end_date" in filters:
        column = "video_created_at" if entity == "videos" else "created_at"
        clauses.append(f"{column} <= %s")
        params.append(filters["end_date"])

    if "min_views" in filters:
        clauses.append("views_count > %s")
        params.append(filters["min_views"])

    if "date" in filters:
        clauses.append("DATE(created_at) = %s")
        params.append(filters["date"])

    where_sql = " WHERE " + " AND ".join(clauses) if clauses else ""
    return where_sql, params


async def json_to_sql(query: Dict[str, Any]) -> Tuple[str, List[Any]]:
    await validate_query(query)

    aggregation = query["aggregation"]
    entity = query["entity"]
    field = query["field"]
    filters = query.get("filters", {})

    table = TABLES[entity]
    where_sql, params = await build_where(entity, filters)

    if aggregation in {"count", "sum"}:
        sql_func = "COUNT" if aggregation == "count" else "SUM"
        sql = f"""
            SELECT {sql_func}({field})
            FROM {table}
            {where_sql}
        """
        return sql.strip(), params

    if aggregation == "delta":
        if entity != "video_snapshots":
            raise ValueError("Delta aggregation allowed only for video_snapshots")

        sql = f"""
            SELECT SUM({field})
            FROM video_snapshots
            {where_sql}
        """
        return sql.strip(), params

    raise ValueError()
