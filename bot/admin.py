from django.contrib import admin
from bot.models import User, Product
from django.forms import ModelForm
# Register your models here.


class ProductForm(ModelForm):
    class Meta:
        model = Product
        fields = ('name_external', 'price', 'count')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name_external', 'price', 'count', 'img_name')
    search_fields = ('name_external', 'name_internal', 'price', 'count')

    fieldsets = (
        (None, {
            'fields': ('name_external', 'price', 'count')
        }),
    )


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'first_name', 'last_name', 'username', 'telephone')
    search_fields = list_display
