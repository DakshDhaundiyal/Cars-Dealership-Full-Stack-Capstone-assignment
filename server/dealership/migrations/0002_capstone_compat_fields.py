from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("dealership", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="dealer",
            name="short_name",
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name="dealer",
            name="full_name",
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AddField(
            model_name="dealer",
            name="zip",
            field=models.CharField(default="00000", max_length=12),
        ),
        migrations.AddField(
            model_name="dealer",
            name="lat",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="dealer",
            name="long",
            field=models.FloatField(default=0.0),
        ),
        migrations.AddField(
            model_name="dealerreview",
            name="purchase",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="dealerreview",
            name="purchase_date",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="dealerreview",
            name="car_make",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.AddField(
            model_name="dealerreview",
            name="car_model",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.AddField(
            model_name="dealerreview",
            name="car_year",
            field=models.PositiveSmallIntegerField(default=2025),
        ),
    ]
