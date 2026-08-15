from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout


# =========================================================
# LOGIN
# =========================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect('dashboard')

    error = None

    if request.method == 'POST':

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            return redirect('dashboard')

        error = 'Invalid username or password.'

    return render(
        request,
        'accounts/login.html',
        {
            'error': error
        }
    )


# =========================================================
# LOGOUT
# =========================================================

def logout_view(request):

    logout(request)

    return redirect('login')