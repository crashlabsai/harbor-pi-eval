def export(rows):
    """Format rows as ``id:v`` lines ordered by ascending id."""
    return "\n".join(f"{row['id']}:{row['v']}" for row in sorted(rows, key=lambda row: row["id"]))
