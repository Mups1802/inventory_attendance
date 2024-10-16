from django.db import models
from datetime import datetime

class Student(models.Model):
    student_id = models.CharField(max_length=50, unique=True)  # Keeping this as CharField
    student_name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['student_name']

    def __str__(self):
        return f"{self.student_name} ({self.student_id})"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=datetime.now)  # Explicit date for attendance record
    time_in = models.DateTimeField(null=True, blank=True)
    time_out = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Attendance Record"
        verbose_name_plural = "Attendance Records"
        ordering = ['-time_in']

    def mark_attendance(self, time_in):
        """Marks attendance with time_in or updates time_out if already signed in."""
        if not self.time_in:
            self.time_in = time_in
        else:
            self.time_out = time_in
        self.save()

    def __str__(self):
        return f"{self.student.student_name} ({self.student.student_id}) - In: {self.time_in}, Out: {self.time_out}"

class Item(models.Model):
    id = models.CharField(max_length=100, primary_key=True)
    name = models.CharField(max_length=200)
    quantity = models.PositiveIntegerField()  # Ensure quantity cannot be negative

    def __str__(self):
        return f"{self.name} ({self.id})"
