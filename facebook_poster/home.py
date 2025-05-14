from django.shortcuts import render

def home(request):
    return render(request, 'design/home.html')

def about(request):
    return render(request, 'design/about.html')

def contact(request):
    return render(request, 'design/contact.html')

def features(request):
    return render(request, 'design/features.html')
