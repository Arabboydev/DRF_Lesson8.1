from django import forms
from .models import Pages, Comments, SavedProduct, Products, Images


class PagesForm(forms.ModelForm):
    class Meta:
        model = Pages
        fields = ['category', 'name', 'description']


class ProductsForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['category', 'name', 'description', 'price', 'discount']


class ProductImagesForm(forms.Form):
    images = forms.FileField(widget=forms.FileInput(), required=False)

    class Meta:
        model = Images
        fields = ['image']


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['star_given', 'comment',]


class SavedProductForm(forms.ModelForm):
    class Meta:
        model = SavedProduct
        fields = ['product',]
