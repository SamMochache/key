from django.db import connection
from django.http import JsonResponse


def health_check(request):
    """Public deployment health endpoint with a lightweight DB check."""
    if request.method != "GET":
        return JsonResponse({"status": "error", "detail": "Method not allowed"}, status=405)

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
    except Exception:
        return JsonResponse(
            {"status": "error", "database": "unavailable"},
            status=503,
        )

    return JsonResponse({"status": "ok", "database": "ok"})
