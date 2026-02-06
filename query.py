async def json_to_sql(data: dict):
    entity = data.get("entity")
    aggregation = data.get("aggregation", "sum").upper()
    field = data.get("field", "*")
    filters = data.get("filters", {})

    where_clauses = []
    params = {}

    if aggregation == "COUNT":
        field = "*"

    date_column = "created_at" if entity == "video_snapshots" else "video_created_at"

    if not filters.get("all_time"):
        start = filters.get("start_date")
        end = filters.get("end_date")
        specific_date = filters.get("date")

        if start and end:
            start_clean = str(start).replace("T", " ")
            end_clean = str(end).replace("T", " ")

            if ":" in start_clean:
                where_clauses.append(f"{date_column} >= %(start_date)s")
                where_clauses.append(f"{date_column} <= %(end_date)s")
            else:
                where_clauses.append(f"DATE({date_column}) BETWEEN %(start_date)s AND %(end_date)s")

            params["start_date"] = start_clean
            params["end_date"] = end_clean

        elif specific_date:
            where_clauses.append(f"DATE({date_column}) = %(date)s")
            params["date"] = specific_date

    if filters.get("creator_id"):
        if entity == "video_snapshots":
            where_clauses.append(f"video_id IN (SELECT id FROM videos WHERE creator_id = %(creator_id)s)")
        else:
            where_clauses.append("creator_id = %(creator_id)s")
        params["creator_id"] = str(filters["creator_id"])

    if filters.get("negative_only"):
        target_filter = "delta_views_count" if entity == "video_snapshots" else "views_count"
        where_clauses.append(f"{target_filter} < 0")

    if filters.get("min_views"):
        prefix = "video_id IN (SELECT id FROM videos WHERE " if entity == "video_snapshots" else ""
        suffix = ")" if entity == "video_snapshots" else ""
        where_clauses.append(f"{prefix}views_count >= %(min_views)s{suffix}")
        params["min_views"] = int(filters["min_views"])

    where_str = f" WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    query = f"SELECT {aggregation}({field}) FROM {entity}{where_str};"

    return query, params
