from django.shortcuts import render

# Create your views here.
def admin(request):
    return render(request, 'admin.html')

def admin_register(request):
    return render(request, 'admin_register.html')