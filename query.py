async def json_to_sql(data: dict):
    entity = data.get("entity", "videos")
    aggregation = data.get("aggregation", "count").upper()
    field = data.get("field", "*")
    is_distinct = data.get("is_distinct", False)
    filters = data.get("filters", {})

    where_clauses = []
    params = {}

    date_column = "created_at" if entity == "video_snapshots" else "video_created_at"

    if aggregation == "COUNT" and is_distinct:
        if "date" in field or "created_at" in field:
            target_field = f"DISTINCT DATE({date_column})"
        else:
            target_field = f"DISTINCT {field}"
    elif aggregation == "COUNT":
        target_field = "*"
    else:
        target_field = field

    if not filters.get("all_time"):
        start = filters.get("start_date")
        end = filters.get("end_date")

        if start and end:
            if ":" in str(start) or ":" in str(end):
                where_clauses.append(f"{date_column} BETWEEN %(start_date)s AND %(end_date)s")
            else:
                where_clauses.append(f"DATE({date_column}) BETWEEN DATE(%(start_date)s) AND DATE(%(end_date)s)")

            params["start_date"] = start
            params["end_date"] = end

    if filters.get("creator_id"):
        c_id = filters["creator_id"]
        if entity == "video_snapshots":
            where_clauses.append("video_id IN (SELECT id FROM videos WHERE creator_id = %(creator_id)s)")
        else:
            where_clauses.append("creator_id = %(creator_id)s")
        params["creator_id"] = str(c_id)
    if filters.get("min_views"):
        m_views = filters["min_views"]
        if entity == "videos":
            where_clauses.append("views_count > %(min_views)s")
        elif entity == "video_snapshots":
            where_clauses.append("views_count > %(min_views)s")

        params["min_views"] = int(m_views)
    if filters.get("negative_only") is True:
        if entity == "video_snapshots":
            where_clauses.append("delta_views_count < 0")
        else:
            where_clauses.append("views_count < 0")

    where_str = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"SELECT {aggregation}({target_field}) FROM {entity}{where_str};"

    return query, params
