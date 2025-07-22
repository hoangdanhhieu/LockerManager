from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, is_password_usable
import json

class User(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=False)
    sdt = models.CharField(max_length=255, unique=True, null=False, db_column='SDT')
    vector_id = models.JSONField(null=True, blank=True, db_column='VectorID')
    RegTime = models.DateTimeField(auto_now_add=True, db_column='RegTime')
    status = models.IntegerField(default = 0, db_column='status')
    class Meta:
        db_table = 'user'
        
    def __str__(self):
        return self.name
        
class Image(models.Model):
    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to='images')
    def __str__(self):
        return self.title

class UserImage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='Image')
    image = models.ForeignKey('Image', on_delete=models.SET_NULL, null=True, blank=True, related_name='UserImages')

    class Meta:
        db_table = 'UserImage'

    def __str__(self):
        return f"Avatar for {self.user.name}"

class Lock(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        db_column='UserID'
    )
    
    class Meta:
        db_table = 'Lock'
        
    def __str__(self):
        return f"Lock {self.id}"
# code = 0 alter \ 1 info \ 2 err
class Log(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.IntegerField(null=True, blank=True, db_column='Code')
    at_time = models.DateTimeField(auto_now_add=True, db_column='AtTime')
    details = models.TextField(null=True, blank=True)
    mark = models.BooleanField(default=False)
    locker = models.ForeignKey(
        Lock,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column='LockerID'
    )
    
    class Meta:
        db_table = 'Log'
        ordering = ['-at_time']
        
    def __str__(self):
        return f"Log {self.id} - {self.at_time}"

class AdminLock(models.Model):
    id = models.AutoField(primary_key=True)
    password = models.CharField(max_length=255, null=False)
    
    class Meta:
        db_table = 'Admin_Lock'

    def __str__(self):
        return f"Admin {self.id}"