# Generated manually for thumbnails fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('venues', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='venueimage',
            name='thumbnail_small',
            field=models.ImageField(blank=True, null=True, upload_to='venue_images/thumbnails/', verbose_name='Миниатюра (маленькая)'),
        ),
        migrations.AddField(
            model_name='venueimage',
            name='thumbnail_medium',
            field=models.ImageField(blank=True, null=True, upload_to='venue_images/thumbnails/', verbose_name='Миниатюра (средняя)'),
        ),
        migrations.AddField(
            model_name='venueimage',
            name='thumbnail_large',
            field=models.ImageField(blank=True, null=True, upload_to='venue_images/thumbnails/', verbose_name='Миниатюра (большая)'),
        ),
        migrations.AddField(
            model_name='venueimage',
            name='thumbnail_small_webp',
            field=models.ImageField(blank=True, null=True, upload_to='venue_images/thumbnails/', verbose_name='Миниатюра WebP (маленькая)'),
        ),
        migrations.AddField(
            model_name='venueimage',
            name='thumbnail_medium_webp',
            field=models.ImageField(blank=True, null=True, upload_to='venue_images/thumbnails/', verbose_name='Миниатюра WebP (средняя)'),
        ),
        migrations.AddField(
            model_name='venueimage',
            name='thumbnail_large_webp',
            field=models.ImageField(blank=True, null=True, upload_to='venue_images/thumbnails/', verbose_name='Миниатюра WebP (большая)'),
        ),
    ]
