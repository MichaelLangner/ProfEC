from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test # type: ignore

# define decorators
def group_required(group_name):
    return user_passes_test(lambda user: user.is_authenticated and (user.groups.filter(name=group_name).exists() or user.is_superuser))

def groups_required(*group_names):
    def check(user):
        return user.is_authenticated and (user.groups.filter(name__in=group_names).exists() or user.is_superuser)
    return user_passes_test(check)

# index dummy
def index(request):
    return render(request,"index.html")

def try_float(v):
   
   try:
       return float(v)
   except Exception:
       return 'nan'

