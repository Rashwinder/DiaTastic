import calendar
import json
import os
from datetime import datetime
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.core import mail
from django.conf import settings
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal

from numpy import double

from .models import Diary_Menu, Category, Portion, Menu, Description,DiaryEntries
from .forms import  DateForm, EmailForm
from django.contrib.auth.models import User
import plotly
import plotly.express as px
from math import floor
from django.core.exceptions import ValidationError
from django.core.validators import validate_email



def login(request):
    if request.session:
        try:
            id=request.session['_auth_user_id']
            request.session['is_login'] = True
            request.session['signup'] = True
            request.session['user_name'] = User.objects.get(id=id).first_name
            return redirect('/index/')
        except:
            request.session['signup'] = True
            # request.session['user_name'] = User.objects.get(id=id).first_name
            return render(request, 'iteration3/login.html', {'iteration3':'iteration3'})
    else:
        return render(request, 'iteration3/login.html', {'iteration3': 'iteration3'})
    return render(request, 'iteration3/login.html',{'iteration3':'iteration3'})

def logout(request):
    if not request.session.get('is_login', None):
        return redirect("/login/")
    request.session.flush()
    return redirect("/index/")


def load_portion(request):
    category_id = request.GET.get('category')
    description_id = request.GET.get('description')
    portion = Portion.objects.filter(category_id=category_id,
                                     description_id=description_id).order_by('name')
    return render(request, 'iteration3/portion_dropdown_list_options.html', {'portion': portion})

def load_description(request):
    category_id = request.GET.get('category')
    description = Description.objects.filter(category_id=category_id).order_by('name')
    return render(request, 'iteration3/description_dropdown_list_options.html', {'description': description})

@login_required
def diary(request):
    category = Category.objects.values('id', 'name')
    portion = Portion.objects.values('id', 'name')
    description = Description.objects.values('id', 'name')
    return render(request, 'iteration3/diary1.html',
                  context={'category': category,
                           'portion': portion,'description':description})


# Diary views.
def create_view(request):
    if request.method == "POST":
        id = request.session['_auth_user_id']
        cart = request.POST.get('cart_items')
        if len(json.loads(cart)) != 0:
            cart = json.loads(cart)

            # Generate the diary_id.
            DiaryEntries.objects.create(date=cart[0]['date'], time=cart[0]['time'],
                                        blood_sugar_level=cart[0]['BSL'],
                                        carbohydrates=0.0, insulin=0.0,user_id=id)
            # Retrieve the id.
            diaryentries_id = DiaryEntries.objects.filter(date=cart[0]['date'], time=cart[0]['time'],user_id=id).values('id')[0]['id']

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
                                          carbohydrates=item_carbs,user_id=id)

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
            DiaryEntries.objects.filter(id=diaryentries_id).update(comment=cart[0]['comment'])
            return render(request, 'Diary/list_view.html', context={'cart': cart})
    return render(request, 'iteration3/list_view.html', context={'cart': request.GET.get('cart')})


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

@login_required
def list_view(request):
    if request.session:
        try:
            user_id = request.session['_auth_user_id']
            Entries = DiaryEntries.objects.filter(user_id=user_id).values().all().order_by('-date', '-time')
            Details = Diary_Menu.objects.values().values_list()

            if Entries.exists():
                LastMonth, LastWeek = {}, {}

                for item in Entries:
                    id = int(item['id'])
                    now = datetime.now().date()
                    temp = Diary_Menu.objects.filter(diary_id=id).values_list()
                    for i in range(len(temp)):
                        if (now - temp[i][3]).days <= 7:
                            LastWeek[id] = {'rows': []}
                            LastWeek[id]['Day'] = calendar.day_name[temp[i][3].weekday()]
                            LastWeek[id]['rows'].append([' x' + str(temp[i][8]), temp[i][5], temp[i][6], str(temp[i][7]),
                                                             str(temp[i][9]) + ' carbohydrates'])
                            LastWeek[id]['DateTime'] = datetime.combine(
                                DiaryEntries.objects.filter(id=id).values_list('date', flat=True)[0],
                                DiaryEntries.objects.filter(id=id).values_list('time',flat=True)[0])
                            LastWeek[id]['Carbs'] = floor(DiaryEntries.objects.filter(id=id).values_list('carbohydrates', flat=True)[0])
                            LastWeek[id]['Insulin'] = floor(DiaryEntries.objects.filter(id=id).values_list('insulin', flat=True)[0])
                            LastWeek[id]['BSL'] = round(DiaryEntries.objects.filter(id=id).values_list('blood_sugar_level', flat=True)[0], 1)
                            if DiaryEntries.objects.filter(id=id).values_list('comment', flat=True)[0]:
                                LastWeek[id]['Comment'] = DiaryEntries.objects.filter(id=id).values_list('comment', flat=True)[0]


                        else:
                            LastMonth[id] = {'rows': []}
                            LastMonth[id]['Day'] = calendar.day_name[temp[i][3].weekday()]
                            LastMonth[id]['rows'].append([' x' + str(temp[i][8]), temp[i][5], temp[i][6], str(temp[i][7]),
                                                             str(temp[i][9]) + ' carbohydrates'])
                            LastMonth[id]['DateTime'] = datetime.combine(
                                DiaryEntries.objects.filter(id=id).values_list('date', flat=True)[0],
                                DiaryEntries.objects.filter(id=id).values_list('time',flat=True)[0])
                            LastMonth[id]['Carbs'] = floor(DiaryEntries.objects.filter(id=id).values_list('carbohydrates', flat=True)[0])
                            LastMonth[id]['Insulin'] = floor(DiaryEntries.objects.filter(id=id).values_list('insulin', flat=True)[0])
                            LastMonth[id]['BSL'] = round(DiaryEntries.objects.filter(id=id).values_list('blood_sugar_level', flat=True)[0], 1)
                            if DiaryEntries.objects.filter(id=id).values_list('comment', flat=True)[0]:
                                LastMonth[id]['Comment'] = DiaryEntries.objects.filter(id=id).values_list('comment', flat=True)[0]

                context = {
                    'LastWeek': LastWeek,
                    'LastMonth': LastMonth,
                    'details': Details,
                }
                return render(request, 'iteration3/list_view.html', context)
            else:
                return render(request, 'iteration3/list_view.html')
        except:
            return render(request, 'iteration3/please_login.html')

def insulin_calculation(carbs, blood_sugar_level):
    ## Carbohydrate correction dose.
    # Initialising values.
    carbs = Decimal(carbs)
    target = Decimal(5.0)

    # Calculating the carbohydrate balancing dose.
    CHO = carbs/10

    # High Blood Sugar Correction Dose
    ## Initialising the target blood sugar.
    difference = Decimal.from_float(blood_sugar_level) - target
    HBSCD = difference/50

    # Final Insulin Dose.
    insulin_req = CHO + HBSCD
    return insulin_req


@login_required
def carb_chart(request):
    if request.session:
        try:
            entries = DiaryEntries.objects.filter(user_id=request.session['_auth_user_id']).all().order_by('date', 'time')

            # If there are entries, check for the start date and end date.
            if entries.exists():
                start = request.GET.get('start')
                end = request.GET.get('end')

                # If start and end date are provided, filter the entries.
                if start and end:
                    entries = entries.filter(date__gte=start)
                    entries = entries.filter(date__lte=end)
                    # If there are entries at that point, create the graph.
                    if entries:
                        # Dataframe generation.
                        x = [datetime.combine(c.date, c.time) for c in entries]
                        bsl = [c.blood_sugar_level for c in entries]
                        carbs = [c.carbohydrates for c in entries]
                        isl = [c.insulin for c in entries]
                        df = pd.DataFrame({'x': x, 'Blood Sugar (mmol/L)': bsl, 'Insulin': isl, 'Carbs': carbs})

                        # Melting for faceting purposes.
                        df_melt = df.melt(id_vars='x', value_vars=['Blood Sugar (mmol/L)', 'Insulin', 'Carbs'])
                        df_melt = df_melt.rename(columns={'variable': 'Legend'})

                        # Figure plotting.
                        fig1 = px.line(
                            df_melt,
                            x=df_melt['x'],
                            y=df_melt['value'],
                            facet_col='Legend',
                            facet_col_wrap=3,
                            color='Legend',
                            title='Metrics Chart',
                            labels={'x': 'Date', 'y': 'Blood Sugar (mmol/L)'}
                        )
                    # If no entries, return 0.
                    else:
                        fig1 = px.line(
                            x=[0],
                            y=[0],
                            title='Blood Sugar Chart',
                            labels={'x': 'Date', 'y': 'Blood Sugar (mmol/L)'}
                        )

                # If no dates are provided, return all entries.
                else:
                    # Dataframe generation.
                    x = [datetime.combine(c.date, c.time) for c in entries]
                    bsl = [c.blood_sugar_level for c in entries]
                    carbs = [c.carbohydrates for c in entries]
                    isl = [c.insulin for c in entries]
                    df = pd.DataFrame({'x': x, 'Blood Sugar (mmol/L)': bsl, 'Insulin': isl, 'Carbs': carbs})

                    # Melting for faceting purposes.
                    df_melt = df.melt(id_vars='x', value_vars=['Blood Sugar (mmol/L)', 'Insulin', 'Carbs'])
                    df_melt = df_melt.rename(columns={'variable': 'Legend'})

                    # Figure plotting.
                    fig1 = px.line(
                        df_melt,
                        x=df_melt['x'],
                        y=df_melt['value'],
                        facet_col='Legend',
                        facet_col_wrap=3,
                        color='Legend',
                        title='Metrics Chart',
                        labels={'x': 'Date', 'y': 'Blood Sugar (mmol/L)'}
                    )

            # If no entries, return 0.
            else:

                # Dataframe generation.
                x = [0]
                bsl = [0]
                carbs = [0]
                isl = [0]
                df = pd.DataFrame({'x': x, 'Blood Sugar (mmol/L)': bsl, 'Insulin': isl, 'Carbs': carbs})

                # Melting for faceting purposes.
                df_melt = df.melt(id_vars='x', value_vars=['Blood Sugar (mmol/L)', 'Insulin', 'Carbs'])
                df_melt = df_melt.rename(columns={'variable': 'Legend'})

                # Figure plotting.
                fig1 = px.line(
                    df_melt,
                    x=df_melt['x'],
                    y=df_melt['value'],
                    facet_col='Legend',
                    facet_col_wrap=3,
                    color='Legend',
                    title='Metrics Chart',
                    labels={'x': 'Date', 'y': 'Blood Sugar (mmol/L)'}
                )

            # Updating the figure layout.
            fig1.update_layout(title={
                'font_size': 22,
                'xanchor': 'center',
                'x': 0.5},
                paper_bgcolor="rgba(0,0,0,0)",
                # plot_bgcolor="rgba(0,0,0,0)"
                )

            # Show axes for all figures.
            fig1.update_yaxes(showticklabels=True, matches=None)

            # Rendering to html.
            bsl_chart = fig1.to_html()

            # Try to create the directory.
            try:
                os.makedirs('../tp08_website/attachments/{}'.format(request.session['_auth_user_id']))
                # Save the figure as a html file.
                fig1.write_html("../tp08_website/attachments/{}/fig_metrics.html".format(request.session['_auth_user_id']))

            # If the directory exists, it'll receive an error. Then, it will just save the figure as a html file.
            except:
                # Save the figure as a html file.
                fig1.write_html("../tp08_website/attachments/{}/fig_metrics.html".format(request.session['_auth_user_id']))

            # Sending the figures to the html template.
            context = {'bsl_chart': bsl_chart,
                       'form': DateForm}
            return render(request, 'iteration3/carb_chart.html', context)
        except:
            return render(request, 'iteration3/please_login.html')


def email_form(request):
    form = EmailForm(request.POST or None)
    user_name = request.session['user_name']
    return render(request, 'iteration3/mail.html',context={'form':form,'user_name':user_name})

def success(request):
    subject = request.POST['subject']
    email_message = request.POST['message']
    email = request.POST['email']
    try:
        validate_email(email)
    except ValidationError:
        message = 'Bad email'
        return render(request, 'iteration3/mail.html',
                      {'message':message})
    else:
        message = 'Send successful！'
        connection = mail.get_connection()
        if connection:
            email = mail.EmailMessage(subject, email_message, settings.EMAIL_HOST_USER, [email])
            email.attach_file("../tp08_website/attachments/{}/fig_metrics.html".format(request.session['_auth_user_id']))
            email.send()
            return render(request, 'iteration3/mail.html',{'message':message})
        else:
            message = 'Could not connect to the mail server. Please try again later.'
            return render(request, 'iteration3/mail.html',{'message':message})


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

def index(request):
    if request.session:
        try:
            entries = DiaryEntries.objects.filter(user_id=request.session['_auth_user_id']).all().order_by('-date', '-time')
            x = [datetime.combine(c.date, c.time) for c in entries][0:10]
            x_lable = [c.strftime("%Y-%m-%d %H:%M:%S") for c in x][0:10]
            y_bsl = str([double(c.blood_sugar_level) for c in entries][0:10])
            y_carb = str([double(c.carbohydrates) for c in entries][0:10])
            y_isl = str([double(c.insulin) for c in entries][0:10])
            return render(request, 'iteration3/index.html', {'y_bsl': y_bsl,'y_carb': y_carb,'y_isl': y_isl,'x_lable':x_lable})
        except:
            request.session['signup'] = True
            return render  ( request,'iteration3/index.html', {'iteration3':'iteration3'})
    else:

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

def add_list(request):
    pass
    return render(request, 'iteration3/add.html')





