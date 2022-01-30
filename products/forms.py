from django import forms

from products.models import Product, WebHook


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

class WebHookForm(forms.ModelForm):
    class Meta:
        model = WebHook
        fields = ['name', 'action', 'url', 'http_method']

        widgets = {   
            'name': forms.TextInput(attrs={'class': 'form-control', 'required':'required','placeholder':'e.g. Product Creation'}),

            'action': forms.Select(attrs={'class': 'form-control', 'required':'required'}),

            'url': forms.URLInput(attrs={'class': 'form-control', }),

            'http_method': forms.Select(attrs={'class': 'form-control', 'required':'required',}),
        }  