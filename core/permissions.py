from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdmin(BasePermission):
    message = "Ця дія доступна лише адміністратору."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsAdminOrReadOnly(IsAdmin):
    """Читати можуть усі, змінювати - лише адміністратор."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)


class IsOwnerOrAdmin(BasePermission):
    """Доступ до об'єкта має його власник (поле user) або адміністратор."""

    message = "Ви не маєте доступу до цього об'єкта."

    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or getattr(obj, "user_id", None) == request.user.id
