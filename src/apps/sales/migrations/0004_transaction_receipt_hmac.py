from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0003_transaction_receipt_payload"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="receipt_hmac",
            field=models.CharField(blank=True, db_index=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name="transaction",
            name="receipt_hmac_algo",
            field=models.CharField(default="HMAC-SHA256", max_length=32),
        ),
        migrations.AddField(
            model_name="transaction",
            name="receipt_hmac_created_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
