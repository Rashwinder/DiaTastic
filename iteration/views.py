from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal
from . import models
from .models import Food, Drink
import pandas as pd
import ast
from .forms import DiaryForm,UserForm
from .models import  DiaryEntries


def login(request):
    # if request.session.get('is_login',None):
    #     return redirect('/index/') #sing in page

    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "please check！"
        # if login_form.is_valid():
            # username = login_form.cleaned_data['username']
            # password = login_form.cleaned_data['password']
        username = request.POST.get('user')
        password = request.POST.get('password')
        try:
            user = models.User.objects.get(name=username)
            if user.password == password:
                request.session['is_login'] = True
                request.session['user_id'] = user.id
                request.session['user_name'] = user.name
                return redirect('/index/')
            else:
                message = "password error！"
        except:
            message = "user error！"
    return render(request, 'iteration/login.html',{'iteration':'iteration'})

def index(request):
    pass
    return render(request, 'iteration/index.html',{'iteration':'iteration'})

def guide(request):
    pass
    return render(request, 'iteration/Beginners Guide.mht')

def symptoms(request):
    pass
    return render(request, 'iteration/symptoms.html')

def community(request):
    pass
    return render(request, 'iteration/community.html')

def about(request):
    pass
    return render(request, 'iteration/about.html')

def contact(request):
    pass
    return render(request, 'iteration/contact.html')

def diary(request):
    drinks = Drink.objects.all()
    food = Food.objects.all()
    return render(request, 'iteration/diary.html',context={'drinks':drinks,'food':food})

def add_diary(request):
    pass
    return render(request, 'iteration/diary.html')

def test(request):
    pass
    return render(request, 'iteration/diary.html')

def create_view(request):
    if request.method == "POST":
        date = request.POST.get('date')
        time = request.POST.get('time')
        blood_sugar_level = request.POST.get('blood_sugar_level')
        food = request.POST.getlist('food')
        drinks = request.POST.getlist('drink')
        DiaryEntries.objects.create(date=date,time=time,blood_sugar_level=blood_sugar_level,food=food,drinks=drinks,insulin=0.0)
        diary_entry = DiaryEntries.objects.all()
        for item in diary_entry:
            if item.insulin == 0:
                DiaryEntries.objects.filter(diary_id=item.diary_id).update(
                    insulin=insulin_calculation(item.food, item.drinks, item.blood_sugar_level))
        return redirect("/list_view/",context={'date':date,'time':time,'blood_sugar_level':blood_sugar_level,'food':food,'drinks':drinks})

    return render(request, "iteration/history.html")

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

    return render(request, "iteration/entry_view.html", context)

def list_view(request):
    diary_entry = DiaryEntries.objects.all()
    for item in diary_entry:
        if item.insulin == 0:
            DiaryEntries.objects.filter(diary_id =item.diary_id).update(insulin = insulin_calculation(item.food, item.drinks, item.blood_sugar_level))
    return render(request,'iteration/history.html',context={'diary_entry':diary_entry})


def insulin_calculation(food, drinks, blood_sugar_level):
    ## Carbohydrate correction dose.
    # Initialising values.
    carbs = Decimal(0.0)
    target = Decimal(5.0)

    # Retrieving the drink data.
    drinks_data = Drink.objects.all().values()
    drinks_df = pd.DataFrame.from_records(drinks_data)
    drinks_df = drinks_df[drinks_df['name'].isin(ast.literal_eval(drinks))]
    # Retrieving the food data.
    food_data = Food.objects.all().values()
    food_df = pd.DataFrame.from_records(food_data)
    food_df = food_df[food_df['name'].isin(ast.literal_eval(food))]

    # Calculating the carbohydrates.
    carbs += Decimal(sum(food_df['carbohydrates'].values)) + Decimal(sum(drinks_df['carbohydrates'].values))

    # Calculating the carbohydrate balancing dose.
    CHO = carbs/10

    ## High Blood Sugar Correction Dose
    # Initialising the target blood sugar.
    difference = blood_sugar_level - target
    HBSCD = difference/50

    # Final Insulin Dose.
    insulin_req = CHO + HBSCD
    return insulin_req

def get_queryset():
    return DiaryEntries.objects.all().order_by('date')

def please_login(request):
    return render(request, "iteration/please_login.html")

def page_no_found(request,**kwargs):
    return render(request, "iteration/404.html")



