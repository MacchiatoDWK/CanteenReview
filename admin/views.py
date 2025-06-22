from django.shortcuts import render

# Create your views here.
def admin(request):
    return render(request, 'admin.html')

def admin_register(request):
    return render(request, 'admin_register.html')

def admin_canteen_manage(request):
    return render(request, 'admin_canteen_manage.html')