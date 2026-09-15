def export(rows):
    # BUG: rows are not ordered by id before formatting.
    return "\n".join(f"{r['id']}:{r['v']}" for r in rows)
