from typing import Optional


def create_order_by(order_by: Optional[str] = None):
    if order_by is None:
        return ""

    return f" order by {order_by}"
