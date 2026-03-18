from django.db import migrations

def create_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.get_or_create(name="customer")
    Group.objects.get_or_create(name="admin")

class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"), 
    ]

    operations = [
        migrations.RunPython(create_groups),
    ]