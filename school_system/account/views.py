
import pymysql
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .models import user_type
from django.conf import settings
from .forms import User_login_form
from django.shortcuts import get_object_or_404,redirect
from django.contrib import messages


db = pymysql.connect(host=settings.DB_HOST,  # your host, usually localhost
                     user=settings.DB_USERNAME,  # your username
                     passwd=settings.DB_PASSWORD,  # your password
                     db=settings.DB_NAME)  # name of the data base
db.set_charset('utf8mb4')
# you must create a Cursor object. It.DB_HOST  you execute all the queries you need
cur = db.cursor()

# Create your views here.


def index(request):
    return TemplateResponse(request, 'account/index.html')


def login_view(request):
    """
        Login for all types of users.
        Logs in user using the login in form and redirects to a certain page.
    """
    form = User_login_form(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            newUser = authenticate(username=username, password=password)
            login(request, newUser)
            type = get_object_or_404(user_type, user = newUser).type
            # TODO: Check on type and return a specific page accordingly

            return HttpResponse(type) # TODO: CHANGEEEEE!
        else:
            messages.error(request,"Something went wrong")
    return render(request ,"account/login_form.html" ,{"form": form})


def register_parent(request):
    """
        Send register form to user for GET. And register user in DB for POST
    """

    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = User()
        user.username = username
        user.set_password(password)
        user.save()
        type_of_user = user_type()
        type_of_user.user = user
        type_of_user.type = 'parent'
        type_of_user.save()
        new_user = authenticate(username=username, password=password)
        login(request, new_user)

        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        address = request.POST.get("address")
        email = request.POST.get("email")
        phone_number = request.POST.get("phone_number")

        cur.execute("INSERT INTO Parents(username, password_, first_name, last_name, email, p_address, telephone_number) VALUES(%s,%s,%s,%s,%s,%s,%s)", (username, password, first_name, last_name, email, address, phone_number))
        db.commit()

        return HttpResponse('Registered')

    return TemplateResponse(request, 'account/register_parent.html')


def register_teacher(request):
    """
        Send register form to teacher for GET. And register teacher in DB for POST
    """

    if request.method == 'POST':

        first_name = request.POST.get("first_name")
        middle_name = request.POST.get("middle_name")
        last_name = request.POST.get("last_name")
        birth_date = request.POST.get("birth_date")
        email = request.POST.get("email")
        gender = request.POST.get("gender")
        address = request.POST.get("address")
        school_name = request.POST.get("school_name")
        school_address = request.POST.get("school_address")
        home_phone = request.POST.get("home_phone")
        years = request.POST.get("years")

        # insert without username
        cur.execute("INSERT INTO Teachers(first_name, middle_name, last_name, birth_date, email, gender, e_address, school_name, school_address,home_phone, years_of_experience) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (first_name, middle_name, last_name, birth_date, email, gender, address, school_name, school_address, home_phone, years))
        db.commit()

        return HttpResponse('Registered as a Teacher')

    cur.execute("SELECT name, s_address FROM Schools")
    data = cur.fetchall()
    all_schools = []
    for rec in data:
        school = {}
        school['name'] = rec[0]
        school['address'] = rec[1]
        all_schools.append(school)

    return TemplateResponse(request, 'account/register_teacher.html', {"schools": all_schools})


def view_schools(request):
    """
        Views All schools categorized by their level.
    """

    cur.execute("SELECT * FROM School_offers_Level ORDER BY l_type")
    data = cur.fetchall()
    all_schools = []
    for school in data:
        sch = {}
        sch['level'] = school[0]
        sch['name'] = school[1]
        sch['address'] = school[2]
        all_schools.append(sch)

    return TemplateResponse(request, 'account/view_schools.html', {"schools": all_schools})


def view_school_info(request):
    """
        View all information about a certain school.
    """

    school_name = request.POST.get("school_name")
    school_address = request.POST.get("school_address")

    cur.execute("SELECT * FROM Schools WHERE name=%s AND s_address=%s", (school_name, school_address))
    school_info = cur.fetchone()
    school = {}
    school['name'] = school_info[0]
    school['address'] = school_info[1]
    school['phone_number'] = school_info[2]
    school['email'] = school_info[3]
    school['information'] = school_info[4]
    school['vision'] = school_info[5]
    school['mission'] = school_info[6]
    school['language'] = school_info[7]
    school['fees'] = school_info[8]
    school['type'] = school_info[9]

    cur.execute("SELECT parent_username, review FROM SchoolReviews WHERE school_name=%s AND school_address=%s", (school_name, school_address))
    reviews = cur.fetchall()
    all_reviews = []
    for review in reviews:
        rev = {}
        rev['parent'] = review[0]
        rev['review'] = review[1]
        all_reviews.append(rev)

    return TemplateResponse(request, 'account/view_school_info.html', {"school": school, "reviews": all_reviews})










