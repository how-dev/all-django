from import_export import resources, fields
from import_export.widgets import DateTimeWidget, CharWidget
from .models import FinalUserModel


class UserResource(resources.ModelResource):
    id = fields.Field(
        attribute="id",
        column_name="User ID",
        widget=CharWidget()
    )
    last_login = fields.Field(
        attribute="last_login",
        column_name="Last Login",
        widget=DateTimeWidget()
    )
    is_active = fields.Field(
        attribute="is_active",
        column_name="Is Active",
        widget=CharWidget()
    )
    date_joined = fields.Field(
        attribute="date_joined",
        column_name="Date Joined",
        widget=DateTimeWidget()
    )
    email = fields.Field(
        attribute="email",
        column_name="Email",
        widget=CharWidget()
    )
    name = fields.Field(
        attribute="name",
        column_name="Name",
        widget=CharWidget()
    )

    class Meta:
        model = FinalUserModel
        fields = [
            "id",
            "last_login",
            "is_active",
            "date_joined",
            "email",
            "name"
        ]
        export_order = fields
