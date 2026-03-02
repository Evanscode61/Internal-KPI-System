import uuid
from django.db import models
from Base.models import BaseModel, Status


class Department(BaseModel):
    """
      Represents an organisational department e.g. Tech, Business, HR.
      departments can be added freely without changing the model.
      The line manager of a department is the User whose role is a line manager
      role AND whose User.department FK points to this department.
      """
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True)
    #line_manager = models.ForeignKey('LineManager',null =True,blank = False,
                                    ## on_delete=models.CASCADE,
                                     #verbose_name = 'Line Manager')"""



    class Meta:
        db_table = 'departments'

    def __str__(self):
        return self.name


class Team(BaseModel):
    """Team: sales team in business department, Backend team in tech department"""
    #Teams within a department.
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    team_name = models.CharField(max_length=100,null = True,blank = True)
    status = models.ForeignKey(Status, on_delete=models.CASCADE, null=True)



    class Meta:
        db_table = 'teams'

    def __str__(self):
        return f"{self.team_name} - {self.department.name}" if self.department else self.team_name


# Create your models here.
