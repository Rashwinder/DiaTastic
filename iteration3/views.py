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
from .forms import DateForm, EmailForm
from django.contrib.auth.models import User

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
            return render(request, 'iteration3/history.html', context={'cart': cart})
    return render(request, 'iteration3/history.html', context={'cart': request.GET.get('cart')})


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
def history(request):
    # if request.session:
    #     try:
    user_id = request.session['_auth_user_id']
    Entries = DiaryEntries.objects.filter(user_id=user_id).values().all().order_by('-date', '-time')
    Details = Diary_Menu.objects.values().values_list()

    if Entries.exists():
        LastWeek, LastMonth = {}, {}

        for item in Entries:
            id = int(item['id'])
            now = datetime.now().date()
            temp = Diary_Menu.objects.filter(diary_id=id).values_list().order_by('-date', '-time')

            # For each entry in filtered Diary_Menu:
            for i in range(len(temp)):

                # If the entry is less than a week old:
                if (now - temp[i][3]).days <= 7:
                    LastWeek[id] = {'rows': []}

                    # Get the calendar day.
                    LastWeek[id]['Day'] = calendar.day_name[temp[i][3].weekday()]

                    # Get the datetime.
                    LastWeek[id]['DateTime'] = datetime.combine(
                        DiaryEntries.objects.filter(id=id).values_list('date', flat=True)[0],
                        DiaryEntries.objects.filter(id=id).values_list('time', flat=True)[0]
                    )

                    # Get the blood sugar level, carbs and insulin values.
                    LastWeek[id]['BSL'] = round(
                        DiaryEntries.objects.filter(id=id).values_list('blood_sugar_level', flat=True)[0], 1)
                    LastWeek[id]['Carbs'] = floor(
                        DiaryEntries.objects.filter(id=id).values_list('carbohydrates', flat=True)[0])
                    LastWeek[id]['Insulin'] = floor(
                        DiaryEntries.objects.filter(id=id).values_list('insulin', flat=True)[0])

                    # Get the comment.
                    if DiaryEntries.objects.filter(id=id).values_list('comment', flat=True)[0]:
                        LastWeek[id]['Comment'] = DiaryEntries.objects.filter(id=id).values_list('comment', flat=True)[
                            0]

                    # Append the entries.
                    for each in temp:
                        LastWeek[id]['rows'].append([' x' + str(each[8]), each[5], each[6], str(each[7]),
                                                     str(each[9]) + ' carbohydrates'])
                # If the entry is more than a week old:
                else:
                    LastMonth[id] = {'rows': []}
                    LastMonth[id]['Day'] = calendar.day_name[temp[i][3].weekday()]
                    LastMonth[id]['rows'].append(['x' + str(temp[i][8]), temp[i][5], temp[i][6], str(temp[i][7]),
                                                  str(temp[i][9]) + ' carbohydrates'])
                    LastMonth[id]['DateTime'] = datetime.combine(
                        DiaryEntries.objects.filter(id=id).values_list('date', flat=True)[0],
                        DiaryEntries.objects.filter(id=id).values_list('time', flat=True)[0])
                    LastMonth[id]['Carbs'] = floor(
                        DiaryEntries.objects.filter(id=id).values_list('carbohydrates', flat=True)[0])
                    LastMonth[id]['Insulin'] = floor(
                        DiaryEntries.objects.filter(id=id).values_list('insulin', flat=True)[0])
                    LastMonth[id]['BSL'] = round(
                        DiaryEntries.objects.filter(id=id).values_list('blood_sugar_level', flat=True)[0], 1)
                    if DiaryEntries.objects.filter(id=id).values_list('comment', flat=True)[0]:
                        LastMonth[id]['Comment'] = DiaryEntries.objects.filter(id=id).values_list('comment', flat=True)[0]
        context = {
            'LastWeek': LastWeek,
            'LastMonth': LastMonth,
            'details': Details,
        }
        return render(request, 'iteration3/history.html', context)
    else:
        return render(request, 'iteration3/history.html')
        # except:
        #     return render(request, 'iteration3/please_login.html')

def insulin_calculation(carbs, blood_sugar_level):
    # Initialising values.
    carbs = Decimal(carbs)
    target = Decimal(5.0)

    # Calculating the carbohydrate balancing dose.
    CHO = carbs/10

    # High Blood Sugar Correction Dose
    difference = Decimal.from_float(blood_sugar_level) - target
    HBSCD = difference/50

    # Final Insulin Dose.
    insulin_req = CHO + HBSCD
    return insulin_req


def visualisation(entries=True):
    # Dataframe generation.
    date = [datetime.combine(c.date, c.time) for c in entries]
    bsl = [c.blood_sugar_level for c in entries]
    carbs = [c.carbohydrates for c in entries]
    isl = [c.insulin for c in entries]
    df = pd.DataFrame({'Date': date, 'Blood Sugar (mmol/L)': bsl, 'Insulin (units)': isl, 'Carbs (g)': carbs})

    # Melting for faceting purposes.
    df_melt = df.melt(id_vars='Date', value_vars=['Blood Sugar (mmol/L)', 'Insulin (units)', 'Carbs (g)'])
    df_melt = df_melt.rename(columns={'variable': 'Legend'})

    # Figure plotting.
    fig4 = px.line(
        df_melt,
        x='Date',
        y='value',
        facet_col='Legend',
        facet_col_wrap=3,
        color='Legend',
        title='Metrics Chart',
        labels={'x': 'Date', 'y': 'Blood Sugar (mmol/L)'}
    )

    bsl_list = df['Blood Sugar (mmol/L)'].min(), df['Blood Sugar (mmol/L)'].max(), df['Blood Sugar (mmol/L)'].mean()
    bsl_list = [round(v, 1) for v in bsl_list]
    carbs_list = df['Carbs (g)'].min(), df['Carbs (g)'].max(), df['Carbs (g)'].mean()
    carbs_list = [round(v, 2) for v in carbs_list]
    isl_list = df['Insulin (units)'].min(), df['Insulin (units)'].max(), df['Insulin (units)'].mean()
    isl_list = [round(v) for v in isl_list]

    # Figure plotting.
    fig1 = px.line(
        df,
        x='Date',
        y='Blood Sugar (mmol/L)',
        title='Blood Sugar Levels',
        labels={'x': 'Date', 'y': 'Blood Sugar (mmol/L)'}
    )
    # Figure plotting.
    fig2 = px.line(
        df,
        x='Date',
        y='Carbs (g)',
        title='Carbohydrates',
        labels={'x': 'Date', 'y': 'Carbs (g)'}
    )
    # Figure plotting.
    fig3 = px.line(
        df,
        x='Date',
        y='Insulin (units)',
        title='Insulin',
        labels={'x': 'Date', 'y': 'Insulin (units)'}
    )

    # Show axes for all figures.
    fig1.update_yaxes(showticklabels=True, matches=None)
    fig2.update_yaxes(showticklabels=True, matches=None)
    fig3.update_yaxes(showticklabels=True, matches=None)
    return fig1, fig2, fig3, bsl_list, carbs_list, isl_list, fig4


@login_required
def metrics(request):
    if request.session:
        entries = DiaryEntries.objects.filter(user_id=request.session['_auth_user_id']).all().order_by('date', 'time')

        # If there are entries, check for the start date and end date.
        if entries.exists():
            start = request.GET.get('start')
            end = request.GET.get('end')

            # If start and end date are provided, filter the entries.
            if start:
                entries = entries.filter(date__gte=start)
            if end:
                entries = entries.filter(date__lte=end)

            if entries.exists():
                # If there are entries at that point, create the graph.
                fig1, fig2, fig3, bsl_list, carbs_list, isl_list, fig4 = visualisation(entries)

            # If no entries, return 0.
            else:
                x, y = [0], [0]
                fig1 = px.line(
                    x=x,
                    y=y,
                    title='Blood Sugar Chart',
                    labels={'x': 'Date', 'y': 'Blood Sugar (mmol/L)'}
                )

                fig2 = px.line(
                    x=x,
                    y=y,
                    title='Blood Sugar Chart',
                    labels={'x': 'Date', 'y': 'Carbs (g)'}
                )

                fig3 = px.line(
                    x=x,
                    y=y,
                    title='Blood Sugar Chart',
                    labels={'x': 'Date', 'y': 'Insulin (units)'}
                )
                bsl_list = 0, 0, 0
                carbs_list = 0, 0, 0
                isl_list = 0, 0, 0

        # Updating the figure layout.
        fig1.update_layout(title={'xanchor': 'center', 'x': 0.5, 'y': 0.85, 'font_size': 16},
                           paper_bgcolor="rgba(0,0,0,0)"
                           )

        fig2.update_layout(title={'xanchor': 'center', 'x': 0.5, 'y': 0.85, 'font_size': 16},
                           paper_bgcolor="rgba(0,0,0,0)"
                           )

        fig3.update_layout(title={'xanchor': 'center', 'x': 0.5, 'y': 0.85, 'font_size': 16},
                           paper_bgcolor="rgba(0,0,0,0)"
                           )

        fig4.update_layout(title={'xanchor': 'center', 'x': 0.5, 'y': 0.85, 'font_size': 16},
                           paper_bgcolor="rgba(0,0,0,0)"
                           )

        # Show axes for all figures.
        fig1.update_yaxes(showticklabels=True, matches=None)
        fig2.update_yaxes(showticklabels=True, matches=None)
        fig3.update_yaxes(showticklabels=True, matches=None)
        fig4.update_yaxes(showticklabels=True, matches=None)

        # Rendering to html.
        bsl_chart = fig1.to_html()
        carbs_chart = fig2.to_html()
        isl_chart = fig3.to_html()

        # Try to create the directory.
        try:
            os.makedirs('../tp08_website/attachments/{}'.format(request.session['_auth_user_id']))
            # Save the figure as a html file.
            fig4.write_html("../tp08_website/attachments/{}/fig_metrics.html".format(request.session['_auth_user_id']))

        # If the directory exists, it'll receive an error. Then, it will just save the figure as a html file.
        except:
            # Save the figure as a html file.
            fig4.write_html("../tp08_website/attachments/{}/fig_metrics.html".format(request.session['_auth_user_id']))

        # Sending the figures to the html template.
        context = {'bsl_chart': bsl_chart,
                   'carbs_chart': carbs_chart,
                   'isl_chart': isl_chart,

                   'bsl_min': bsl_list[0],
                   'bsl_max': bsl_list[1],
                   'bsl_avg': bsl_list[2],
                   'carbs_min': carbs_list[0],
                   'carbs_max': carbs_list[1],
                   'carbs_avg': carbs_list[2],
                   'isl_min': isl_list[0],
                   'isl_max': isl_list[1],
                   'isl_avg': isl_list[2],
                   'form': DateForm}
        return render(request, 'iteration3/metrics.html', context)


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





