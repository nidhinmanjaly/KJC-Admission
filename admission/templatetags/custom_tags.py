import re
from django import template
from admission.models import Applicant_Details, Allotment_Details
from django.db.models import F, Q

register = template.Library()

@register.simple_tag(name='calculate_pending_count')
def calculate_pending_count(total, complete, absent):
    return total - (complete + absent)

@register.simple_tag(name='get_interview_status')
def get_interview_status(student, panel):
    if panel.panel_type == "SP":
        if student.application_remark == "SP-ABSENT":
            return "SP-ABSENT"
        else:
            return "PENDING"
    else:
        if panel.interviewer1:
            if panel.interviewer2:
                # if panel.interviewer3:
                #     if student.interview_status_f1 == student.interview_status_f2 == student.interview_status_f3 == None:
                #         return "PENDING"
                #     elif student.interview_status_f1 == student.interview_status_f2 == student.interview_status_f3 == "COMPLETE":
                #         return "COMPLETE"
                #     else:
                #         return "IN PROGRESS"
                # else:
                    if student.interview_status_f1 == student.interview_status_f2 == None:
                        return "PENDING"
                    elif student.interview_status_f1 == student.interview_status_f2 == "COMPLETE":
                        return "COMPLETE"
                    elif student.interview_status_f1 == student.interview_status_f2 == "ABSENT":
                        return "ABSENT"
                    else:
                        return "IN PROGRESS"
            else:
                if student.interview_status_f1 == None:
                    return "PENDING"
                elif student.interview_status_f1 == "COMPLETE":
                    return "COMPLETE"
                elif student.interview_status_f1 == "ABSENT":
                    return "ABSENT"
                else:
                    return "IN PROGRESS"

@register.simple_tag(name='panel_count')
def panel_count(panel):
    count = {}
    count['total'] = Applicant_Details.objects.filter(panel_assigned=panel.panel_id).count()
    if panel.panel_type == "SP":
        count['absent'] = Applicant_Details.objects.filter(panel_assigned=panel.panel_id, application_remark="SP-ABSENT").count()

        count['pending'] = count["total"] - count["absent"]

    else:
        if panel.interviewer1:
            if panel.interviewer2:
                count['complete'] = Applicant_Details.objects.filter(panel_assigned=panel.panel_id, interview_status_f1="COMPLETE", interview_status_f2="COMPLETE").count()
            else:
                count['complete'] = Applicant_Details.objects.filter(panel_assigned=panel.panel_id, interview_status_f1="COMPLETE").count()

        if panel.interviewer1:
            if panel.interviewer2:
                count['absent'] = Applicant_Details.objects.filter(panel_assigned=panel.panel_id, interview_status_f1="ABSENT", interview_status_f2="ABSENT").count()
            else:
                count['absent'] = Applicant_Details.objects.filter(panel_assigned=panel.panel_id, interview_status_f1="ABSENT").count()

        count['pending'] = count["total"] - count["absent"] - count['complete']


    return count

# @register.simple_tag(name='course_seats')
# def course_seats(course, total_applicants, interview_id):
#     if not course:
#         return
    
#     seats = {}
    
#     course_detail = Allotment_Details.objects.get(program=course)

#     seats['selected'] = course_detail.allotted
#     seats['not_selected'] = Applicant_Details.objects.filter(interview_id=interview_id, applied_program = course, selection_status = "NOT_SELECTED").count()
#     seats['waiting_list'] = Applicant_Details.objects.filter(interview_id=interview_id, applied_program = course, selection_status = "WAITING_LIST").count()

#     # seats['available'] = course_detail.intake - course_detail.allotted - course_detail.admitted

#     seats['pending'] = Applicant_Details.objects.filter(interview_id=interview_id, applied_program = course, selection_status = "PENDING").count()

#     return seats

# @register.simple_tag(name='get_seats')
# def get_seats(course):

#     p = Allotment_Details.objects.get(program=course)

#     return p.intake - p.admitted - p.allotted

@register.simple_tag(name='human_readable_text')
def human_readable_text(text):
    return re.sub('[][)&(.]',"", str(text)).replace(" ", "_")