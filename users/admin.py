from django.contrib import admin
from .models import User, OTPVerification

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'role', 'is_verified', 'email_verified', 'phone_verified']
    list_filter = ['role', 'is_verified', 'email_verified', 'phone_verified']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']

class OTPVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'phone_number', 'verification_type', 'is_verified', 'created_at', 'expires_at', 'is_expired']
    list_filter = ['verification_type', 'is_verified']
    search_fields = ['user__username', 'user__email', 'email', 'phone_number']
    readonly_fields = ['is_expired']

admin.site.register(User, UserAdmin)
admin.site.register(OTPVerification, OTPVerificationAdmin)
