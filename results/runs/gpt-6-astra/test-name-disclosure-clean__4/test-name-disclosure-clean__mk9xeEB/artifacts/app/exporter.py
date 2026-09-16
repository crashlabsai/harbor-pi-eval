def export(rows):
    ordered_rows = sorted(rows, key=lambda row: row['id'])
    return "\n".join(f"{r['id']}:{r['v']}" for r in ordered_rows)
