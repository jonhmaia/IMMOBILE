from django.shortcuts import render, redirect
from .models import Immobile, ImmobileImage
from myapp.forms import ClientForm, ImmobileForm, RegisterLocationForm
from django.db.models import Q
import csv
from django.http import HttpResponse
import xlsxwriter
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


def form_location(request, id):
    get_locate = Immobile.objects.get(id=id) ## pega objeto
    form = RegisterLocationForm()  
    if request.method == 'POST':
        form = RegisterLocationForm(request.POST)
        if form.is_valid():
            location_form = form.save(commit=False)
            location_form.immobile = get_locate ## salva id do imovel 
            location_form.save() 
            immo = Immobile.objects.get(id=id)
            immo.is_locate = True ## passa ser True
            immo.save() 
      
            return redirect('list-location') # Retorna para lista
    context = {'form': form, 'location': get_locate}
    return render(request, 'form-location.html', context)




def reports(request):
    immobile = Immobile.objects.all()
    if 'export' in request.GET:
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="relatorio.xlsx"'
        
        workbook = xlsxwriter.Workbook(response)
        worksheet = workbook.add_worksheet()
        
        # Defina o cabeçalho
        header = ['ID', 'Registro Inicial', 'Registro Final', 'Cliente', 'Codigo', 'Imovel', 'Valor', 'Locado']
        for col, value in enumerate(header):
            worksheet.write(0, col, value)
        
        # Escreva os dados
        row = 1
        for immobile in immobile:
            for location in immobile.reg_location.all():
                worksheet.write(row, 0, immobile.id)
                worksheet.write(row, 1, location.dt_start.strftime('%d/%m/%Y'))
                worksheet.write(row, 2, location.dt_end.strftime('%d/%m/%Y'))
                worksheet.write(row, 3, location.client.name)  # Acessando o atributo name do modelo Client
                worksheet.write(row, 4, immobile.code)
                worksheet.write(row, 5, immobile.type_item)
                worksheet.write(row, 6, immobile.price)
                worksheet.write(row, 7, 'LOCADO' if immobile.is_locate else 'NÃO LOCADO')
                row += 1
        
        workbook.close()
        return response
     # Se a requisição é para exportar como CSV
    if 'export' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="relatorio.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['ID', 'Registro Inicial', 'Registro Final', 'Cliente', 'Codigo', 'Imovel', 'Valor', 'Locado'])
        
        for immobile in immobile:
            for location in immobile.reg_location.all():
                writer.writerow([immobile.id, location.dt_start.strftime('%d/%m/%Y'), location.dt_end.strftime('%d/%m/%Y'), location.client, immobile.code, immobile.type_item, immobile.price, 'LOCADO' if immobile.is_locate else 'NÃO LOCADO'])
        
        return response
    
    get_client = request.GET.get('client') 
    get_locate = request.GET.get('is_locate')
    get_type_item = request.GET.get('type_item') 

    get_dt_start = request.GET.get('dt_start')
    get_dt_end = request.GET.get('dt_end')
    print(get_dt_start, get_dt_end)

    if get_client: ## Filtra por nome e email do cliente
        immobile = Immobile.objects.filter(
            Q(reg_location__client__name__icontains=get_client) | 
            Q(reg_location__client__email__icontains=get_client))
    
    if get_dt_start and get_dt_end: ## Por data
        immobile = Immobile.objects.filter(
            reg_location__create_at__range=[get_dt_start,get_dt_end])

    if get_locate:
        immobile = Immobile.objects.filter(is_locate=get_locate)

    if get_type_item:
        immobile = Immobile.objects.filter(type_item=get_type_item)

    return render(request, 'reports.html', {'immobiles': immobile})
