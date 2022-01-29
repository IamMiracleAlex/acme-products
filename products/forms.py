from django import forms

from products.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'sku', 'is_active', 'description']

        widgets = {   
            'name': forms.TextInput(attrs={'class': 'form-control', 'required':'required','placeholder':'e.g. Miracle Alex'}),

            'sku': forms.TextInput(attrs={'class': 'form-control', 'required':'required','placeholder':'e.g. citizen-some-middle'}),

            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', }),

            'description': forms.Textarea(attrs={'class': 'form-control', 'required':'required','placeholder':'Please enter a description', 'rows':'3'}),
        }  