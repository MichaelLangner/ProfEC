from django import template

register = template.Library()

@register.filter(name='has_any_group')
def has_any_group(user, group_names):
    if not user.is_authenticated:
        return False

    # group_names is a comma-separated string: "Admin,Staff,Editor"
    group_list = [name.strip() for name in group_names.split(",")]

    return user.groups.filter(name__in=group_list).exists()