def export(rows):
    return "\n".join(
        f"{r['id']}:{r['v']}" for r in sorted(rows, key=lambda row: row['id'])
    )
