# ================================================= Libraries =========================================================

import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from iteration3.models import Category, Portion, Description


# ================================================= Diary Views =======================================================


# Sending the data for the three dropdowns.
@login_required
def diary(request):
    category = Category.objects.values('id', 'name')
    portion = Portion.objects.values('id', 'name')
    description = Description.objects.values('id', 'name')
    return render(request, 'iteration3/diary1.html',
                  context={'category': category,
                           'portion': portion, 'description': description})


# Loading the new description dropdown menu in response to the ajax request.
def load_description(request):
    category_id = request.GET.get('category')
    description = Description.objects.filter(category_id=category_id).order_by('name')
    return render(request, 'iteration3/description_dropdown_list_options.html', {'description': description})


# Loading the new portion dropdown menu in response to the ajax request.
def load_portion(request):
    category_id = request.GET.get('category')
    description_id = request.GET.get('description')
    portion = Portion.objects.filter(category_id=category_id,
                                     description_id=description_id).order_by('name')
    return render(request, 'iteration3/portion_dropdown_list_options.html', {'portion': portion})


# Loading the cart sent by the user.
def load_cart(request):
    cart = request.POST.get('cart_items')
    cart = json.loads(cart)
    return render(request, 'iteration3/diary.html', {'cart': cart})


# Insulin formula.
def insulin_calculation(carbs, blood_sugar_level):
    # Initialising values.
    carbs = Decimal(carbs)
    target = Decimal(5.0)

    # Calculating the carbohydrate balancing dose.
    CHO = carbs / 10

    # High Blood Sugar Correction Dose
    difference = Decimal.from_float(blood_sugar_level) - target
    HBSCD = difference / 50

    # Final Insulin Dose.
    insulin_req = CHO + HBSCD
    return insulin_req


# ================================================= Diary Views =======================================================
