from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import User, Team
from .forms import ProfileForm


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


@login_required
def profile_edit(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("accounts:profile")
    return render(request, "accounts/profile_edit.html", {"form": form})


@login_required
def user_list(request):
    users = User.objects.all().order_by("first_name")
    return render(request, "accounts/user_list.html", {"users": users})


@login_required
def team_list(request):
    teams = Team.objects.select_related("leader").prefetch_related("members").all()
    return render(request, "accounts/team_list.html", {"teams": teams})
