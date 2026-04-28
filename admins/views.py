from django.shortcuts import render,redirect
from django.contrib import messages
from users.models import UserRegistration

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username == 'admin' and password == 'admin':
            return render(request, 'admins/adminhome.html')
        else:
            messages.success(request, 'Invalid username or password')
    return render(request, 'adminlogin.html')

def admin_home(request):
    return render(request, 'admins/adminhome.html')

def view(request):
    users = UserRegistration.objects.all()
    return render(request, 'admins/view.html', {'users': users})

def activate_user(request, user_id):
    user = UserRegistration.objects.get(id=user_id)
    user.status = 'active'
    user.save()
    return redirect('view')

def block_user(request, user_id):
    user = UserRegistration.objects.get(id=user_id)
    user.status = 'waiting'
    user.save()
    return redirect('view')

def delete_user(request, user_id):
    user = UserRegistration.objects.get(id=user_id)
    user.delete()
    return redirect('view')
