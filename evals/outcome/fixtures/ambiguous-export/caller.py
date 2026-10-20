from exporter import export_rows


def export_clicked(session, query, page, rows):
    return export_rows(rows, session.tenant_id, query.matches, page)
