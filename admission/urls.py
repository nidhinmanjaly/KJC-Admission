from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name="index"),
    path('admin_dashboard', views.admin_dashboard, name="admin_dashboard"),
    path('import_data/<interview_id>', views.import_data , name="import_data"),
    path('create_user', views.create_user, name="create_user"),
    path('login', views.loginPage, name="login"),
    path('panel', views.panel, name="panel"),
    path('delete_panel', views.delete_panel, name="delete_panel"),
    path('assign_panel', views.assign_panel, name="assign_panel"),
    path('sc_panel/<panel_id>', views.sc_panel, name="sc_panel"),
    path('sc_panel/<panel_id>/<appno>', views.view_sc_application, name="view_sc_application"),
    path('sp_panel/<panel_id>', views.sp_panel, name="sp_panel"),
    path('sp_panel/<panel_id>/<appno>', views.view_sp_application, name="view_sp_application"),
    path('delete_user',views.delete_user , name="delete_user"),
    path('reset_user_password',views.reset_user_password , name="reset_user_password"),
    path('logout',views.logoutUser,name='logout'),
    path('change_password',views.change_password, name='change_password'),
    path('score_sheet/<interview_id>',views.score_sheet, name='score_sheet'),
    path('edit_panel/<panel_id>',views.edit_panel, name='edit_panel'),
    path('get_remarks',views.get_remarks, name='get_remarks'),
    path('403_v2', views.error_403, name='error_403'),
    path('about', views.about, name='about'),
    path('panelToggle',views.panelToggle,name='panelToggle'),
    path('int_status_inactive',views.int_status_inactive,name='int_status_inactive'),
    path('int_status_active',views.int_status_active,name='int_status_active'),
    path('int_status_disable',views.int_status_disable,name='int_status_disable'),    
    path('get_student_not_found',views.get_student_not_found, name='get_student_not_found'),
    path('interviewer_dashboard', views.interviewer_dashboard, name='interviewer_dashboard'),
    path('studentview_index', views.studentview_index, name='studentview_index'),
    path('studentview/<interview_id>', views.studentview, name= 'studentview'),
    path('change_panel_status', views.change_panel_status, name="change_panel_status"),
    path('queue_interview',views.queue_interview, name='queue_interview'),
    path('queue_display',views.queue_display, name='queue_display'),
    path('backup', views.backup, name='backup'),
    path('generate_allotment_detail_format/<interview_id>', views.generate_allotment_detail_format, name="generate_allotment_detail_format"),
    path('get_live_panel_details/<interview_id>', views.get_live_panel_details, name="get_live_panel_details"),
    path('archived_data', views.archived_data, name="archived_data"),

#for Principal's UI.....

    path('principal_dashboard', views.principal_dashboard, name='principal_dashboard'),
    path('view_report', views.view_report, name="view_report"),
    path('courselist/<interview_id>', views.courselist, name='courselist'),
    path('finalstudentlist', views.finalstudentlist, name='finalstudentlist'),
    path('set_selection_status', views.set_selection_status, name='set_selection_status'),
    path('set_allotted_course', views.set_allotted_course, name='set_allotted_course'),
    path('get_updated_allot_details', views.get_updated_allot_details, name="get_updated_allot_details"),


]   