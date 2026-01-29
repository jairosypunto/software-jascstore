from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0018_alter_factura_banco_alter_factura_ciudad_and_more'),
    ]

    operations = [
        # Añadir el campo que falta en DetalleFactura
        migrations.AddField(
            model_name='detallefactura',
            name='imagen_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        # Asegurar que color_vinculado exista antes de alterarlo
        migrations.AddField(
            model_name='productimage',
            name='color_vinculado_new', # Usamos un nombre temporal por seguridad
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]