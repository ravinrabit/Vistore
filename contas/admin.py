from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):

    ordering = ["nome"]
    list_display = ["nome", "email", "perfil", "unidade", "is_active"]
    list_filter = ["perfil", "unidade", "is_active"]
    search_fields = ["nome", "email"]

    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Dados pessoais", {"fields": ["nome", "perfil", "unidade"]}),
        ("Permissões", {"fields": ["is_active", "is_staff", "is_superuser", "groups", "user_permissions"]}),
        ("Datas", {"fields": ["last_login", "date_joined"]}),
    ]
    add_fieldsets = [
        (None, {
            "classes": ["wide"],
            "fields": ["email", "nome", "perfil", "unidade", "password1", "password2"],
        }),
    ]
