async def json_to_sql(data: dict):
    entity = data.get("entity", "videos")
    aggregation = data.get("aggregation", "count").upper()
    field = data.get("field", "*")
    is_distinct = data.get("is_distinct", False)
    filters = data.get("filters", {})

    where_clauses = []
    params = {}

    if entity == "video_snapshots":
        date_column = "created_at"
    else:
        date_column = "video_created_at"

    if aggregation == "COUNT":
        if is_distinct:
            target_field = f"DISTINCT {field}"
        else:
            target_field = "*"
    else:
        target_field = field

    if not filters.get("all_time"):
        start = filters.get("start_date")
        end = filters.get("end_date")
        specific_date = filters.get("date")

        if start and end:
            if "00:00:00" in str(start) and ("23:59:59" in str(end) or "00:00:00" in str(end)):
                where_clauses.append(f"DATE({date_column}) BETWEEN %(start_date)s AND %(end_date)s")
            elif ":" in str(start):
                where_clauses.append(f"{date_column} >= %(start_date)s AND {date_column} <= %(end_date)s")
            else:
                where_clauses.append(f"DATE({date_column}) BETWEEN %(start_date)s AND %(end_date)s")

            params["start_date"] = start
            params["end_date"] = end

        elif specific_date:
            where_clauses.append(f"DATE({date_column}) = %(date)s")
            params["date"] = specific_date

    if filters.get("creator_id"):
        if entity == "video_snapshots":
            where_clauses.append("video_id IN (SELECT id FROM videos WHERE creator_id = %(creator_id)s)")
        else:
            where_clauses.append("creator_id = %(creator_id)s")
        params["creator_id"] = str(filters["creator_id"])

    if filters.get("min_views"):
        if entity == "videos":
            where_clauses.append("views_count >= %(min_views)s")
        else:
            where_clauses.append("video_id IN (SELECT id FROM videos WHERE views_count >= %(min_views)s)")
        params["min_views"] = int(filters["min_views"])

    if filters.get("negative_only"):
        where_clauses.append("delta_views_count < 0")

    where_str = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"SELECT {aggregation}({target_field}) FROM {entity}{where_str};"

    return query, params
