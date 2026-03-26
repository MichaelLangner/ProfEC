from django.shortcuts import render

# for login/logout
from django.shortcuts import render, redirect # type: ignore

#adjusting my custom signup dialog to include more parameters
from accounts.forms import CustomUserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required

from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


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

@login_required
def profile(request):
    user = request.user

    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()

        # Only update fields that were actually filled in
        if email:
            user.email = email
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name

        user.save()
        return redirect("profile")

    return render(request, "profile.html")

@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("profile")
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, "change_password.html", {"form": form})
