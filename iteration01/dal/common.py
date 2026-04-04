class DALNotFound(Exception):
    pass

class DALConflict(Exception):
    pass

def safe_order_by(sort, direction, allowed_cols):
    # ORDER BY cannot be parameterized so we can whitelist it
    if sort not in allowed_cols:
        sort = "id"

    direction = (direction or "").upper()
    if direction not in ("ASC", "DESC"):
        direction = "DESC"

    return sort, direction