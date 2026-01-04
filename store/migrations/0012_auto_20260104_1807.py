from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_update_storage'),  # ajusta al último archivo que tengas
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(upload_to='products/', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='video_thumb',
            field=models.ImageField(upload_to='video_thumbs/', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='video_file',
            field=models.FileField(upload_to='videos/products/', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='banner',
            name='image',
            field=models.ImageField(upload_to='banners/', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='productimage',
            name='image',
            field=models.ImageField(upload_to='products/', blank=True, null=True),
        ),
    ]