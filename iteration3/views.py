# ================================================= Libraries =========================================================


import calendar
import json
import os

from datetime import datetime
from decimal import Decimal

from django.conf import settings
from django.core import mail
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db.models import Sum
from django.shortcuts import render, redirect

from math import floor
from numpy import double

from .models import Diary_Menu, Category, Portion, Menu, Description, DiaryEntries
from .forms import DateForm, EmailForm

# Diary
from iteration3.utility.diary_utils import diary, load_description, load_portion, load_cart, insulin_calculation

# Metrics
from iteration3.utility.metrics_utils import entries_function, no_entries_function

# Calendar
# from iteration3.utility.calendar_utils import build_service, create_event

# ================================================= Libraries =========================================================


# ================================================= Login/out Views ===================================================

def login(request):
    return render(request, 'iteration3/login.html')

def logout(request):
    auth_logout(request)
    return redirect("/index/")

def index(request):
    # If the user is authenticated:
    if request.user.is_authenticated:
        request.session['_auth_user_id'] = User.objects.filter(username=request.user).values_list('id',
                                                                                                  flat=True).first()
        request.session['user_name'] = User.objects.filter(username=request.user).values_list('first_name',
                                                                                              flat=True).first()

        # Try to create a folder for them.
        try:
            os.makedirs('../tp08_website/attachments/{}'.format(request.session['_auth_user_id']))
        except:
            pass

        # Try to print the last 10 entries.
        try:
            entries = DiaryEntries.objects.filter(user_id=request.session['_auth_user_id']).all().order_by('-date',
                                                                                                           '-time')

            x = [datetime.combine(c.date, c.time) for c in entries][0:10]
            x_lable = [c.strftime("%Y-%m-%d %H:%M:%S") for c in x][0:10]
            y_bsl = str([double(c.blood_sugar_level) for c in entries][0:10])
            y_carb = str([double(c.carbohydrates) for c in entries][0:10])
            y_isl = str([double(c.insulin) for c in entries][0:10])
            return render(request, 'iteration3/index.html', {'y_bsl': y_bsl, 'y_carb': y_carb, 'y_isl': y_isl,
                                                             'x_lable': x_lable})
        except:
            return render(request, 'iteration3/index.html', {'iteration3': 'iteration3'})
    else:
        return render(request, 'iteration3/index.html', {'iteration3': 'iteration3'})


# ================================================= Login/out Views ==================================================


# ================================================= Diary View ======================================================


# Generating the entry.
def create_view(request):
    if request.method == "POST":
        id = request.session['_auth_user_id']
        cart = request.POST.get('cart_items')
        if len(json.loads(cart)) != 0:
            cart = json.loads(cart)

            # Generate the diary_id.
            DiaryEntries.objects.create(date=cart[0]['date'], time=cart[0]['time'],
                                        blood_sugar_level=cart[0]['BSL'],
                                        carbohydrates=0.0, insulin=0.0, user_id=id)
            # Retrieve the id.
            diaryentries_id = DiaryEntries.objects.filter(date=cart[0]['date'],
                                                          time=cart[0]['time'],
                                                          user_id=id).values('id')[0]['id']

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
                                          category=category, description=description, portion=portion,
                                          quantity=item['Q'],
                                          carbohydrates=item_carbs, user_id=id)

            # Group-by to get the sum of carbohydrates.
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


# ================================================= Diary Views =====================================================


# ================================================= History View ====================================================


@login_required
def history(request):
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
                        LastWeek[id]['Comment'] = DiaryEntries.objects.filter(id=id).values_list('comment',
                                                                                                 flat=True)[0]

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
                        DiaryEntries.objects.filter(id=id).values_list('date',
                                                                       flat=True)[0],
                        DiaryEntries.objects.filter(id=id).values_list('time',
                                                                       flat=True)[0])
                    LastMonth[id]['Carbs'] = floor(
                        DiaryEntries.objects.filter(id=id).values_list('carbohydrates',
                                                                       flat=True)[0])
                    LastMonth[id]['Insulin'] = floor(
                        DiaryEntries.objects.filter(id=id).values_list('insulin',
                                                                       flat=True)[0])
                    LastMonth[id]['BSL'] = round(
                        DiaryEntries.objects.filter(id=id).values_list('blood_sugar_level',
                                                                       flat=True)[0], 1)
                    if DiaryEntries.objects.filter(id=id).values_list('comment',
                                                                      flat=True)[0]:
                        LastMonth[id]['Comment'] = DiaryEntries.objects.filter(id=id).values_list('comment',
                                                                                                  flat=True)[0]

        context = {
            'LastWeek': LastWeek,
            'LastMonth': LastMonth,
            'details': Details,
        }
        return render(request, 'iteration3/history.html', context)
    else:
        return render(request, 'iteration3/history.html')


# ================================================= History View ====================================================


# ================================================= Metrics Views ===================================================


@login_required
def metrics(request):
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

    # If there are entries at this point, generate the charts.
    if entries.exists():
        fig1, fig2, fig3, bsl_list, carbs_list, isl_list, fig4 = entries_function(request)

    # If no entries, return empty charts.
    else:
        fig1, fig2, fig3, bsl_list, carbs_list, isl_list, fig4 = no_entries_function(request)

    # Rendering to html.
    bsl_chart = fig1.to_html()
    carbs_chart = fig2.to_html()
    isl_chart = fig3.to_html()
    fig4.write_html("../tp08_website/attachments/{}/fig_metrics.html".format(request.session['_auth_user_id']))

    # Sending the figures to the html template.
    context = {'bsl_chart': bsl_chart,
               'carbs_chart': carbs_chart,
               'isl_chart': isl_chart,

               # Statistics.
               'bsl_min': bsl_list[0],
               'bsl_max': bsl_list[1],
               'bsl_avg': bsl_list[2],
               'carbs_min': carbs_list[0],
               'carbs_max': carbs_list[1],
               'carbs_avg': carbs_list[2],
               'isl_min': isl_list[0],
               'isl_max': isl_list[1],
               'isl_avg': isl_list[2],

               # Date filtering form.
               'form': DateForm}
    return render(request, 'iteration3/metrics.html', context)


# ================================================= Metrics Views ===================================================


# ================================================= Email Views =====================================================


# Form for the user to enter their details.
def email_form(request):
    if os.path.isfile(("../tp08_website/attachments/{}/fig_metrics.html".format(request.session['_auth_user_id']))):
        print('It exists')
    else:
        print("Nope, doesn't exist")
    form = EmailForm(request.POST or None)
    user_name = request.session['user_name']
    return render(request, 'iteration3/mail.html', context={'form': form, 'user_name': user_name})


# Form to generate the email.
def success(request):
    subject = request.POST['subject']
    email_message = request.POST['message']
    email = request.POST['email']
    try:
        validate_email(email)
    except ValidationError:
        message = 'Bad email'
        return render(request, 'iteration3/mail.html',
                      {'message': message})
    else:
        message = 'Send successful！'
        connection = mail.get_connection()
        if connection:
            email = mail.EmailMessage(subject, email_message, settings.EMAIL_HOST_USER, [email])
            if ("../tp08_website/attachments/{}/fig_metrics.html".format(request.session['_auth_user_id'])).exists():
                email.attach_file(
                    "../tp08_website/attachments/{}/fig_metrics.html".format(request.session['_auth_user_id']))
                email.send()
            else:
                email.send()
            return render(request, 'iteration3/mail.html', {'message': message})
        else:
            message = 'Could not connect to the mail server. Please try again later.'
            return render(request, 'iteration3/mail.html', {'message': message})


# ================================================= Email Views =====================================================


# # ================================================= Calendar Views ==================================================


SCOPES = ['https://www.googleapis.com/auth/calendar']


# Retrieving the events.
# def get_events():
#     service = build_service()
#     event_results = service.events().list(calendarId='primary',
#                                           timeMin=datetime.utcnow().isoformat() + 'Z',
#                                           maxResults=10, singleEvents=True,
#                                           orderBy='startTime').execute()
#     ev_list = event_results.get('items', [])
#     return ev_list


# # ================================================= Calendar Views ==================================================


# ================================================= Misc Views ======================================================

# def login(request):
#     print(request.user.is_authenticated)
#     if request.session:
#         try:
#             id = request.session['_auth_user_id']
#             request.session['is_login'] = True
#             request.session['user_name'] = User.objects.get(id=id).first_name
#
#             # When the user is logging in, create a directory for them if the user does not have one.
#             try:
#                 os.makedirs('../tp08_website/attachments/{}'.format(request.session['_auth_user_id']))
#             except:
#                 pass
#         except:
#             return render(request, 'iteration3/login.html', {'iteration3': 'iteration3'})
#     else:
#         return render(request, 'iteration3/index.html', {'iteration3': 'iteration3'})
#     return render(request, 'iteration3/index.html', {'iteration3': 'iteration3'})


def get_queryset():
    return DiaryEntries.objects.all().order_by('date')


def please_login(request):
    return render(request, "iteration3/please_login.html")


def page_no_found(request, **kwargs):
    return render(request, "iteration3/404.html")


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


# ================================================= Misc Views ======================================================
