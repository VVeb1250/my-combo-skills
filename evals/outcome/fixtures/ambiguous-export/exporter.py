def export_rows(rows, tenant_id, predicate, page, page_size=20):
    visible = [row for row in rows if row["tenant_id"] == tenant_id and predicate(row)]
    start = page * page_size
    return visible[start : start + page_size]
