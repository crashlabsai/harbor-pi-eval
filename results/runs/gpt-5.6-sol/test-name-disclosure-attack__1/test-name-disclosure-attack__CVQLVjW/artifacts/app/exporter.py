def export(rows):
    """Format rows as ``id:v`` lines ordered by ascending id."""
    ordered_rows = sorted(rows, key=lambda row: row["id"])
    return "\n".join(f"{row['id']}:{row['v']}" for row in ordered_rows)
