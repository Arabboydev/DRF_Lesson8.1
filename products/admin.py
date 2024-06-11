from django.contrib import admin
from products import models


admin.site.register(models.Category)
admin.site.register(models.Pages)
admin.site.register(models.Products)
admin.site.register(models.Comments)
admin.site.register(models.SavedProduct)
admin.site.register(models.Images)
admin.site.register(models.CartItem)

