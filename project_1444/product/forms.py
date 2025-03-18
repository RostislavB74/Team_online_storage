from django import forms

from product.models import Product, Categories  # Імпортуємо моделі

class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.category:
            category = self.instance.category
            if not category.has_length:
                self.fields.pop("length", None)
            if not category.has_width:
                self.fields.pop("width", None)
            if not category.has_diameter:
                self.fields.pop("diameter", None)
            if not category.has_weight:
                self.fields.pop("weight", None)

        self.fields["categories"].queryset = Categories.objects.filter(has_length=True, has_width=True, has_diameter=True, has_weight=True)