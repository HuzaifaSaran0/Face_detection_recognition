# attendance/models.py
from django.db import models
import numpy as np
import json

class Student(models.Model):
    name = models.CharField(max_length=100)
    ag_number = models.CharField(max_length=50, unique=True)
    class_name = models.CharField(max_length=50, default="CS")
    section = models.CharField(max_length=10)
    courses = models.CharField(max_length=200)  # Comma-separated string: "AI,Math,DS"
    face_encoding = models.TextField()  # Stores 128-d array as JSON string
    timestamp = models.DateTimeField(auto_now_add=True)

    def get_encoding_array(self):
        """Return face encoding as numpy array"""
        return np.array(json.loads(self.face_encoding))

    def __str__(self):
        return f"{self.name} ({self.ag_number})"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=[("Present", "Present"), ("Absent", "Absent")], default="Present")

    def __str__(self):
        return f"{self.student.name} - {self.course} - {self.timestamp.strftime('%Y-%m-%d')}"
