from django.db import models
from bot.validators import validate_positive
# Create your models here.


class User(models.Model):
    """User of the bot"""
    chat_id = models.IntegerField(unique=True, null=False, db_index=True)
    last_name = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=100, null=True)
    username = models.CharField(max_length=100, null=True)
    telephone = models.CharField(max_length=15, null=True, db_index=True)

    def __str__(self):
        return f'{self.chat_id}: {self.first_name} {self.last_name}, {self.username}, {self.telephone}'


class Product(models.Model):
    """Product of the shop"""
    name_external = models.CharField(max_length=150, null=False, unique=True)
    name_internal = models.CharField(max_length=150, null=False, unique=True)
    count = models.IntegerField(null=False, validators=[validate_positive])
    price = models.IntegerField(null=False, validators=[validate_positive])

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.name_internal = str.lower(self.name_external)
        super().save()

    def __str__(self):
        return f'{self.name_external}, count: {self.count}, price: {self.price}'



