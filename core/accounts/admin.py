from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, Address
# Register your models here.


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0
    fk_name = 'user'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    list_display = (
        'id', 'email', 'is_superuser', 'is_active', 'is_verified', 'is_staff'
        )
    list_filter = ('is_superuser', 'is_active','is_verified', 'is_staff')
    search_fields = ('email',)
    ordering = ('email',)

    fieldsets = (
        ("Authentication", {
            "fields": (
                "email", "password",
                )
            }),

        ("Personal info", {
            "fields": (
                "first_name", "last_name",
            )
        }),

        ("Permissions", {
            "fields": (
                "is_staff", "is_active", "is_verified", "groups", "user_permissions"
                )
            }),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "user_permissions", "is_verified",
                "is_superuser"
            )}
        ),
    )

# admin.site.register(User, CustomUserAdmin)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'first_name', 'last_name', 'birth_date', 'created_date'
    )
    search_fields = ('user__email', 'last_name')
    readonly_fields = ('created_date', 'updated_date')
    list_select_related = ('user',)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'title', 'receiver_name', 'province',
        'city', 'is_default', 'created_date'
    )
    list_filter = ('province', 'city', 'is_default')
    search_fields = ('user__email', 'receiver_name', 'postal_code')
    list_select_related = ('user',)
    readonly_fields = ('created_date',)
    list_editable = ('is_default',)