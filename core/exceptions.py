from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.views import exception_handler


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Конфлікт з поточним станом даних."
    default_code = "conflict"


def custom_exception_handler(exc, context):
    """Повертає всі помилки API в єдиному форматі {"error": {...}}."""
    response = exception_handler(exc, context)
    if response is None:
        return None

    error = {"status": response.status_code}
    if isinstance(exc, ValidationError):
        error["message"] = "Некоректні дані. Перевірте поля запиту."
        error["details"] = response.data
    elif response.status_code == status.HTTP_401_UNAUTHORIZED:
        error["message"] = "Потрібно увійти в акаунт або оновити токен."
    else:
        detail = response.data.get("detail") if isinstance(response.data, dict) else None
        error["message"] = str(detail or "Сталася помилка.")

    response.data = {"error": error}
    return response
