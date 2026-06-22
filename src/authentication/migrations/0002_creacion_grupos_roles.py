from django.db import migrations

def crear_grupos(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    roles = ['Administrador', 'Coach', 'Gymbro']
    for rol in roles:
        Group.objects.get_or_create(name=rol)

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0001_initial'), 
    ]

    operations = [
        migrations.RunPython(crear_grupos),
    ]