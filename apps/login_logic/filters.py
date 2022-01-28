from django_filters import rest_framework as filters

from apps.login_logic.models import FinalUserModel


class FinalUserFilter(filters.FilterSet):
    id = filters.NumberFilter(field_name="id")
    last_login = filters.DateTimeFilter(field_name="last_login", lookup_expr="gte")
    is_active = filters.BooleanFilter(field_name="is_active")
    date_joined = filters.DateTimeFilter(field_name="date_joined", lookup_expr="gte")
    email = filters.CharFilter(field_name="email", lookup_expr="icontains")
    name = filters.CharFilter(field_name="name", lookup_expr="icontains")
    has_no_document = filters.BooleanFilter(field_name="document", lookup_expr="isnull")

    class Meta:
        model = FinalUserModel
        fields = [
            "id",
            "last_login",
            "is_active",
            "date_joined",
            "email",
            "name",
            "has_no_document",
        ]
