import json

from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal
from datetime import date, datetime
from . import models
from .models import User, Diary_Menu, Category, Portion, Menu, Description
from .forms import DiaryForm, UserForm, DateForm
from .models import DiaryEntries
import plotly.express as px


def login(request):
    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "please check！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
        username = request.POST.get('user')
        password = request.POST.get('password')
        try:
            user = User.objects.get(name=username)
            if user.password == password:
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/index/')
            else:
                message = "password error！"
        except:
            message = "user error！"
    return render(request, 'iteration3/login.html',{'iteration3':'iteration3'})

def load_portion(request):
    category_id = request.GET.get('category')
    portion = Portion.objects.filter(category_id=category_id).order_by('name')
    return render(request, 'iteration3/portion_dropdown_list_options.html', {'portion': portion})

def load_description(request):
    category_id = request.GET.get('category')
    description = Description.objects.filter(category_id=category_id).order_by('name')
    return render(request, 'iteration3/description_dropdown_list_options.html', {'description': description})

def diary(request):
    category = Category.objects.values('id', 'name')
    portion = Portion.objects.values('id', 'name')
    description = Description.objects.values('id', 'name')
    return render(request, 'iteration3/diary1.html',
                  context={'category': category,
                           'portion': portion,'description':description})

# def create_view(request):
#     if request.method == "POST":
#         diary_entry = DiaryEntries.objects.all()
#         date = request.POST.get('date')
#         time = request.POST.get('time')
#         blood_sugar_level = request.POST.get('blood_sugar_level')
#         category = request.POST.get('category')
#         portion = request.POST.get('portion')
#         quantity = request.POST.get('quantity')
#         list_date=[]
#         if 'add_list' in request.POST:
#             for items in diary_entry:
#                 list_date.append(datetime.strftime(items.date,'%Y-%m-%d'))
#             if date not in list_date:
#                 DiaryEntries.objects.create(date=date,blood_sugar_level=blood_sugar_level,
#                                 carbohydrates=0.0,time=time,insulin=0.0)
#                 diaryentries_id = DiaryEntries.objects.filter(date = date).values('id')
#                 Diary_Menu.objects.create(date=date, time=time,
#                                           carbohydrates=0,
#                                           category=category, portion=portion,
#                                           quantity=quantity)
#                 Diary_Menu.objects.filter(date = date).update(diary_id=diaryentries_id[0]['id'])
#                 return redirect('/iteration3/diary/')
#             else:
#                 diaryentries_id = DiaryEntries.objects.filter(date = date).values('id')
#                 Diary_Menu.objects.create(date=date, time=time,
#                                           carbohydrates=0,
#                                           category=category, portion=portion,
#                                           quantity=quantity)
#                 Diary_Menu.objects.filter(date = date).update(diary_id=diaryentries_id[0]['id'])
#                 return redirect('/iteration3/diary/')
#         elif 'submit' in request.POST:
#             pass
#         return render(request, 'iteration3/list_view.html', context={'diary_entry': diary_entry,'date':date,'time':time,'blood_sugar_level':blood_sugar_level,
#                                                                      'category':category,'portion':portion,'quantity':quantity})
#     return render(request, 'iteration3/list_view.html',locals())

# Diary views.
def create_view(request):
    if request.method == "POST":
        cart = request.POST.get('cart_items')
        sub = request.POST.get('submit_items')
        if len(json.loads(cart)) != 0:
            cart = json.loads(cart)

            # Generate the diary_id.
            DiaryEntries.objects.create(date=cart[0]['date'], time=cart[0]['time'],
                                        blood_sugar_level=cart[0]['BSL'],
                                        carbohydrates=0.0, insulin=0.0)
            # Retrieve the id.
            diaryentries_id = DiaryEntries.objects.filter(date=cart[0]['date'], time=cart[0]['time']).values('id')[0]['id']

            for item in cart:
                category = Category.objects.filter(id=item['categoryId']).values('name')[0]['name']
                description = Description.objects.filter(id=item['descriptionId']).values('name')[0]['name']
                portion = Portion.objects.filter(id=item['portionId']).values('name')[0]['name']
                # Retrieving item carb value, and weight.

                item_carbs = Menu.objects.filter(category=category,
                                                 description=description,
                                                 portion=portion).values('carbohydrates')[0]['carbohydrates']
                item_weight = Menu.objects.filter(category=category,
                                                  description=description,
                                                  portion=portion).values('portion_weight')[0]['portion_weight']
                # Calculate carb value for item.
                item_carbs = item_carbs * item_weight * Decimal(0.01) * item['Q']

                # Update database.
                Diary_Menu.objects.create(diary_id=diaryentries_id,
                                          date=item['date'], time=item['time'],
                                          category=category, description=description, portion=portion, quantity=item['Q'],
                                          carbohydrates=item_carbs)

            # Groupby to get the sum of carbohydrates.
            carbs = Diary_Menu.objects.filter(date=cart[0]['date'], time=cart[0]['time'],
                                              diary_id=diaryentries_id).aggregate(total_sum=Sum('carbohydrates'))
            # Retrieve sum.
            carbs = carbs['total_sum']

            # Get insulin value.
            insulin = insulin_calculation(carbs, cart[0]['BSL'])

            # Update insulin value.
            DiaryEntries.objects.filter(id=diaryentries_id).update(carbohydrates=carbs)
            DiaryEntries.objects.filter(id=diaryentries_id).update(insulin=insulin)
            return render(request, 'Diary/list_view.html', context={'cart': cart})

        elif len(json.loads(sub)) != 0:
            sub = json.loads(sub)
            # Generate the diary_id.
            DiaryEntries.objects.create(date=sub[0]['date'], time=sub[0]['time'],
                                        blood_sugar_level=sub[0]['BSL'],
                                        carbohydrates=0.0, insulin=0.0)
            # Retrieve the id.
            diaryentries_id = DiaryEntries.objects.filter(date=sub[0]['date'], time=sub[0]['time']).values('id')[0]['id']

            category = Category.objects.filter(id=sub[0]['categoryId']).values('name')[0]['name']
            description = Description.objects.filter(id=sub[0]['descriptionId']).values('name')[0]['name']
            portion = Portion.objects.filter(id=sub[0]['portionId']).values('name')[0]['name']

            # Retrieving item carb value, and weight.
            item_carbs = Menu.objects.filter(category=category,
                                             description=description,
                                             portion=portion).values('carbohydrates')[0]['carbohydrates']
            item_weight = Menu.objects.filter(category=category,
                                              description=description,
                                              portion=portion).values('portion_weight')[0]['portion_weight']

            # Calculate carb value for item.
            item_carbs = item_carbs * item_weight * Decimal(0.01) * sub[0]['Q']

            # Update database.
            Diary_Menu.objects.create(diary_id=diaryentries_id,
                                      date=sub[0]['date'], time=sub[0]['time'],
                                      category=category, description=description, portion=portion, quantity=sub[0]['Q'],
                                      carbohydrates=item_carbs)

            # Groupby to get the sum of carbohydrates.
            carbs = Diary_Menu.objects.filter(date=sub[0]['date'], time=sub[0]['time'],
                                              diary_id=diaryentries_id).aggregate(total_sum=Sum('carbohydrates'))
            # Retrieve sum.
            carbs = carbs['total_sum']

            # Get insulin value.
            insulin = insulin_calculation(carbs, sub[0]['BSL'])

            # Update insulin value.
            DiaryEntries.objects.filter(id=diaryentries_id).update(carbohydrates=carbs)
            DiaryEntries.objects.filter(id=diaryentries_id).update(insulin=insulin)
            return render(request, 'iteration3/list_view.html', context={'cart': cart})
    return render(request, 'iteration3/list_view.html', context={'cart': request.GET.get('cart')})

# def create_view(request):
#     diary_entry = DiaryEntries.objects.all()
#     my_form = DiaryForm(request.POST or None)
#     if my_form.is_valid():
#
#         # Get form data.
#         date = my_form.cleaned_data['date']
#         time = my_form.cleaned_data['time']
#         blood_sugar_level = my_form.cleaned_data['blood_sugar_level']
#         category = my_form.cleaned_data['category']
#         portion = my_form.cleaned_data['portion']
#         quantity = my_form.cleaned_data['quantity']
#
#         category_name = Category.objects.filter(id=category).all().values('name')[0]['name']
#         portion_name = Portion.objects.filter(id=category).all().values('name')[0]['name']
#
#         # # This will be a list at some point.
#         # ## Retrieve carb values for given entry. (.getlist?)
#         # carbs = Menu.objects.get(category=category_name,
#         #                          portion=portion_name,
#         #                          ).carbohydrates
#         #
#         # ## Retrieve weight values for given entry.
#         # weight = Menu.objects.get(category=category_name,
#         #                           portion=portion_name
#         #                           ).portion_weight
#         #
#         # # Carbohydrate formula.
#         # carbs = Decimal(0.01)*carbs*weight*quantity
#         # insulin = insulin_calculation(carbs, blood_sugar_level)
#
#         # # Updating.
#         # ## First, update the DiaryEntries model to generate a diary_id.
#         # DiaryEntries.objects.create(date=date, time=time,
#         #                             blood_sugar_level=blood_sugar_level,
#         #                             carbohydrates=0.0,
#         #                             insulin=0.0)
#
#         # Retrieve generated diary_id.
#         # id = DiaryEntries.objects.order_by('id').values_list('id', flat=True).last()
#
#         # Add daily food, if no entries are created it will automatically create one for the day.
#         if request.POST.has_key('add_list'):
#             for items in diary_entry:
#                 if date not in items.date:
#                     DiaryEntries.objects.create(date=date,blood_sugar_level=blood_sugar_level,
#                                     carbohydrates=0.0,
#                                     insulin=0.0)
#                     diaryentries_id = DiaryEntries.objects.filter(date = date).values('id')
#                     Diary_Menu.objects.create(date=date, time=time,
#                                               blood_sugar_level=blood_sugar_level,
#                                               category=category, portion=portion,
#                                               quantity=quantity,diary_id = diaryentries_id)
#                     return redirect('/iteration3/diary/')
#                 else:
#                     diaryentries_id = DiaryEntries.objects.filter(date = date).values('id')
#                     Diary_Menu.objects.create(date=date, time=time,
#                                               blood_sugar_level=blood_sugar_level,
#                                               category=category, portion=portion,
#                                               quantity=quantity,diary_id = diaryentries_id)
#                     return redirect('/iteration3/diary/')
#         elif request.POST.has_key('submit'):
#             pass
#
#         # ## Use generated diary_id to populate diary_menu.
#         # Diary_Menu.objects.create(category=category_name,
#         #                           portion=portion_name,
#         #                           quantity=quantity,
#         #                           carbohydrates=carbs,
#         #                           date = date,
#         #                           time=time,
#         #                           diary_id = id
#         #                           )
#
#         my_form = DiaryForm() # Show stored value.
#         context = {
#             'form': my_form
#         }
#
#         return render(request, 'iteration3/list_view.html', context)
#     else:
#         my_form = DiaryForm(request.POST or None)
#         context = {
#             'form': my_form
#         }
#     return render(request, 'iteration3/list_view.html', context={'diary_entry':diary_entry})

def entry_view(request, diary_id):
    obj = get_object_or_404(DiaryEntries, diary_id=diary_id)
    val = insulin_calculation(obj.food, obj.drinks, obj.blood_sugar_level)
    context = {
        'date': obj.date,
        'time': obj.time,
        'food': obj.food,
        'drink': obj.drinks,
        'blood_sugar_level': obj.blood_sugar_level,
        'Insulin': val
    }

    return render(request, "iteration3/entry_view.html", context)

def list_view(request):
    Entries = DiaryEntries.objects.values().all()
    Details = Diary_Menu.objects.values().values_list()
    ListViewDict = {}

    if Entries.exists():
        for item in Entries:
            id = int(item['id'])
            ListViewDict[id] = {'header': [], 'rows': []}
            ListViewDict[id]['header'] = ['Category', 'Description', 'Portion', 'Quantity', 'Carbohydrates']

            temp = Diary_Menu.objects.filter(diary_id=id).values_list()
            for i in range(len(temp)):
                ListViewDict[id]['rows'].append([temp[i][4], temp[i][5], temp[i][6], temp[i][7], temp[i][8]])
            ListViewDict[id]['insulin'] = DiaryEntries.objects.filter(id=id).values_list('insulin', flat=True)[0]
            ListViewDict[id]['BSL'] = DiaryEntries.objects.filter(id=id).values_list('blood_sugar_level', flat=True)[0]
    context = {
        'field': ListViewDict,
        'details': Details,
    }
    return render(request, 'iteration3/list_view.html', context)

def insulin_calculation(carbs, blood_sugar_level):
    ## Carbohydrate correction dose.
    # Initialising values.
    carbs = Decimal(carbs)
    target = Decimal(5.0)

    # Calculating the carbohydrate balancing dose.
    CHO = carbs/10

    # High Blood Sugar Correction Dose
    ## Initialising the target blood sugar.
    difference = blood_sugar_level - target
    HBSCD = difference/50

    # Final Insulin Dose.
    insulin_req = CHO + HBSCD
    return insulin_req

def carb_chart(request):
    entries = Diary_Menu.objects.all().order_by('-date')
    if entries.exists():
        start = request.GET.get('start')
        end = request.GET.get('end')
        if start:
            entries = entries.filter(date__gte=start)
        if end:
            entries = entries.filter(date__lte=end)

        fig = px.line(
            x=[c.date for c in entries],
            y=[c.carbohydrates for c in entries],
            title = 'Carbohydrates Chart',
            labels={'x': 'Date', 'y': 'Carbohydrates (g)'}
        )

        fig.update_layout(title = {
            'font_size': 22,
            'xanchor': 'center',
            'x': 0.5
        })
    else:
        fig = px.line(
            x=[0],
            y=[0],
            title='Carbohydrates Chart',
            labels={'x': 'Date', 'y': 'Carbohydrates (g)'}
        )


    carb_chart = fig.to_html()

    context = {'carb_chart': carb_chart,
               'form': DateForm}
    return render(request, 'iteration3/carb_chart.html', context)

def load_cart(request):
    cart = request.POST.get('cart_items')
    cart = json.loads(cart)
    return render(request, 'iteration3/diary.html', {'cart':cart})

def get_queryset():
    return DiaryEntries.objects.all().order_by('date')

def please_login(request):
    return render(request, "iteration3/please_login.html")

def page_no_found(request,**kwargs):
    return render(request, "iteration3/404.html")

def please_login(request):
    return render(request, "iteration3/404.html")

def index(request):
    pass
    return render(request, 'iteration3/index.html',{'iteration3':'iteration3'})

def guide(request):
    pass
    return render(request, 'iteration3/Beginners Guide.html')

def FAQ(request):
    pass
    return render(request, 'iteration3/faq.html')

def tips(request):
    pass
    return render(request, 'iteration3/tips.html')

def symptoms(request):
    pass
    return render(request, 'iteration3/symptoms.html')

def community(request):
    pass
    return render(request, 'iteration3/community.html')

def about(request):
    pass
    return render(request, 'iteration3/about.html')

def contact(request):
    pass
    return render(request, 'iteration3/contact.html')

def test(request):
    pass
    return render(request, 'iteration3/Beginners Guide.mht')

