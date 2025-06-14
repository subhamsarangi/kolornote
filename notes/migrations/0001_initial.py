# Generated by Django 4.2.21 on 2025-06-04 14:01

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('hex_value', models.CharField(max_length=7, validators=[django.core.validators.RegexValidator(message='Invalid hex color', regex='^#[0-9A-Fa-f]{6}$')])),
                ('is_default', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='colors', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('owner', 'hex_value')},
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('note_type', models.CharField(choices=[('note', 'Note'), ('checklist', 'Checklist')], default='note', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='notes.color')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-modified_at'],
            },
        ),
    ]
