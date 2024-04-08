from django.shortcuts import render, redirect
from .models import Immobile, ImmobileImage
from myapp.forms import ClientForm, ImmobileForm

def list_location(request):
    immobiles = Immobile.objects.filter(is_locate=False)
    context = {
        'immobiles': immobiles,
    }
    return render(request, 'list-location.html', context)

def form_client(request):
    form = ClientForm() 
    #se o método não for post eu n crio o cliente
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list-location')   
    return render(request, 'form-client.html', {'form': form})
def form_immobile(request):
    form = ImmobileForm()
    if request.method == 'POST':
        form = ImmobileForm(request.POST, request.FILES)
        if form.is_valid():
            immobile = form.save()
            files = request.FILES.getlist('immobile') ## pega todas as imagens
            if files:
                for f in files:
                    ImmobileImage.objects.create( # cria instance para imagens
                        immobile=immobile, 
                        image=f)
            return redirect('list-location')  
    return render(request, 'form-immobile.html', {'form': form})




