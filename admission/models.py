from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from .managers import UserManager

# Login details
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        primary_key=True
    )
    username = models.CharField(
        max_length= 100,
        null = False
    )
    password = models.CharField(
        max_length= 50,
        null = False
    )
    user_type = models.CharField(
        max_length=100,
        null=False
    )

    is_staff = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    last_login = None
    
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def get_full_name(self):
        return self.username
    
    def __str__(self):
        return self.email
    
# Applicant details loaded from excel
class Applicant_Details(models.Model):
    application_number = models.CharField(
        max_length= 50,
        primary_key=True
    )
    application_status = models.CharField(
        max_length=100,
        null=True
    )
    application_remark = models.CharField(
        max_length=50,
        null=True
    )
    application_date = models.CharField(
        max_length=100,
        null=True
    )
    first_name = models.CharField(
        max_length=100,
        null=True
    )
    middle_name = models.CharField(
        max_length=100,
        null=True
    )
    last_name = models.CharField(
        max_length=100,
        null=True
    )
    dob = models.CharField(
        max_length=100,
        null=True
    )
    gender = models.CharField(
        max_length=100,
        null=True
    )
    nationality = models.CharField(
        max_length=100,
        null=True
    )
    mobile_number = models.CharField(
        max_length=100,
        null=True
    )
    email_address = models.CharField(
        max_length= 50,
        null=True
    )
    caste_category = models.CharField(
        max_length= 100,
        null=True
    )
    addressline1 = models.CharField(
        max_length= 100,
        null=True
    )
    addressline2 = models.CharField(
        max_length= 100,
        null=True
    )
    country = models.CharField(
        max_length= 100,
        null=True
    )
    permanent_country = models.CharField(
        max_length= 50,
        null=True
    )
    fathers_name = models.CharField(
        max_length= 100,
        null=True
    )
    course_category = models.CharField(
        max_length= 100,
        null=True
    )
    ug_course_preference = models.CharField(
        max_length= 50,
        null=True
    )
    applied_program = models.CharField(
        max_length=200,
        null=True
    )
    admission_category = models.CharField(
        max_length= 100,
        null=True
    )
    law_course = models.CharField(
        max_length= 50,
        null=True
    )
    qualifying_exam = models.CharField(
        max_length= 100,
        null=True
    )
    board_university = models.CharField(
        max_length= 50,
        null=True
    )
    year_of_passing = models.IntegerField(
        null=True
    )
    state_of_board = models.CharField(
        max_length= 50,
        null=True
    )
    country_of_board = models.CharField(
        max_length= 100,
        null=True
    )
    other_board_or_university = models.CharField(
        max_length= 100,
        null=True
    )
    other_qualifying_examination = models.CharField(
        max_length= 50,
        null=True
    )
    name_of_institution = models.CharField(
        max_length= 100,
        null=True
    )
    aggregrate_percentage_including_language_for_UG = models.CharField(
        max_length= 50,
        null=True
    )
    aggregrate_percentage_excluding_language_for_UG = models.CharField(
        max_length= 100,
        null=True
    )
    aggregrate_percentage_including_language_for_PG = models.CharField(
        max_length= 50,
        null=True
    )
    aggregrate_percentage_excluding_language_for_PG = models.CharField(
        max_length= 100,
        null=True
    )
    tenth_percentage  = models.CharField(
        max_length= 50,
        null=True
    )
    tenth_year = models.IntegerField(
        null=True
    )
    twelfth_percentage = models.CharField(
        max_length= 50,
        null=True
    )
    twelfth_year = models.IntegerField(
        null=True
    )
    result_status = models.CharField(
        max_length= 100,
        null=True
    )
    qualification_details  = models.CharField(
        max_length= 50,
        null=True
    )
    district_of_board = models.CharField(
        max_length= 100,
        null=True
    )
    payment_status = models.CharField(
        max_length= 100,
        null=True
    )
    
    panel_assigned = models.ForeignKey(
        'Interview_panel',
        to_field='panel_id',
        on_delete=models.SET_NULL,
        null=True
    )

    token_no = models.IntegerField(
        null=True
    )

    interview_status_f1 = models.CharField(
        max_length=50,
        null=True
    )
    interview_status_f2 = models.CharField(
        max_length=50,
        null=True
    )
    interview_status_f3 = models.CharField(
        max_length=50,
        null=True
    )

    remark1 = models.ForeignKey(
        'Remarks',
        to_field="id",
        on_delete=models.DO_NOTHING,
        related_name='remark1',
        null=True
    )
    remark2 = models.ForeignKey(
        'Remarks',
        to_field="id",
        on_delete=models.DO_NOTHING,
        related_name='remark2',
        null=True
    )
    remark3 = models.ForeignKey(
        'Remarks',
        to_field="id",
        on_delete=models.DO_NOTHING,
        related_name='remark3',
        null=True
    )

    interview_id = models.ForeignKey(
        'Interview',
        to_field='id',
        on_delete=models.SET_NULL,
        null=True
    )

    selection_status = models.CharField(
        max_length=50,
        null=True
    )

    course_allotted = models.CharField(
        max_length=500,
        null=True
    )

    # one who selects the candidate finally (ususally principal)
    reviewer = models.ForeignKey(
        User,
        to_field="email",
        on_delete = models.DO_NOTHING,
        related_name='reviewer',
        null=True
    )

    def __str__(self):
        return self.application_number
    

# Interview session details
class Interview(models.Model):
    id = models.CharField(
        max_length=100,
        primary_key=True,
        unique=True,
        null=False
    )
    date = models.DateField()
    
    status = models.CharField(
        max_length=100,
        default="active"
    )

    def __str__(self):
        return self.id

    @property
    def panel_count(self):
        Interview_panel.objects.filter(interview_id=Interview.id).count()


# Interview panel details
class Interview_panel(models.Model):
    panel_id = models.CharField(
        max_length=100,
        primary_key=True
    )

    panel_type = models.CharField(
        max_length=2,
        null=False
    )
    
    course_handled = models.CharField(
        max_length=300,
        null=True
    )
    
    interview_id = models.ForeignKey(
        Interview,
        to_field="id",
        on_delete = models.CASCADE
    )
    interviewer1 = models.ForeignKey(
        User,
        to_field="email",
        on_delete = models.SET_NULL,
        related_name='interviewer1',
        null=True
    )
    interviewer2 = models.ForeignKey(
        User,
        to_field="email",
        on_delete = models.SET_NULL,
        related_name='interviewer2',
        null=True
    )
    interviewer3 = models.ForeignKey(
        User,
        to_field="email",
        on_delete = models.SET_NULL,
        related_name='interviewer3',
        null=True
    )

    panel_size = models.IntegerField(
        default=0,
        null=True
    )
    
    panel_active = models.BooleanField(
        default=True
    )
    
    def __str__(self):
        return self.panel_id


# Application remarks reviewers
class Remarks(models.Model):
    id = models.AutoField(
        primary_key=True
    )
    application_no = models.ForeignKey(
        Applicant_Details,
        to_field="application_number",
        on_delete=models.CASCADE
    )
    reviewer_id = models.ForeignKey(
        User,
        to_field="email",
        on_delete=models.DO_NOTHING,
        null=True
    )
    mode_of_education = models.CharField(
        max_length= 100,
        null=False
    )

    second_language = models.CharField(
        max_length=50,
        null=False
    )
    cocurricular_activities = models.CharField(
        max_length= 200,
        null=True
    )

    subject_knowledge = models.CharField(
        max_length = 100,
        null=True
    )

    attitude = models.CharField(
        max_length=100,
        null=True
    )

    communication = models.CharField(
        max_length=100,
        null=True
    )

    remarks = models.CharField(
        max_length=500,
        null=False
    )
    
    notes_for_admission_office = models.CharField(
        max_length= 500,
        null=True
    )

    interview_score = models.IntegerField(
        null=True
    )

    activity_score = models.IntegerField(
        null=True
    )

    def __str__(self):
        return str(self.application_no)

class Allotment_Details(models.Model):
    program = models.CharField(
        max_length=500,
        primary_key=True
    )

    intake = models.IntegerField()

    admitted = models.IntegerField(
        null=True
    )

    allotted = models.IntegerField(
        null=True
    )

    def __str__(self):
        return self.program
    
class Reviewers_Indicators(models.Model):
    application_number = models.OneToOneField(
        Applicant_Details,
        to_field="application_number",
        on_delete=models.CASCADE,
        primary_key=True
    )

    selection = models.CharField(
        max_length=100,
        null=True
    )

    reccomended_by = models.CharField(
        max_length=100,
        null=True
    )

    reference = models.CharField(
        max_length= 100,
        null=True
    )

    def __str__(self):
        return str(self.application_number)