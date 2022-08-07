# Generated by Django 4.0.4 on 2022-08-07 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='market_day',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.IntegerField()),
                ('status', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='sectors',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='users',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=50)),
                ('password', models.CharField(default='', max_length=50)),
                ('ifLogged', models.BooleanField(default=False)),
                ('token', models.CharField(default='', max_length=500, null=True)),
                ('available_funds', models.DecimalField(decimal_places=2, max_digits=5)),
                ('blocked_funds', models.DecimalField(decimal_places=2, max_digits=5)),
            ],
        ),
        migrations.CreateModel(
            name='stocks',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('total_volume', models.IntegerField()),
                ('unallocated', models.IntegerField()),
                ('price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('sector_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest_assignment.sectors')),
            ],
        ),
        migrations.CreateModel(
            name='orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bid_price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('type', models.CharField(max_length=4)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(max_length=20)),
                ('bid_volume', models.IntegerField()),
                ('executed_volume', models.IntegerField()),
                ('stock_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest_assignment.stocks')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest_assignment.users')),
            ],
        ),
        migrations.CreateModel(
            name='ohlcv',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock_id', models.IntegerField()),
                ('open', models.DecimalField(decimal_places=2, max_digits=5)),
                ('high', models.DecimalField(decimal_places=2, max_digits=5)),
                ('low', models.DecimalField(decimal_places=2, max_digits=5)),
                ('close', models.DecimalField(decimal_places=2, max_digits=5)),
                ('volume', models.IntegerField()),
                ('market_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest_assignment.market_day')),
            ],
        ),
        migrations.CreateModel(
            name='holdings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('volume', models.IntegerField()),
                ('bid_price', models.DecimalField(decimal_places=2, max_digits=5)),
                ('brought_on', models.DateField()),
                ('stock_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest_assignment.stocks')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rest_assignment.users')),
            ],
        ),
    ]
