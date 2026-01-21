from django.http import HttpResponse

def home(request):
    return HttpResponse("Jadwa AI is running")
