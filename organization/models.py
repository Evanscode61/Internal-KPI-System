from django.db import models
from Base.models import BaseModel

class Department(BaseModel):
    """Department: TECH or Business."""
    class Name(models.TextChoices):
        TECH = 'TECH', 'TECH'
        BUSINESS = 'BUSINESS', 'Business'

    name = models.CharField(max_length=20, choices=Name.choices, unique=True)
    description = models.CharField(max_length=255, blank=True)
    """line_manager = models.ForeignKey('LineManager',null =True,blank = False,
                                     on_delete=models.CASCADE,
                                     verbose_name = 'Line Manager')"""



    class Meta:
        db_table = 'departments'

    def __str__(self):
        return self.get_name_display()


class Team(models.Model):
    #Teams within a department.
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=100,null = True,blank = True)


    class Meta:
        db_table = 'teams'

    def __str__(self):
        return f"{self.team_name} - {self.department.name}" if self.department else self.team_name


# Create your models here.
