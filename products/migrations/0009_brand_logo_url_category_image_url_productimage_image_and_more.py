
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0008_wishlist"),
    ]

    operations = [
        migrations.RenameField(
            model_name="brand",
            old_name="logo",
            new_name="logo_url",
        ),
        migrations.RenameField(
            model_name="category",
            old_name="image",
            new_name="image_url",
        ),
        migrations.RenameField(
            model_name="storesettings",
            old_name="logo",
            new_name="logo_url",
        ),
        migrations.AddField(
            model_name="productimage",
            name="image",
            field=models.ImageField(
                upload_to="products/",
                blank=True,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="brand",
            name="logo",
            field=models.ImageField(
                upload_to="brands/",
                blank=True,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="image",
            field=models.ImageField(
                upload_to="categories/",
                blank=True,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="storesettings",
            name="logo",
            field=models.ImageField(
                upload_to="store/",
                blank=True,
                null=True,
            ),
        ),

        migrations.AlterField(
            model_name="productimage",
            name="image_url",
            field=models.URLField(
                blank=True,
                null=True,
            ),
        ),
    ]
