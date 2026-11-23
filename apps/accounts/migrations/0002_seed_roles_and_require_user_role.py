
from django.db import migrations, models
import django.db.models.deletion


def create_roles(apps, schema_editor):
    Role = apps.get_model('accounts', 'Role')

    role_names = [
        'Registered User',
        'Municipality Staff',
        'District Admin',
        'Superadmin',
    ]

    for role_name in role_names:
        Role.objects.get_or_create(role_name=role_name)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            create_roles,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='users',
                to='accounts.role',
            ),
        ),
    ]
