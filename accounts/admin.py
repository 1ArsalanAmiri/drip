from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserAddress, OTP

# ---------------------------
# User Admin
# ---------------------------
class UserAddressInline(admin.TabularInline):
    model = UserAddress
    extra = 0
    readonly_fields = ('created_at', 'updated_at')
    can_delete = True

class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("id", "phone_number", "first_name", "last_name", "email", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("phone_number", "first_name", "last_name", "email")
    ordering = ("id",)
    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "password1", "password2", "is_staff", "is_active")}
        ),
    )
    inlines = [UserAddressInline]

# ---------------------------
# OTP Admin ساده
# ---------------------------
class OTPAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "code", "created_at")
    search_fields = ("phone_number", "code")
    readonly_fields = ("phone_number", "code", "created_at")  # فقط مشاهده

# ---------------------------
# ثبت در پنل
# ---------------------------
admin.site.register(User, UserAdmin)
admin.site.register(OTP, OTPAdmin)
