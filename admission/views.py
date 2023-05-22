import itertools
import re
from django.shortcuts import render,redirect, get_object_or_404
from django.http import FileResponse, HttpResponse, JsonResponse
import pandas as pd
from .models import *
from django.conf import settings
from .custom_scripts import db_loader, panel_assigner, print_stuff
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from datetime import datetime
from datetime import date
from django.urls import reverse
from django.db.models import Q, F
from django.contrib.auth.hashers import make_password
import os
import sqlite3
from django.core.management import call_command

DB_PATH = settings.DATABASES['default']['NAME']
BACKUP_DB_PATH = os.path.join(settings.BASE_DIR, 'backup.sqlite3')


@login_required(login_url='login')
def index(request):
    if request.user.user_type == 'staff' or request.user.user_type == 'faculty':
        return redirect('interviewer_dashboard')
    elif request.user.user_type == 'principal':
        return redirect('principal_dashboard')
    else:
        return redirect('admin_dashboard')

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'admin' or user.is_superuser, "error_403")
def admin_dashboard(request):
    if request.method == "POST":
        interview_id = request.POST['interview_id']
        interview_date = request.POST['date']

        interview_id = f"{str(datetime.strptime(interview_date, '%Y-%m-%d').date()).replace('-','')}_{interview_id.replace(' ', '_')}"
        
        Interview(id=interview_id, date=interview_date).save()

    interviews = []
    for interview in Interview.objects.all():
        interviews.append(
            {
                'interview_id' : interview.id,
                'date' : interview.date,
                'status': interview.status,
                'panel_count' : Interview_panel.objects.filter(interview_id=interview.id).count()
            }
        )

    return render(request, 'admin_dashboard.html', {'interviews' : interviews})

def int_status_inactive(request):
    if request.method == "POST":
        interview_id = request.POST["interview_id"]
        # print(interview_id)
        panel = Interview.objects.get(id=interview_id).status
        # print(panel)  
            
        Interview.objects.filter(id=interview_id).update(status="inactive")
        panel = Interview.objects.get(id=interview_id).status
        # print(panel)
        
        return redirect('index')


def int_status_active(request):
    if request.method == "POST":
        interview_id = request.POST["interview_id"]
        # print(interview_id)
        panel = Interview.objects.get(id=interview_id).status
        # print(panel)  
            
        Interview.objects.filter(id=interview_id).update(status="active")
        panel = Interview.objects.get(id=interview_id).status
        # print(panel)
        
        return redirect('index')

def int_status_disable(request):
    if request.method == "POST":
        interview_id = request.POST["interview_id"]
        # print(interview_id)
        panel = Interview.objects.get(id=interview_id).status
        # print(panel)  
            
        Interview.objects.filter(id=interview_id).update(status="disabled")
        panel = Interview.objects.get(id=interview_id).status
        # print(panel)
        
        return redirect('index')


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'admin', "error_403")
def import_data(request, interview_id):
    msg = None

    # folder to save uploaded files
    uploads_folder = os.path.join(settings.BASE_DIR, 'uploads')
    
    if not os.path.exists(uploads_folder):
        os.mkdir(uploads_folder)
    
    if request.method == "POST":
        if 'upload_btn1' in request.POST.keys():
            input_file = request.FILES["input_file1"]
            
            # save file to this path
            file_save_path = os.path.join(uploads_folder, str(input_file))

            if os.path.exists(file_save_path):
                os.remove(file_save_path)

            with open(file_save_path, 'wb+') as destination:
                for chunk in input_file.chunks():
                    destination.write(chunk)
            
            msg = "success"
            
            # load data to db
            db_loader.load_student_data(file_save_path, DB_PATH, "admission_applicant_details", interview_id)

            os.remove(file_save_path)
        
        if 'upload_btn2' in request.POST.keys():
            input_file = request.FILES["input_file2"]
            
            # save file to this path
            file_save_path = os.path.join(uploads_folder, str(input_file))

            if os.path.exists(file_save_path):
                os.remove(file_save_path)

            with open(file_save_path, 'wb+') as destination:
                for chunk in input_file.chunks():
                    destination.write(chunk)
            
            msg = "success2"
            
            # load data to db
            db_loader.load_allotment_details(file_save_path, DB_PATH, "admission_allotment_details")

            os.remove(file_save_path)
        
        if 'upload_btn3' in request.POST.keys():
            input_file = request.FILES["input_file3"]
            
            # save file to this path
            file_save_path = os.path.join(uploads_folder, str(input_file))

            if os.path.exists(file_save_path):
                os.remove(file_save_path)

            with open(file_save_path, 'wb+') as destination:
                for chunk in input_file.chunks():
                    destination.write(chunk)
            
            msg = "success3"
            
            # load data to db
            db_loader.load_selection_details(file_save_path, DB_PATH, "admission_applicant_details", interview_id)

            os.remove(file_save_path)
        
        if 'upload_btn4' in request.POST.keys():
            input_file = request.FILES["input_file4"]
            
            # save file to this path
            file_save_path = os.path.join(uploads_folder, str(input_file))

            if os.path.exists(file_save_path):
                os.remove(file_save_path)

            with open(file_save_path, 'wb+') as destination:
                for chunk in input_file.chunks():
                    destination.write(chunk)
            
            msg = "success4"
            
            # load data to db
            db_loader.load_reviewers_indicators(file_save_path, DB_PATH, "admission_reviewers_indicators")

            os.remove(file_save_path)

    return render(request, 'import_data.html', {'message':msg, 'interview_id': interview_id})


@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'admin', "error_403")
def create_user(request):
    msg = None

    if request.method =="POST":
        # if file uploaded
        if(request.FILES):
            # folder to save uploaded files
            uploads_folder = os.path.join(settings.BASE_DIR, 'uploads')

            input_file = request.FILES["input_file"]

            if not os.path.exists(uploads_folder):
                os.mkdir(uploads_folder)
            
            # save file to this path
            file_save_path = os.path.join(uploads_folder, str(input_file))

            if os.path.exists(file_save_path):
                os.remove(file_save_path)

            with open(file_save_path, 'wb+') as destination:
                for chunk in input_file.chunks():
                    destination.write(chunk)
            
            msg = "success"
            
            # load data to db
            db_loader.load_users(file_save_path, DB_PATH, "admission_user")

            os.remove(file_save_path)

        else:
            email = request.POST['email']
            username = request.POST['username']
            password = request.POST['password']
            if password:
                password = make_password(password)

            # deanery = request.POST['deanery']
            user_type = request.POST['user_type'].lower()

            # Connect to SQLite database
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            table_name = "admission_user"

            # get list of existing userIds
            existing_users = c.execute(f"SELECT email from {table_name}").fetchall()
            existing_users = [user[0] for user in existing_users]

            if email in existing_users:
                if not password:
                    c.execute(f"UPDATE {table_name} set username=?, user_type=? where email=?",(username, user_type, email))
                else: 
                    c.execute(f"DELETE FROM {table_name} where email=?",(email, ))
                    sql = f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, False, False)"
                    values = [email, username, password, user_type]

                    c.execute(sql, values)
            else:
                sql = f"INSERT INTO {table_name} VALUES (?, ?, ?, ?, False, False)"
                values = [email, username, password, user_type]
                
                c.execute(sql, values)
            
            

            # Commit changes and close connection
            conn.commit()
            conn.close()


    user_data = User.objects.all()
    return render(request, 'create_user.html', {'message':msg, 'user_data' : user_data})

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'admin', "error_403")
def delete_user(request):
    if request.method == "POST":
        email = request.POST['email_id']

        user = User.objects.get(email=email)
        user.delete()
        return redirect('create_user')

    return render(request, 'create_user.html')

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('/')
    else:
        if request.method =="POST":
            email = request.POST.get('email') 
            password = request.POST.get('password')

            users = authenticate(request, email=email, password=password)

            if users is not None:
                login(request, users)
                return redirect('/')
            else:
                messages.info(request,'Invalid Email/Password')
                return render(request,'login.html')
         
        return render(request, 'login.html')

def logoutUser(request):
    logout(request)
    return redirect('/')

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'admin', "error_403")
def panel(request):
    if request.method == "GET":
        interview_id = request.GET['interview_id']

    elif request.method == 'POST':
        panel_name = request.POST['panel_id']
        panel_type = request.POST['panel_type']
        courses_handled = request.POST.getlist('course_select') # multiple values
        interview_id = request.POST['interview_id']
        interviewers = request.POST.getlist('Interviewer_select') # multiple values

        interviewer_1 = interviewers[0]
        interviewer_2 = interviewers[1] if len(interviewers) == 2 else None
        interviewer_3 = interviewers[2] if len(interviewers) == 3 else None

        panel_id = f"{interview_id}_{panel_name.replace(' ', '_')}"

        # create new panel
        Interview_panel(panel_id, panel_type, courses_handled, Interview.objects.get(id=interview_id), interviewer_1, interviewer_2, interviewer_3).save()


    panel_dict = {}
    assigned_studs = []
    for panel in Interview_panel.objects.filter(interview_id=interview_id).order_by('panel_id'):
        panel_dict[panel] = {
            # 'panel_size' : Applicant_Details.objects.filter(panel_assigned=panel.panel_id).count(),

            # 'panel_pending_count': Applicant_Details.objects.filter(panel_assigned=panel.panel_id, interview_status_f1=None).count(),

            # 'panel_completed_count': Applicant_Details.objects.filter(panel_assigned=panel.panel_id, interview_status_f1="COMPLETE").count(),

            # 'panel_completed_count': (Applicant_Details.objects.filter(panel_assigned=panel.panel_id, interview_status_f1="COMPLETE", interview_status_f2="COMPLETE").count() if panel.interviewer1 and panel.interviewer2 else Applicant_Details.objects.filter(panel_assigned=panel.panel_id, interview_status_f1="COMPLETE").count()),

            # 'panel_absent_count': max(Applicant_Details.objects.filter(panel_assigned=panel.panel_id, interview_status_f1="ABSENT").count(), Applicant_Details.objects.filter(panel_assigned=panel.panel_id, application_remark="SP-ABSENT").count()),

            # sorted(SP_panels, key=lambda p: Applicant_Details.objects.filter(panel_assigned=p.panel_id)
            'applicants' : sorted(Applicant_Details.objects.filter(panel_assigned=panel.panel_id), key=lambda a: a.token_no)

        }
        assigned_studs += Applicant_Details.objects.filter(panel_assigned=panel.panel_id)
        
    courses = [course[0] for course in Applicant_Details.objects.filter(interview_id=interview_id).values_list('applied_program').distinct()]

    # get list of already assigned interviewers
    already_assigned_interviewers = set(itertools.chain(*(Interview_panel.objects.filter(interview_id=interview_id).values_list('interviewer1', 'interviewer2', 'interviewer3'))))
    # list of unassigned interviewers to be passed to panel creation page
    interviewers = [u for u in User.objects.all() if u.email not in already_assigned_interviewers]

    # print(assigned_studs)

    params = {
        'interview_id' : interview_id,
        'panel_dict' : panel_dict,
        'courses' : courses,
        'interviewers' : interviewers,
        'assigned_studs' : assigned_studs
    }
    return render(request, 'panels.html', params)

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'admin', "error_403")
def assign_panel(request):
    if request.method == 'POST':
        # attendee_list = [a.strip() for a in request.POST['attendee_list'].split(',')]
        attendee_list = [a for a in re.sub(r"[,\s]+", ",", request.POST['attendee_list'], flags=re.UNICODE).split(',')]
        
        # print(attendee_list)

        interview_id = request.POST['interview_id']

        panel_assigner.assign(attendee_list, interview_id)
    
    redirect_url = reverse('panel')
    return redirect(f'{redirect_url}?interview_id={interview_id}')

# ---> FACULTY USERS ONLY
@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'faculty', "error_403")
def sc_panel(request, panel_id):
    panel = Interview_panel.objects.get(panel_id=panel_id)
    f1, f2, f3 = [panel.interviewer1, panel.interviewer2, panel.interviewer3]
    
    if request.user == f1:
        # display on left panel 
        pending_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status_f1=None) | Q(panel_assigned=panel_id, interview_status_f1="IN PROGRESS")), key=lambda a: a.token_no) 

        # display on right panel
        completed_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status_f1="COMPLETE") | Q(panel_assigned=panel_id, interview_status_f1="ABSENT")), key=lambda a: a.token_no)

    elif request.user == f2:
        # display on left panel 
        pending_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status_f2=None) | Q(panel_assigned=panel_id, interview_status_f2="IN PROGRESS")), key=lambda a: a.token_no) 

        # display on right panel
        completed_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status_f2="COMPLETE") | Q(panel_assigned=panel_id, interview_status_f2="ABSENT")), key=lambda a: a.token_no)
    elif request.user == f3:
        # display on left panel 
        pending_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status_f3=None) | Q(panel_assigned=panel_id, interview_status_f3="IN PROGRESS")), key=lambda a: a.token_no) 

        # display on right panel
        completed_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status_f3="COMPLETE") | Q(panel_assigned=panel_id, interview_status_f3="ABSENT")), key=lambda a: a.token_no)

    # applicants = sorted(Applicant_Details.objects.filter(panel_assigned=panel_id), key=lambda a: a.token_no)

    params = {
        'pending_applicants' : pending_applicants,
        'completed_applicants' : completed_applicants,
        'panel_id' : panel_id
    }
    return render(request, 'sc_panel.html', params)

# ---> OFFICE AND STAFF USERS ONLY
@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'faculty', "error_403")
def view_sc_application(request, panel_id, appno):

    panel = Interview_panel.objects.get(panel_id=panel_id)
    f1, f2, f3 = [panel.interviewer1, panel.interviewer2, panel.interviewer3]
    
    if request.user == f1:
        Applicant_Details.objects.filter(application_number=appno).update(interview_status_f1 = "IN PROGRESS")
    elif request.user == f2:
        Applicant_Details.objects.filter(application_number=appno).update(interview_status_f2 = "IN PROGRESS")
    if request.user == f3:
        Applicant_Details.objects.filter(application_number=appno).update(interview_status_f3 = "IN PROGRESS")

    if request.method == "POST":
        if 'complete-btn' in request.POST.keys():
            reviewer_id = User.objects.get(email=request.POST['reviewer_id'])
            mode_of_education = request.POST['mode_education']
            second_language = request.POST['second_lang']
            cocurricular_activities = request.POST['activity']
            subject_knowledge = request.POST['sub_knowledge']
            attitude = request.POST['attitude']
            communication = request.POST['communication']
            remarks = request.POST['remarks']
            notes_for_admission_office = request.POST.get('notes_for_admission_office')
            interview_score = request.POST['interview_score']
            activity_score = request.POST['activity_score']
            
            if Remarks.objects.filter(application_no=appno, reviewer_id=request.user).exists():
                Remarks.objects.filter(application_no=appno, reviewer_id=request.user).update(mode_of_education=mode_of_education, 
                    second_language=second_language,cocurricular_activities=cocurricular_activities,
                    subject_knowledge=subject_knowledge,attitude=attitude,communication=communication,
                    remarks=remarks,notes_for_admission_office=notes_for_admission_office,
                    interview_score=interview_score,activity_score=activity_score)
            else:
                Remarks(application_no=Applicant_Details.objects.get(application_number=appno),reviewer_id=reviewer_id,mode_of_education=mode_of_education, 
                    second_language=second_language,cocurricular_activities=cocurricular_activities,
                    subject_knowledge=subject_knowledge,attitude=attitude,communication=communication,
                    remarks=remarks,notes_for_admission_office=notes_for_admission_office,
                    interview_score=interview_score,activity_score=activity_score).save()
            

            if request.user == f1:
                Applicant_Details.objects.filter(application_number=appno).update(interview_status_f1 = "COMPLETE")
            elif request.user == f2:
                Applicant_Details.objects.filter(application_number=appno).update(interview_status_f2 = "COMPLETE")
            if request.user == f3:
                Applicant_Details.objects.filter(application_number=appno).update(interview_status_f3 = "COMPLETE")

            # Applicant_Details.objects.filter(application_number=appno).update(interview_status = "COMPLETE")
            # return redirect('login')
            return redirect('sc_panel', panel_id=panel_id)
        
        elif 'absent-btn' in request.POST.keys():
            # application_number = request.POST['application_number']
            reviewer_id = User.objects.get(email=request.POST['reviewer_id'])

            if request.user == f1:
                Applicant_Details.objects.filter(application_number=appno).update(interview_status_f1 = "ABSENT")
            elif request.user == f2:
                Applicant_Details.objects.filter(application_number=appno).update(interview_status_f2 = "ABSENT")
            if request.user == f3:
                Applicant_Details.objects.filter(application_number=appno).update(interview_status_f3 = "ABSENT")

            # Applicant_Details.objects.filter(application_number=application_number).update(interview_status="ABSENT")

            Remarks(application_no=Applicant_Details.objects.get(application_number=appno), reviewer_id=reviewer_id, remarks="ABSENT").save()
            # return redirect('login')
            return redirect('sc_panel', panel_id=panel_id)
        
        elif 'back-to-queue-btn' in request.POST.keys():
            # application_number = request.POST['application_number']

            if request.user == f1:
                Applicant_Details.objects.filter(application_number=appno).update(interview_status_f1 = None)
            elif request.user == f2:
                Applicant_Details.objects.filter(application_number=appno).update(interview_status_f2 = None)
            if request.user == f3:
                Applicant_Details.objects.filter(application_number=appno).update(interview_status_f3 = None)

            # Applicant_Details.objects.filter(application_number=application_number).update(interview_status=None)
            # return redirect('login')
            return redirect('sc_panel', panel_id=panel_id)

    applicant_details = Applicant_Details.objects.get(application_number = appno)

    if applicant_details.course_category == "PG":
        year_gap = "NA"
    else:
        year_gap = date.today().year - int(float(applicant_details.tenth_year)) - 2

    # year_gap = today_date.year

    # panel_id = applicant_details.panel_assigned

    # panel = Interview_panel.objects.get(panel_id=panel_id)
    # f1, f2, f3 = [panel.interviewer1, panel.interviewer2, panel.interviewer3]
    
    if request.user == f1:
        # display on left panel 
        pending_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status_f1=None) | Q(panel_assigned=panel_id, interview_status_f1="IN PROGRESS")), key=lambda a: a.token_no) 
        # display on right panel
        completed_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status_f1="COMPLETE") | Q(panel_assigned=panel_id, interview_status_f1="ABSENT")), key=lambda a: a.token_no)

    elif request.user == f2:
        # display on left panel 
        pending_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status_f2=None) | Q(panel_assigned=panel_id, interview_status_f2="IN PROGRESS")), key=lambda a: a.token_no) 
        # display on right panel
        completed_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status_f2="COMPLETE") | Q(panel_assigned=panel_id, interview_status_f2="ABSENT")), key=lambda a: a.token_no)

    elif request.user == f3:
        # display on left panel 
        pending_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status_f3=None) | Q(panel_assigned=panel_id, interview_status_f3="IN PROGRESS")), key=lambda a: a.token_no) 
        # display on right panel
        completed_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status_f3="COMPLETE") | Q(panel_assigned=panel_id, interview_status_f3="ABSENT")), key=lambda a: a.token_no)

    # # display on left panel 
    # pending_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status=None) | Q(panel_assigned=panel_id, interview_status="IN PROGRESS")), key=lambda a: a.token_no) 

    # # display on right panel
    # completed_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status="COMPLETE") | Q(panel_assigned=panel_id, interview_status="ABSENT")), key=lambda a: a.token_no)

    # applicants = sorted(Applicant_Details.objects.filter(panel_assigned=panel_id), key=lambda a: a.token_no) 

    form_data = Remarks.objects.filter(application_no=appno, reviewer_id=request.user).first()

    # print(form_data)

    params = {
        'pending_applicants' : pending_applicants,
        'completed_applicants' : completed_applicants,
        'panel_id' : panel_id,
        "application_details" : applicant_details,
        "year_gap" : year_gap,
        "form_data" : form_data
    }

    return render(request,'sc_panel.html', params)

@login_required(login_url='login')
def change_password(request):
    new_password = None
    confirm_password = 'x'
    if request.method == 'POST':
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']
    if new_password != confirm_password:
        return render(request,'change_password.html')
    else:
        # user = User.objects.get(email=request.POST['email'])
        # user.password = new_password
        User.objects.filter(email=request.POST['email']).update(password=make_password(new_password))

        return redirect('login')

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'admin', "error_403")
def score_sheet(request, interview_id):
    remark_dict = {}
    
    interviewed_applications = Remarks.objects.all().values_list('application_no', flat=True).distinct()
    for appNo in interviewed_applications:
        app =  Applicant_Details.objects.get(application_number=appNo)

        # skip if interview id not same
        if app.interview_id.id != interview_id:
            continue

        remark_dict[app] = Remarks.objects.filter(application_no=appNo)[:2]
    
    # student_data = Applicant_Details.objects.all()
    return render(request,'score_sheet.html', {'remark_dict': remark_dict})


def error_403(request):
    return render(request, "403_v2.html")


def get_remarks(request):
    out_file = print_stuff.get_remarks(DB_PATH)
    file = open(out_file, 'rb')
    response = FileResponse(file)
    return response

def get_student_not_found(request):
    out_file = 'Std nt found.csv'
    csv = open(out_file, 'rb')
    response = FileResponse(csv)
    return response

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'admin', "error_403")
def edit_panel(request, panel_id):
    if request.method == 'POST':
        # print(panel_id)
        panel_id = request.POST['panel_id']
        panel_type = request.POST['panel_type']
        courses_handled = request.POST.getlist('course_select') # multiple values
        interview_id = request.POST['interview_id']
        interviewers = request.POST.getlist('Interviewer_select') # multiple values

        interviewer_1 = interviewers[0]
        interviewer_2 = interviewers[1] if len(interviewers) >= 2 else None
        interviewer_3 = interviewers[2] if len(interviewers) == 3 else None

        # Update panel
        Interview_panel.objects.filter(panel_id=panel_id).update(panel_type=panel_type, course_handled=courses_handled, interview_id=interview_id, interviewer1=interviewer_1, interviewer2=interviewer_2, interviewer3=interviewer_3)

        # Interview_panel(panel_id, panel_type, courses_handled, Interview.objects.get(id=interview_id), interviewer_1, interviewer_2, interviewer_3).save()
        
        redirect_url = reverse('panel')
        return redirect(f'{redirect_url}?interview_id={interview_id}')


    
    interview_id = Interview_panel.objects.get(panel_id=panel_id).interview_id
    
    edit_data = get_object_or_404(Interview_panel, panel_id=panel_id)  
    courses = [course[0] for course in Applicant_Details.objects.values_list('applied_program').distinct()] 
    # print(courses)
    # interviewers = [u[0] for u in Interview_panel.objects.values_list('interviewer1','interviewer2','interviewer3')]
    course_handled = edit_data.course_handled.strip('][').replace("'", "").split(', ')


    # list of unassigned interviewers to be passed to panel creation page
    # interviewers = [u[0] for u in User.objects.values_list('email') if u[0] not in already_assigned_interviewers]

    # interviewers = User.objects.all()

    interviewers_assigned = [i for i in [edit_data.interviewer1, edit_data.interviewer2, edit_data.interviewer3] if i]

    # get list of already assigned interviewers in all panels
    already_assigned_interviewers = list(itertools.chain(*(Interview_panel.objects.filter(interview_id=interview_id).values_list('interviewer1', 'interviewer2', 'interviewer3'))))

    
    interviewers = [u for u in User.objects.all() if u.email not in already_assigned_interviewers]

    interviewers += interviewers_assigned

    context = {
        'e_panel': edit_data,
        'courses' : courses,
        'interviewers' : interviewers,
        'interviewers_assigned' : interviewers_assigned,
        'course_handled' : course_handled
    }

    return render(request, 'edit_panel.html',context)
 
# ---> STAFF USERS ONLY
@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'staff', "error_403")
def sp_panel(request, panel_id):
    # display on left panel
    pending_applicants = sorted(Applicant_Details.objects.filter(panel_assigned=panel_id, application_remark = "SP"), key=lambda a: a.token_no)

    # display on right panel
    completed_applicants = sorted(Applicant_Details.objects.filter(panel_assigned=panel_id, application_remark = "SP-ABSENT"), key=lambda a: a.token_no)

    params = {
        'pending_applicants' : pending_applicants,
        'completed_applicants' : completed_applicants,
        'panel_id' : panel_id
    }

    return render(request,'sp_panel.html', params)

# ---> STAFF USERS ONLY
@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'staff', "error_403")
def view_sp_application(request, panel_id, appno):

    if request.method == 'POST':
        if 'submit-btn' in request.POST.keys():
            scrutiny_status = request.POST['scrutiny_status']
            appno = request.POST['appno']
            twelfth_percentage = request.POST['twelfth_percentage']

            # print(twelfth_percentage)

            # print(scrutiny_status, appno)
            Applicant_Details.objects.filter(application_number=appno).update(application_remark = scrutiny_status, aggregrate_percentage_including_language_for_UG=twelfth_percentage)
            # store current panel_id before reassigning
            curr_panel_id = panel_id

            panel_assigner.assign([appno], Interview_panel.objects.get(panel_id = panel_id).interview_id)

            # return redirect('index')
            return redirect('sp_panel', panel_id=curr_panel_id)
            

        
        elif 'absent-btn' in request.POST.keys():
            appno = request.POST['application_number']
            Applicant_Details.objects.filter(application_number=appno).update(application_remark = "SP-ABSENT")
            # store current panel_id
            curr_panel_id = panel_id
            
            return redirect('sp_panel', panel_id=curr_panel_id)
        
    
    applicant_details = Applicant_Details.objects.get(application_number = appno)
    if applicant_details.course_category == "PG":
        year_gap = "NA"
    else:
        year_gap = date.today().year - int(float(applicant_details.tenth_year)) - 2

    # panel_id = applicant_details.panel_assigned

    # display on left panel
    pending_applicants = sorted(Applicant_Details.objects.filter(panel_assigned=panel_id, application_remark = "SP"), key=lambda a: a.token_no) 
    # pending_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status=None) | Q(panel_assigned=panel_id, interview_status="IN PROGRESS")), key=lambda a: a.token_no) 

    # display on right panel
    completed_applicants = sorted(Applicant_Details.objects.filter(panel_assigned=panel_id, application_remark = "SP-ABSENT"), key=lambda a: a.token_no)
    # completed_applicants = sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel_id, interview_status="COMPLETED") | Q(panel_assigned=panel_id, interview_status="ABSENT")), key=lambda a: a.token_no)


    params = {
        "application_details" : applicant_details,
        "year_gap" : year_gap,
        'pending_applicants' : pending_applicants,
        'completed_applicants': completed_applicants,
        'panel_id' : panel_id
    }
    
    return render(request, 'sp_panel.html', params)

def panelToggle(request):
    # print("Requset fetched")

    if request.method == 'POST':
        panel_id = request.POST['panel_id']
        status = request.POST['status']
        # print(panel_id)
        # print(status)

        if(status == "true"):
            flag = True
        else:
            flag = False

        Interview_panel.objects.filter(panel_id=panel_id).update(panel_active=flag)

        response = HttpResponse("Updated")

        return response
    
def about(request):
    return render(request,'about.html')

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'staff' or user.user_type == 'faculty', "error_403")
def interviewer_dashboard(request):

    excluded_interviews = Interview.objects.filter(status__in = ['inactive', 'disabled'])

    # print(excluded_interviews)
    panels_assigned = Interview_panel.objects.filter(Q(interviewer1=request.user) | Q(interviewer2=request.user) | Q(interviewer3=request.user)).exclude(interview_id__in = excluded_interviews).distinct()

    params = {
        'panels_assigned' : panels_assigned,

    }
    return render(request, 'interviewer_dashboard.html', params)

def change_panel_status(request): # set panel_active = True or False
    if request.method == "POST":
        # panel_id = request.POST['panel_id']
        interview_id = request.POST['interview_id']
        status = request.POST['status']

        # if panel_id:
        #     Interview_panel.objects.filter(panel_id=panel_id).update(panel_active=status)
        # else:
        Interview_panel.objects.filter(interview_id=interview_id).update(panel_active=status)

        return HttpResponse("Updated")


def reset_user_password(request):
    email = request.POST['email_id']

    User.objects.filter(email=email).update(password=make_password(email))
    
    return redirect('create_user')

def delete_panel(request):
    if request.method == "POST":
        interview_id = request.POST['interview_id']
        panel_id = request.POST['panel_id']

        Interview_panel.objects.get(panel_id=panel_id).delete()
        
        redirect_url = reverse('panel')
        return redirect(f'{redirect_url}?interview_id={interview_id}')
    
def queue_interview(request):
    return render(request,'queue_interview.html')

def queue_display(request):
    return render(request,'queue_display.html')


# Father's dashboard and report pages
@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'principal', "error_403")
def principal_dashboard(request):
    interviews = Interview.objects.filter(status='inactive')

    return render(request, 'principal_dashboard.html', {'interviews' : interviews})

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'principal', "error_403")
def finalstudentlist(request):
    students = [
        {'name': 'John Doe', 'date': '10/04/2023', 'status': ''},
        {'name': 'Jane Smith', 'date': '11/04/2023', 'status': ''},
    ]
    if request.method == 'POST':
    # update the status of the selected student
        index = int(request.POST['index'])
        status = request.POST['status']
        students[index]['status'] = status
    return render(request, 'finalstudentlist.html', {'students': students})
    # return render(request, 'finalstudentlist.html')

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'principal', "error_403")
def courselist(request, interview_id):
    coursewise_dict = {}

    absent_applicants = Remarks.objects.filter(remarks = 'ABSENT').values_list("application_no", flat=True).distinct()
    interviewed_applications = Remarks.objects.all().values_list('application_no', flat=True).distinct()
    courses = Applicant_Details.objects.filter(interview_id=interview_id, application_number__in = interviewed_applications).values_list("applied_program", flat=True).distinct()

    interviewed_applications = Applicant_Details.objects.filter(interview_id=interview_id, application_number__in = interviewed_applications).exclude(application_number__in = absent_applicants)

    Applicant_Details.objects.filter(interview_id=interview_id, application_number__in = interviewed_applications, selection_status=None).exclude(application_number__in = absent_applicants).update(selection_status = 'PENDING')

    for course in courses:
        coursewise_dict[course] = {}

        for application in interviewed_applications.filter(applied_program = course):

            coursewise_dict[course][application] =  {
                'remarks': Remarks.objects.filter(application_no = application.application_number), 
                'reviewers_indicator': Reviewers_Indicators.objects.filter(application_number=application.application_number).first()
            }

        programs = Allotment_Details.objects.all().values_list('program', flat=True)

        params = {
            'coursewise_dict': coursewise_dict,
            'programs': programs,
            'interview_id': interview_id,
        }

    return render(request, 'courselist.html', params)


def studentview_index(request):
    interviews = Interview.objects.filter(status = 'active')
    return render(request, 'studentview_index.html', {'interviews' : interviews})


def studentview(request, interview_id):
    queue_list = []

    panels = Interview_panel.objects.filter(interview_id=interview_id).exclude(panel_active = "False")

    for panel in panels:
        queue_list.append(
            {
                # panel : Applicant_Details.objects.filter(panel_assigned=panel)[:10]
                panel: sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel, interview_status_f1=None) | Q(panel_assigned=panel, interview_status_f1="IN PROGRESS")).exclude(application_remark = "SP-ABSENT"), key=lambda a: a.token_no)[:10]
            }
        )
    
    # split list into lists of size 5
    q_list = [queue_list[i:i + 5] for i in range(0, len(queue_list), 5)]


    return render(request, 'studentview.html', {'q_list': q_list, 'interview_id': interview_id})

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'admin' or user.is_superuser, "error_403")
def backup(request):
    msg = ''
    
    # Define the file paths for the two databases
    default_db_path = DB_PATH
    backup_db_path = BACKUP_DB_PATH

    if request.method == "POST":

        # BACKUP DB
        if 'backup-db-btn' in request.POST.keys():
            # check if principal review not done
            conn = sqlite3.connect(default_db_path)
            pending_principal_selection = conn.cursor().execute(f"SELECT application_number, applied_program FROM admission_applicant_details WHERE application_number IN (SELECT DISTINCT application_no_id FROM admission_remarks WHERE remarks!='ABSENT') AND (selection_status='PENDING' OR selection_status IS NULL)  AND interview_id_id NOT IN (SELECT id from admission_interview WHERE status!='disabled');").fetchall()
            conn.close()
            if pending_principal_selection:
                # print(len(pending_principal_selection))
                params = {
                    'message': "backup-error",
                    'pending_applications': pending_principal_selection 
                }
                
                return render(request, 'backup.html', params)
            
            # Define a list of tables to exclude from the backup
            # excluded_tables = ['admission_user', 'django_migrations', 'sqlite_sequence', 'django_content_type','auth_group', 'auth_group_permissions', 'auth_permission', 'auth_user', 'auth_user_groups', 'auth_user_user_permissions', 'admission_user_user_permissions', 'admission_user_groups','django_session', 'django_admin_log',]
            
            backup_tables_list = ['admission_applicant_details', 'admission_remarks']

            # Check if the backup database file already exists
            backup_exists = os.path.exists(backup_db_path)
            
            # If the backup file doesn't exist, create a new file by creating empty tables for the included tables
            if not backup_exists:
                # Open a connection to the backup database file
                backup_conn = sqlite3.connect(backup_db_path)
                
                # Open a connection to the default database file
                with sqlite3.connect(default_db_path) as conn:
                    # Create a cursor object to execute SQL commands
                    cursor = conn.cursor()
                    
                    # Get a list of all the tables in the database
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = [row[0] for row in cursor.fetchall()]
                    
                    # Iterate over the included tables and create empty tables in the backup database
                    for table in backup_tables_list:
                        cursor.execute(f"SELECT sql FROM sqlite_master WHERE name='{table}';")
                        sql = cursor.fetchone()[0]
                        backup_conn.execute(sql)
                
                # Commit changes to the backup database and close the connection
                backup_conn.commit()
                backup_conn.close()
            
            # if backup db exists

            # Connect to the backup database file
            backup_conn = sqlite3.connect(backup_db_path)
            
            # Open a connection to the default database file
            with sqlite3.connect(default_db_path) as conn:
                # Create a cursor object to execute SQL commands
                cursor = conn.cursor()
                
                ## backup REMARKS table
                # Execute an SQL command to select data from the table
                cursor.execute(f"SELECT DISTINCT application_no_id FROM admission_remarks WHERE remarks!='ABSENT' AND (application_no_id IN (SELECT application_number FROM admission_applicant_details WHERE interview_id_id IN (SELECT id from admission_interview WHERE status='disabled')));")
                
                # Fetch all data from the cursor object
                incoming_applications = [row[0] for row in cursor.fetchall()]

                for appno in incoming_applications:
                    # check if application exists in backup db
                    if backup_conn.cursor().execute(f"SELECT * FROM admission_remarks WHERE application_no_id='{appno}';").fetchall():
                        continue
                    
                    # get data if it doesnt exist in backup
                    cursor.execute(f"SELECT * FROM admission_remarks WHERE application_no_id='{appno}';")
                    # get data ignore id field (autogenerated int id)
                    data = [d[1:] for d in cursor.fetchall()]
                    # get column names
                    cols = tuple(i[0] for i in cursor.description[1:])

                    # Check if there is any data to insert
                    if data:
                        # Build the placeholders string based on the number of fields in each row of data
                        placeholders = ",".join("?" * len(data[0]))
                        
                        # Execute an SQL command to insert the data into the backup database table
                        backup_conn.executemany(f"INSERT OR IGNORE INTO admission_remarks {cols} VALUES ({placeholders});", data)
                
                ## backup APPLICANT_DETAILS table exclude absent and no remarks applicants
                # Execute an SQL command to select data from the table
                cursor.execute(f"SELECT * FROM admission_applicant_details WHERE application_number IN (SELECT DISTINCT application_no_id FROM admission_remarks WHERE remarks!='ABSENT') AND interview_id_id NOT IN (SELECT id from admission_interview WHERE status!='disabled');")
                # Fetch all data from the cursor object
                data = cursor.fetchall()

                # Check if there is any data to insert
                if data:
                    # Build the placeholders string based on the number of fields in each row of data
                    placeholders = ",".join("?" * len(data[0]))
                    
                    # Execute an SQL command to insert the data into the backup database table
                    backup_conn.executemany(f"INSERT OR IGNORE INTO admission_applicant_details VALUES ({placeholders});", data)

                
                # Commit changes to the backup database and close the connection
                backup_conn.commit()
                backup_conn.close()

            msg = "backup-success"
        
        # FLUSH DB
        if 'flush-db-btn' in request.POST.keys():
            
            # Open a connection to the default database file
            conn = sqlite3.connect(default_db_path)
            
            # Enable foreign key checks
            conn.execute('PRAGMA foreign_keys = OFF;')

            flushed_apps = [app[0] for app in conn.cursor().execute(f"SELECT application_number from admission_Applicant_Details WHERE interview_id_id IN (SELECT id from admission_interview WHERE status='disabled');").fetchall()]

            # flush data from tables
            # !!!!!!!! DO NOT CHANGE ORDER !!!!!!!!!!!
            conn.execute(f"DELETE FROM admission_Applicant_Details WHERE interview_id_id IN (SELECT id from admission_interview WHERE status='disabled');")
            conn.execute(f"DELETE FROM admission_Interview_panel WHERE interview_id_id IN (SELECT id from admission_interview WHERE status='disabled');")
            conn.execute(f"DELETE FROM admission_Interview WHERE status='disabled';")
            for app in flushed_apps:
                conn.execute(f"DELETE FROM admission_Remarks WHERE application_no_id='{app}';")
            
            # Commit changes to the backup database and close the connection
            conn.commit()
            conn.close()

            msg = "flush-success"

    return render(request,'backup.html', {'message': msg})


def generate_allotment_detail_format(request, interview_id):
    programs = Applicant_Details.objects.filter(interview_id=interview_id).values_list("applied_program", flat=True).distinct()

    data = {
        'program': programs,
        'intake': None,
        'admitted': None,
        'allotted': None
    }

    df = pd.DataFrame(data)
    df.dropna(inplace = True, how="all")

    file = "allotment_detail_format.xlsx"

    df.to_excel(file, index=False)
    
    response = FileResponse(open(file, 'rb'))
    return response

def set_selection_status(request):
    if request.method == "POST":
        appno = request.POST['application_no']
        selection_status = request.POST['status']

        applicant = Applicant_Details.objects.get(application_number = appno)
        previous_course = applicant.course_allotted if applicant.course_allotted else applicant.applied_program
        
        if selection_status in ["NOT_SELECTED", "WAITING_LIST"]:
            if applicant.selection_status == "SELECTED":
                allotted = Allotment_Details.objects.get(program = previous_course).allotted
                Allotment_Details.objects.filter(program = previous_course).update(allotted = allotted - 1)

            Applicant_Details.objects.filter(application_number = appno).update(course_allotted = None)

        if selection_status == "SELECTED" and not applicant.course_allotted:
            allotted = Allotment_Details.objects.get(program = applicant.applied_program).allotted
            Allotment_Details.objects.filter(program = applicant.applied_program).update(allotted = allotted + 1)

            Applicant_Details.objects.filter(application_number = appno).update(course_allotted = applicant.applied_program)

        Applicant_Details.objects.filter(application_number = appno).update(selection_status=selection_status, reviewer=request.user)
        

        return HttpResponse("StatusUpdated")

def set_allotted_course(request):
    if request.method == "POST":
        appno = request.POST['application_no']
        alloted_course = request.POST['alloted_course']

        applicant = Applicant_Details.objects.get(application_number = appno)

        previous_course = applicant.course_allotted if applicant.course_allotted else applicant.applied_program

        ac_allotted = Allotment_Details.objects.get(program = alloted_course).allotted
        pc_allotted = Allotment_Details.objects.get(program = previous_course).allotted
        
        if applicant.selection_status == "SELECTED":
            if applicant.course_allotted == None or alloted_course != previous_course:
                Allotment_Details.objects.filter(program = previous_course).update(allotted = pc_allotted - 1)

        if not alloted_course == previous_course:
            Allotment_Details.objects.filter(program = alloted_course).update(allotted = ac_allotted + 1)


        Applicant_Details.objects.filter(application_number = appno).update(course_allotted=alloted_course, selection_status="SELECTED", reviewer=request.user)

        return HttpResponse("CourseUpdated")

@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'admin' or user.user_type == 'principal' or user.is_superuser, "error_403")
def get_updated_allot_details(request):
    interview_id = request.POST['interview_id']

    data = []

    # allot_details = list(Allotment_Details.objects.all().values())
    absent_applicants = Remarks.objects.filter(remarks = 'ABSENT').values_list("application_no", flat=True).distinct()
    interviewed_applications = Remarks.objects.filter().exclude(application_no__in = absent_applicants).values_list('application_no', flat=True).distinct()
    

    for detail in Allotment_Details.objects.all().values():

        detail.update({
            'not_selected': Applicant_Details.objects.filter(interview_id=interview_id, application_number__in = interviewed_applications, applied_program = detail['program'], selection_status = "NOT_SELECTED").count(),
            'waiting_list': Applicant_Details.objects.filter(interview_id=interview_id, application_number__in = interviewed_applications, applied_program = detail['program'], selection_status = "WAITING_LIST").count(),
            'pending': Applicant_Details.objects.filter(interview_id=interview_id, application_number__in = interviewed_applications, applied_program = detail['program'], selection_status = "PENDING").count(),
            'course_change':Applicant_Details.objects.filter(interview_id=interview_id, application_number__in = interviewed_applications, applied_program = detail['program'], selection_status = "SELECTED").exclude(applied_program = F('course_allotted')).count(),
            'selected': Applicant_Details.objects.filter(interview_id=interview_id, application_number__in = interviewed_applications, applied_program = detail['program'], selection_status = "SELECTED").count(),
        })
        
        data.append(
           detail
        )

    # print(data)
    return JsonResponse({'data': data}, safe=False)


def get_live_panel_details(request, interview_id):

    queue_list = []

    panels = Interview_panel.objects.filter(interview_id=interview_id).exclude(panel_active = "False")

    for panel in panels:
        queue_list.append(
            {
                panel.panel_id: [{ 'application_number': app.application_number, 'name': app.first_name + (f" {app.middle_name}" if app.middle_name else "") + (f" {app.last_name}" if app.last_name else "")} for app in sorted(Applicant_Details.objects.filter(Q(panel_assigned=panel, interview_status_f1=None) | Q(panel_assigned=panel, interview_status_f1="IN PROGRESS")).exclude(application_remark = "SP-ABSENT"), key=lambda a: a.token_no)[:10]]
            }
        )
    
    return JsonResponse({"data": queue_list}, safe=False)




@login_required(login_url='login')
@user_passes_test(lambda user: user.user_type == 'principal', "error_403")

# report for principal's view................

def view_report(request):

    # interview_id = request.POST['interview_id']
    data = []
    # allot_details = list(Allotment_Details.objects.all().values())
    absent_applicants = Remarks.objects.filter(remarks = 'ABSENT').values_list("application_no", flat=True).distinct()
    interviewed_applications = Remarks.objects.filter().exclude(application_no__in = absent_applicants).values_list('application_no', flat=True).distinct()
    

    for detail in Allotment_Details.objects.all().values():

        detail.update({
                'totalStudents': Applicant_Details.objects.filter(application_number__in = interviewed_applications, applied_program = detail['program']).count(),
                'not_selected': Applicant_Details.objects.filter(application_number__in = interviewed_applications, applied_program = detail['program'], selection_status = "NOT_SELECTED").count(),
                'waiting_list': Applicant_Details.objects.filter(application_number__in = interviewed_applications, applied_program = detail['program'], selection_status = "WAITING_LIST").count(),
                'vacant': detail['intake'] - detail['admitted'] - detail['allotted'],
            })
        
        data.append(
           detail
        )
    return render(request, 'view_report.html', {'courseDetails': data})

def archived_data(request):

    remarks_dict = {}
    try:
        backup_conn = sqlite3.connect(BACKUP_DB_PATH)
        backup_conn.row_factory = sqlite3.Row
        cursor = backup_conn.cursor()

        applications = cursor.execute(f"SELECT * FROM admission_applicant_details;").fetchall()

        for app in applications:
            remarks_dict[app] = cursor.execute(f"SELECT * FROM admission_remarks WHERE application_no_id='{app['application_number']}';").fetchall()
        
        # Close the connection to the backup database
        backup_conn.close()
    except:
        pass
    
    # student_data = Applicant_Details.objects.all()
    params = {
        'remark_dict': remarks_dict,
        'base_template': 'simple_base.html',
    }

    if request.user.user_type == 'admin':
        params['base_template'] = 'admin_base.html'
    if request.user.user_type == 'principal':
        params['base_template'] = 'principal_base.html'

    return render(request,'archived_data_report.html', params)
    