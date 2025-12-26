# store/forms.py
from django import forms

class CheckoutForm(forms.Form):
    nombre = forms.CharField(label="Nombre completo", max_length=150)
    email = forms.EmailField(label="Correo electrónico")
    telefono = forms.CharField(label="Teléfono de contacto", max_length=30)
    direccion = forms.CharField(label="Dirección de entrega", max_length=255)
    ciudad = forms.CharField(label="Ciudad", max_length=120)
    departamento = forms.CharField(label="Departamento", max_length=120)
    metodo_pago = forms.ChoiceField(
        label="Método de pago",
        choices=[
            ("banco", "Pago por banco"),
            ("contraentrega", "Contraentrega")
        ],
        required=True
    )