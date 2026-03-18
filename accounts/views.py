from django.shortcuts import render

# for login/logout
from django.shortcuts import render, redirect # type: ignore

#adjusting my custom signup dialog to include more parameters
from accounts.forms import CustomUserCreationForm
from django.contrib.auth.models import Group



# signup replacement 
def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # assign group
            customer_group = Group.objects.get(name="customer")
            user.groups.add(customer_group)

            return redirect("login")
    else:
        form = CustomUserCreationForm()
    return render(request, "signup.html", {"form": form})



