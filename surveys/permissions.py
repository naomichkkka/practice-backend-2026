from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Редактировать/удалять опрос может только автор."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, 'author', None) == request.user


class IsSurveyAuthor(permissions.BasePermission):
    """Доступ только автору опроса (для аналитики, экспорта, publish/close)."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        survey = getattr(obj, 'survey', obj)
        return survey.author == request.user
