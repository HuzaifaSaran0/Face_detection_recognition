# attendance/views.py

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import Student, Attendance
from django.utils.timezone import now
import face_recognition
import numpy as np
import json
import cv2
import base64
from io import BytesIO
from PIL import Image
from django.urls import reverse



def home(request):
    return render(request, "attendance/home.html")


@csrf_exempt
def add_student(request):
    if request.method == "POST":
        try:
            name = request.POST['name']
            ag_number = request.POST['ag_number']
            class_name = request.POST['class_name']
            section = request.POST['section']
            courses = request.POST['courses']
            image_data = request.POST['image']

            # Decode base64 image
            format, imgstr = image_data.split(';base64,') 
            img_bytes = base64.b64decode(imgstr)
            img = Image.open(BytesIO(img_bytes)).convert('RGB')
            img_np = np.array(img)

            # Detect face encoding
            face_locations = face_recognition.face_locations(img_np)
            encodings = face_recognition.face_encodings(img_np, face_locations)
            if not encodings:
                return HttpResponseBadRequest("No face detected.")
            face_encoding = encodings[0]

            # Compare with existing students
            all_students = Student.objects.all()
            for student in all_students:
                known_encoding = student.get_encoding_array()
                match = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.5)
                if match[0]:
                    return render(request, "attendance/add_student.html", {
                        "error": f"This face is already registered as {student.name} ({student.ag_number}).Now take <a href='{reverse('mark_attendance_page')}'>Attendance</a>.",
                        "form_data": request.POST,
                    })


            # Save to DB if no match
            student = Student(
                name=name,
                ag_number=ag_number,
                class_name=class_name,
                section=section,
                courses=courses,
                face_encoding=json.dumps(face_encoding.tolist())
            )
            student.save()

            return render(request, "attendance/add_student.html", {
                "success": f"Student {student.name} ({student.ag_number}) has been registered successfully. Now take <a href='{reverse('mark_attendance_page')}'>Attendance</a>."
            })


        except Exception as e:
            return HttpResponseBadRequest(f"Error: {str(e)}")

    return render(request, "attendance/add_student.html")


@csrf_exempt
def mark_attendance(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            image_data = body['image']
            course = body.get('course')

            if not course:
                return JsonResponse({"error": "Course is required."}, status=400)

            format, imgstr = image_data.split(';base64,')
            img_bytes = base64.b64decode(imgstr)
            img = Image.open(BytesIO(img_bytes)).convert('RGB')
            img.save("test_capture.jpg")
            img_np = np.array(img)

            # unknown_encodings = face_recognition.face_encodings(img_np)
            # Detect face locations first
            face_locations = face_recognition.face_locations(img_np)
            print("Face locations:", face_locations)
            unknown_encodings = face_recognition.face_encodings(img_np, face_locations)
            if not unknown_encodings:
                return JsonResponse({"error": "No face detected."}, status=400)

            unknown_encoding = unknown_encodings[0]

            all_students = Student.objects.all()
            for student in all_students:
                known_encoding = np.array(json.loads(student.face_encoding))
                results = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.5)
                if results[0]:
                    today = now().date()
                    already_marked = Attendance.objects.filter(
                        student=student,
                        course=course,
                        timestamp__date=today
                    ).exists()

                    if already_marked:
                        return JsonResponse({"message": f"{student.name} is already marked present for {course}."})
                    else:
                        Attendance.objects.create(
                            student=student,
                            course=course,
                            status="Present"
                        )
                        return JsonResponse({"message": f"{student.name} marked present for {course}."})

            return JsonResponse({"error": "Face not recognized."}, status=400)

        except Exception as e:
            return JsonResponse({"error": f"{str(e)}"}, status=400)

    return JsonResponse({"error": "Invalid request method."}, status=400)

def mark_attendance_page(request):
    return render(request, "attendance/mark_attendance.html")
