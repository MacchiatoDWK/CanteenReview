from django.shortcuts import render

# Create your views here.
def admin(request):
    return render(request, 'admin.html')

def admin_register(request):
    return render(request, 'admin_register.html')

def admin_canteen_manage(request):
    return render(request, 'admin_canteen_manage.html')

def admin_center(request):
    return render(request, 'admin_center.html')

def admin_message_center(request):
    return render(request, 'admin_message_center.html')