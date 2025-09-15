from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserAddress, OTP
from django import forms

# ---------------------------
# User Admin
# ---------------------------
class OTPInline(admin.TabularInline):
    model = OTP
    extra = 0
    readonly_fields = ('code', 'created_at')

class UserAddressInlineForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = '__all__'
        widgets = {
            'address_line': forms.Textarea(attrs={'rows': 2, 'cols': 40}),
        }

class UserAddressInline(admin.TabularInline):
    model = UserAddress
    form = UserAddressInlineForm
    extra = 0
    fields = ('full_name', 'phone_number', 'postal_code', 'address_line', 'city', 'province')
    readonly_fields = ('created_at', 'updated_at')


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
        # ("Important dates", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("phone_number", "password1", "password2", "is_staff", "is_active")}
        ),
    )
    inlines = [UserAddressInline , OTPInline]



# ---------------------------
# OTP Admin ساده
# ---------------------------
class OTPAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "code", "created_at")
    search_fields = ("phone_number", "code")
    readonly_fields = ("phone_number", "code", "created_at")

# ---------------------------




# ثبت در پنل
# ---------------------------
admin.site.register(User, UserAdmin)
admin.site.register(OTP, OTPAdmin)


