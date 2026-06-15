from flask import request
from typing import Callable

DEFAULT_PAGE_SIZE = 50
MAX_PAGE_SIZE = 200


def paginate(query, serialiser: Callable):
    """
    Reads `page` and `per_page` from the query string, paginates `query`,
    and returns a dict suitable for jsonify().

    Args:
        query:       A SQLAlchemy Query object (not yet .all()'d).
        serialiser:  A callable applied to each row, e.g. lambda r: r.to_dict()

    Returns a dict:
        {
            "items":    [...],
            "page":     1,
            "per_page": 50,
            "total":    123,
            "pages":    3,
        }
    """
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (TypeError, ValueError):
        page = 1

    try:
        per_page = min(
            MAX_PAGE_SIZE,
            max(1, int(request.args.get("per_page", DEFAULT_PAGE_SIZE))),
        )
    except (TypeError, ValueError):
        per_page = DEFAULT_PAGE_SIZE

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "items": [serialiser(item) for item in pagination.items],
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }
