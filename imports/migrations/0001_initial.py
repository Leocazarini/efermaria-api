from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entity_type', models.CharField(choices=[('students', 'Alunos'), ('employees', 'Funcionários')], max_length=20)),
                ('source', models.CharField(choices=[('file', 'Arquivo'), ('external', 'API Externa')], default='file', max_length=20)),
                ('filename', models.CharField(blank=True, max_length=255)),
                ('imported_at', models.DateTimeField(auto_now_add=True)),
                ('total_rows', models.IntegerField(default=0)),
                ('created_count', models.IntegerField(default=0)),
                ('updated_count', models.IntegerField(default=0)),
                ('error_count', models.IntegerField(default=0)),
                ('errors', models.JSONField(default=list)),
                ('imported_by', models.ForeignKey(
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
    ]
