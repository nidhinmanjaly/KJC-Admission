from admission.models import Interview_panel, Applicant_Details
import csv
import os

def assign(students_list, interview_id):
    app_not_found = []
    app_found = []

    for appno in students_list:
        if not Applicant_Details.objects.filter(application_number=appno).exists():
            app_not_found.append([appno])
        elif Applicant_Details.objects.get(application_number=appno).interview_status_f1 or Applicant_Details.objects.get(application_number=appno).interview_status_f2:
            # if application exists with some interview status other than NULL: ignore
            continue
        else:
            app_found.append(appno)

    filename = 'student_not_found.csv'
    if not os.path.exists(filename):
        with open(filename, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['application_number'])
    else:
        with open(filename, 'a', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(app_not_found)
    
    # List of available interview panels
    panels = Interview_panel.objects.filter(interview_id=interview_id, panel_active=True)

    # Separate students based on scrutiny status
    SC_students = [s for s in app_found if (Applicant_Details.objects.get(application_number=s).application_remark).upper() == 'SC']
    SP_students = [s for s in app_found if (Applicant_Details.objects.get(application_number=s).application_remark).upper() == 'SP']

    SC_panels = [p for p in panels if (p.panel_type).upper() == 'SC']
    SP_panels = [p for p in panels if (p.panel_type).upper() == 'SP']

    # Sort the panels based on number of students already assigned to it
    SC_panels = sorted(SC_panels, key=lambda p: Applicant_Details.objects.filter(panel_assigned=p.panel_id, interview_status_f1=None).count())
    SP_panels = sorted(SP_panels, key=lambda p: Applicant_Details.objects.filter(panel_assigned=p.panel_id, interview_status_f1=None).exclude(application_remark = "SP-ABSENT").count())
    # SC_panels = sorted([p for p in panels if (p.panel_type).upper() == 'SC'], key=lambda p: Applicant_Details.objects.filter(panel_assigned=p.panel_id).count())
    # SP_panels = sorted([p for p in panels if (p.panel_type).upper() == 'SP'], key=lambda p: Applicant_Details.objects.filter(panel_assigned=p.panel_id).count())

    # Assign students to sc panels
    interval = 1
    for student_id in SC_students:
        student = Applicant_Details.objects.get(application_number=student_id)

        if interval == 0:
            interval = 1
            SC_panels = sorted(SC_panels, key=lambda p: Applicant_Details.objects.filter(panel_assigned=p.panel_id, interview_status_f1=None).count())
            # SC_panels = sorted(SC_panels, key=lambda p: Applicant_Details.objects.filter(panel_assigned=p.panel_id).count())
            # print(SC_panels)

        for panel in SC_panels:
            # print(panel.course_handled)
            if student.applied_program in (panel.course_handled):
                student.panel_assigned = panel
                student.token_no = panel.panel_size + 1
                panel.panel_size += 1
                panel.save()
                student.save()
                interval -= 1
                break

    # Assign students to sp panels
    interval = 1
    for student_id in SP_students:
        student = Applicant_Details.objects.get(application_number=student_id)

        if interval == 0:
            interval = 1
            SP_panels = sorted(SP_panels, key=lambda p: Applicant_Details.objects.filter(panel_assigned=p.panel_id, interview_status_f1=None).exclude(application_remark = "SP-ABSENT").count())
            # SP_panels = sorted(SP_panels, key=lambda p: Applicant_Details.objects.filter(panel_assigned=p.panel_id).count())
                
        for panel in SP_panels:
            student.panel_assigned = panel
            student.token_no = panel.panel_size + 1
            panel.panel_size += 1
            panel.save()
            student.save()
            interval -= 1
            break