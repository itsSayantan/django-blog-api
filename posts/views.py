from django.http import HttpResponse

def posts(request):
    return HttpResponse('Posts page received')
