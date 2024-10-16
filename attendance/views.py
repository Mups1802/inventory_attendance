from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Attendance, Student, Item
from datetime import datetime
import json
import traceback
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

# Helper function to handle JsonResponse for invalid method
def invalid_method_response():
    return JsonResponse({'status': 'error', 'message': 'Invalid request method!'}, status=405)

# Attendance-related views
def mark_attendance(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        time = request.POST.get('time')  # Assuming this can be time_in or time_out
        student = get_object_or_404(Student, student_id=student_id)

        attendance, created = Attendance.objects.get_or_create(
            student=student,
            date=datetime.now().date(),
        )

        if created:  # If it's a new attendance record
            attendance.time_in = time
        else:
            # If the record already exists, update time_out if it's not set
            if not attendance.time_out:
                attendance.time_out = time
        
        attendance.save()

        return JsonResponse({'status': 'success', 'message': 'Attendance marked successfully!'})
    
    return invalid_method_response()


def attendance_history(request):
    student_id = request.GET.get('student_id')
    student = get_object_or_404(Student, student_id=student_id)
    attendances = Attendance.objects.filter(student=student).values('date', 'time_in', 'time_out')
    return JsonResponse(list(attendances), safe=False)

@csrf_exempt  # Use if CSRF token is not being sent
def record_attendance(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            student_name = data.get('student_name')
            
            if not student_id or not student_name:
                return JsonResponse({'status': 'error', 'message': 'Missing student ID or name.'}, status=400)

            student, created = Student.objects.get_or_create(
                student_id=student_id,
                defaults={'student_name': student_name}
            )

            current_time = timezone.now()
            attendance, created = Attendance.objects.get_or_create(
                student=student,
                date=current_time.date(),
                defaults={'time_in': current_time}
            )

            if not created:
                if attendance.time_out:
                    # Create a new attendance record for the same day
                    attendance = Attendance.objects.create(
                        student=student,
                        date=current_time.date(),
                        time_in=current_time
                    )
                else:
                    attendance.time_out = current_time
                    attendance.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Attendance recorded successfully',
                'data': {
                    'student_id': student.student_id,
                    'student_name': student.student_name,
                    'date': attendance.date.isoformat(),
                    'time_in': attendance.time_in.isoformat() if attendance.time_in else None,
                    'time_out': attendance.time_out.isoformat() if attendance.time_out else None
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
def get_attendance_history(request):
    records = Attendance.objects.select_related('student').all().order_by('-date', '-time_in')
    data = [
        {
            'student_id': record.student.student_id,
            'student_name': record.student.student_name,
            'date': record.date.isoformat(),
            'time_in': record.time_in.isoformat() if record.time_in else None,
            'time_out': record.time_out.isoformat() if record.time_out else None,
        }
        for record in records
    ]
    return JsonResponse(data, safe=False)
@csrf_exempt
def add_update_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('id')
            name = data.get('name')
            quantity = data.get('quantity')

            if not item_id or not name:
                return JsonResponse({'status': 'error', 'message': 'Item ID and Name are required'}, status=400)

            try:
                quantity = int(quantity)
            except ValueError:
                return JsonResponse({'status': 'error', 'message': 'Quantity must be a number'}, status=400)

            item, created = Item.objects.update_or_create(
                id=item_id,
                defaults={'name': name, 'quantity': quantity}
            )
            action = 'added' if created else 'updated'

            return JsonResponse({'status': 'success', 'message': f'Item {action} successfully!'})
        except Exception as e:
            print(f"Error in add_update_item: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'}, status=500)
    
    return invalid_method_response()

@csrf_exempt
def get_inventory(request):
    try:
        items = Item.objects.all().values('id', 'name', 'quantity')
        return JsonResponse(list(items), safe=False)
    except Exception as e:
        print(f"Error in get_inventory: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return JsonResponse({'status': 'error', 'message': f'Error fetching inventory: {str(e)}'}, status=500)

def get_item(request, item_id):
    try:
        item = Item.objects.get(id=item_id)
        return JsonResponse({'id': item.id, 'name': item.name, 'quantity': item.quantity})
    except Item.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Item not found'}, status=404)

@csrf_exempt
def delete_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            item_id = data.get('id')
            item = get_object_or_404(Item, id=item_id)
            item.delete()

            return JsonResponse({'status': 'success', 'message': 'Item deleted successfully!'})
        except Exception as e:
            print(f"Error in delete_item: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Server error: {str(e)}'}, status=500)
    
    return invalid_method_response()

def attendance(request):
    history = Attendance.objects.all()
    return render(request, 'attendance.html', {'history': history})

def inventory(request):
    return render(request, 'inventory.html')
