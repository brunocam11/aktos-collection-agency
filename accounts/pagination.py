from rest_framework.pagination import CursorPagination


class AccountCursorPagination(CursorPagination):
    """
    Cursor-based pagination for accounts API.

    Cursor-based pagination provides several advantages:
    1. Consistent results when new items are added/removed
    2. Better performance with large datasets
    3. No duplicate records when paginating
    4. Cannot skip to arbitrary pages, which prevents deep pagination issues

    The trade-off is that users can't jump to specific page numbers.
    """

    page_size = 100
    ordering = ["created_at"]
    cursor_query_param = "cursor"
