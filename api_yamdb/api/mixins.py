from rest_framework import filters, mixins, viewsets

from .permissions import IsAdminOrReadOnly


class AdminViewSet(mixins.CreateModelMixin,
                   mixins.ListModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    """Кастомный вьюсет для создания, возвращения и удаления объектов."""
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
