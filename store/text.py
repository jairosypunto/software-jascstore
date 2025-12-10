from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal

from .models import Product, Factura, DetalleFactura

class FlujoCompraTest(TestCase):
    def setUp(self):
        # Crear usuario de prueba
        self.user = User.objects.create_user(username="jairo", email="jairo@test.com", password="12345")
        self.client = Client()
        self.client.login(username="jairo", password="12345")

        # Crear producto de prueba
        self.producto = Product.objects.create(
            name="Camisa Elegante",
            slug="camisa-elegante",
            cost=Decimal("40000"),
            discount=5,
            sizes="S,M,L,XL",
            colors="Blanco,Negro,Rojo",
            stock=10,
            is_available=True
        )

    def test_agregar_al_carrito_y_generar_factura(self):
        # 1. Agregar producto al carrito
        response = self.client.post(reverse("store:agregar_al_carrito", args=[self.producto.id]), {
            "cantidad": 2,
            "selected_size": "M",
            "selected_color": "Negro"
        })
        self.assertEqual(response.status_code, 302)  # redirección al carrito

        # 2. Ver carrito
        response = self.client.get(reverse("store:ver_carrito"))
        self.assertContains(response, "Camisa Elegante")
        self.assertContains(response, "Talla: M")
        self.assertContains(response, "Color: Negro")

        # 3. Generar factura
        response = self.client.post(reverse("store:generar_factura"), {
            "metodo_pago": "Tarjeta",
            "banco": "Bancolombia"
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/factura_detalle.html")

        # 4. Validar que la factura se creó
        factura = Factura.objects.first()
        self.assertIsNotNone(factura)
        self.assertEqual(factura.usuario, self.user)

        # 5. Validar detalle de factura
        detalle = DetalleFactura.objects.first()
        self.assertEqual(detalle.producto, self.producto)
        self.assertEqual(detalle.talla, "M")
        self.assertEqual(detalle.color, "Negro")
        self.assertEqual(detalle.cantidad, 2)

    def test_descargar_factura_pdf(self):
        # Crear factura manualmente
        factura = Factura.objects.create(
            usuario=self.user,
            total=Decimal("76000"),
            metodo_pago="Tarjeta",
            estado_pago="Pagado",
            banco="Bancolombia"
        )
        DetalleFactura.objects.create(
            factura=factura,
            producto=self.producto,
            cantidad=1,
            subtotal=Decimal("38000"),
            talla="L",
            color="Blanco"
        )

        # Descargar PDF
        response = self.client.get(reverse("store:generar_factura_pdf", args=[factura.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")