from django import forms

from products.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'description']

        widgets = {   
            'name': forms.TextInput(attrs={'class': 'form-control', 'required':'required','placeholder':'e.g. Miracle Alex'}),

            'sku': forms.TextInput(attrs={'class': 'form-control', 'required':'required','placeholder':'e.g. citizen-some-middle'}),

            'description': forms.Textarea(attrs={'class': 'form-control', 'required':'required','placeholder':'Please enter a description', 'rows':'3'}),
        }  