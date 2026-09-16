from operator import itemgetter


def export(rows):
    ordered = list(rows)
    ordered.sort(key=itemgetter("id"))
    return "\n".join("%d:%s" % (r["id"], r["v"]) for r in ordered)
