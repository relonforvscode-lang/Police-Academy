from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.hashers import make_password, check_password
from .models import User, Assignment, Evaluation, Message, Notification
from django.db import IntegrityError
from django.db.models import Q
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import datetime

# --- Helpers ---
def get_session_user(request):
    uid = request.session.get('uid')
    if not uid:
        return None
    try:
        return User.objects.get(id=uid)
    except User.DoesNotExist:
        return None

def role_required(roles):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            user = get_session_user(request)
            if not user or user.role not in roles:
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# --- Auth ---
def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        try:
            user = User.objects.get(username=u)
            # Check password (supporting both plain for legacy and hashed for new)
            if check_password(p, user.password) or p == user.password:
                request.session['uid'] = user.id
                request.session['role'] = user.role
                request.session['name'] = user.full_name
                
                # Upgrade password to hash if it was plain
                if p == user.password:
                    user.set_password(p)
                    user.save()
                
                if user.role == 'admin': return redirect('admin_dashboard')
                if user.role == 'trainer': return redirect('trainer_dashboard')
                if user.role == 'cadet': return redirect('cadet_dashboard')
            else:
                return render(request, 'login.html', {'error': 'بيانات الدخول غير صحيحة'})
        except User.DoesNotExist:
            return render(request, 'login.html', {'error': 'المستخدم غير موجود'})
    return render(request, 'login.html')

def logout_view(request):
    request.session.flush()
    return redirect('login')

# --- Dashboards ---
@role_required(['admin'])
def admin_dashboard(request):
    users = User.objects.exclude(role='admin').order_by('role', 'username')
    return render(request, 'admin_dashboard.html', {'users': users})

@role_required(['admin'])
def admin_member_detail(request, uid):
    target_user = get_object_or_404(User, id=uid)
    
    if target_user.role == 'trainer':
        evals = Evaluation.objects.filter(trainer=target_user).select_related('cadet')
    elif target_user.role == 'cadet':
        evals = Evaluation.objects.filter(cadet=target_user).select_related('trainer')
    else:
        evals = []

    # Get Chat History - organize by conversation partner
    all_messages = Message.objects.filter(
        models.Q(sender=target_user) | models.Q(receiver=target_user)
    ).select_related('sender', 'receiver').order_by('created_at')
    
    # Group messages by conversation partner
    chats_dict = {}
    for msg in all_messages:
        # Determine the other person in the conversation
        other_user = msg.receiver if msg.sender == target_user else msg.sender
        
        if other_user.id not in chats_dict:
            chats_dict[other_user.id] = {
                'other': other_user,
                'messages': []
            }
        
        chats_dict[other_user.id]['messages'].append({
            'sender_id': msg.sender.id,
            'content': msg.content,
            'timestamp': msg.created_at
        })
    
    # Convert to list
    chats = list(chats_dict.values())
    
    if request.method == 'POST':
        msg_content = request.POST.get('message')
        Notification.objects.create(user=target_user, message=msg_content)
        return redirect('admin_member_detail', uid=uid)

    return render(request, 'admin_member_detail.html', {
        'target': target_user, 
        'evaluations': evals,
        'chats': chats
    })

@role_required(['trainer'])
def trainer_dashboard(request):
    user = get_session_user(request)
    assignments = Assignment.objects.filter(trainer=user).select_related('cadet')
    
    # Get cadets with unread message counts
    cadets_data = []
    for a in assignments:
        unread_count = Message.objects.filter(
            sender=a.cadet,
            receiver=user,
            is_read=False
        ).count()
        cadets_data.append({
            'cadet': a.cadet,
            'unread_count': unread_count
        })
    
    notifs = Notification.objects.filter(user=user, is_read=False)
    return render(request, 'trainer_dashboard.html', {
        'cadets_data': cadets_data,
        'user': user,
        'notifications': notifs
    })

@role_required(['cadet'])
def cadet_dashboard(request):
    user = get_session_user(request)
    assignments = Assignment.objects.filter(cadet=user).select_related('trainer')
    
    # Get trainers with unread message counts
    trainers_data = []
    for a in assignments:
        unread_count = Message.objects.filter(
            sender=a.trainer,
            receiver=user,
            is_read=False
        ).count()
        trainers_data.append({
            'trainer': a.trainer,
            'unread_count': unread_count
        })
    
    notifications = Notification.objects.filter(user=user, is_read=False).order_by('-created_at')
    return render(request, 'cadet_dashboard.html', {
        'user': user,
        'trainers_data': trainers_data,
        'notifications': notifications
    })

# --- Admin CRUD ---
@role_required(['admin'])
def admin_add_user(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        fn = request.POST.get('full_name')
        r = request.POST.get('role')
        try:
            user = User(username=u, full_name=fn, role=r)
            user.set_password(p)
            user.save()
            return redirect('admin_dashboard')
        except IntegrityError:
            return render(request, 'user_form.html', {'title': 'إضافة مستخدم', 'error': 'اسم المستخدم موجود مسبقاً'})
    return render(request, 'user_form.html', {'title': 'إضافة مستخدم'})

@role_required(['admin'])
def admin_edit_user(request, uid):
    user = get_object_or_404(User, id=uid)
    if request.method == 'POST':
        p = request.POST.get('password')
        fn = request.POST.get('full_name')
        user.full_name = fn
        if p:
            user.set_password(p)
        user.save()
        return redirect('admin_dashboard')
    return render(request, 'user_form.html', {'title': 'تعديل مستخدم', 'edit_user': user})

@role_required(['admin'])
def admin_delete_user(request, uid):
    user = get_object_or_404(User, id=uid)
    user.delete()
    return redirect('admin_dashboard')

@role_required(['admin'])
def admin_assignments_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'assign':
            tid = request.POST.get('trainer_id')
            cid = request.POST.get('cadet_id')
            trainer = get_object_or_404(User, id=tid)
            cadet = get_object_or_404(User, id=cid)
            Assignment.objects.get_or_create(trainer=trainer, cadet=cadet)
        elif action == 'delete':
            aid = request.POST.get('assignment_id')
            Assignment.objects.filter(id=aid).delete()
        return redirect('admin_assignments')

    trainers = User.objects.filter(role='trainer')
    cadets = User.objects.filter(role='cadet')
    assignments = Assignment.objects.all().select_related('trainer', 'cadet')
    return render(request, 'assignments.html', {'trainers': trainers, 'cadets': cadets, 'assignments': assignments})

# --- Features ---
from django.utils import timezone
import json

def chat_view(request, other_id):
    user = get_session_user(request)
    if not user: 
        return redirect('login')
    
    other = get_object_or_404(User, id=other_id)
    
    if user.role != 'admin':
        is_assigned = Assignment.objects.filter(
            models.Q(trainer=user, cadet=other) | models.Q(trainer=other, cadet=user)
        ).exists()
        if not is_assigned:
            return HttpResponseForbidden("غير مسموح لك بمراسلة هذا المستخدم")

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        if content:
            msg = Message.objects.create(
                sender=user, 
                receiver=other, 
                content=content
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'id': msg.id,
                    'content': msg.content,
                    'timestamp': msg.created_at.isoformat(),
                    'time': msg.created_at.strftime("%H:%M"),
                    'date': msg.created_at.strftime("%Y/%m/%d")
                })
            
            return redirect('chat', other_id=other_id)
    
    # إرسال timestamps مع الرسائل
    messages = Message.objects.filter(
        models.Q(sender=user, receiver=other) | 
        models.Q(sender=other, receiver=user)
    ).order_by('created_at')
    
    # Mark messages from other person as read
    Message.objects.filter(
        sender=other,
        receiver=user,
        is_read=False
    ).update(is_read=True)
    
    # تحويل الرسائل إلى قائمة مع timestamps
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'sender_id': msg.sender.id,
            'timestamp': msg.created_at.isoformat(),
            'time': msg.created_at.strftime("%H:%M"),
            'date': msg.created_at.strftime("%Y/%m/%d")
        })
    
    return render(request, 'chat.html', {
        'messages_json': json.dumps(messages_data),  # إرسال كـ JSON
        'messages': messages,
        'other': other, 
        'user': user,
        'my_id': user.id
    })

@csrf_exempt
def chat_messages_api(request, other_id):
    user = get_session_user(request)
    if not user:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    other = get_object_or_404(User, id=other_id)
    
    # Security Check
    if user.role != 'admin':
        is_assigned = Assignment.objects.filter(
            models.Q(trainer=user, cadet=other) | models.Q(trainer=other, cadet=user)
        ).exists()
        if not is_assigned:
            return JsonResponse({'error': 'Forbidden'}, status=403)
    
    # الحصول على الرسائل الجديدة فقط
    last_id = request.GET.get('last_id', 0)
    try:
        last_id = int(last_id)
    except:
        last_id = 0
    
    messages = Message.objects.filter(
        (models.Q(sender=user, receiver=other) | models.Q(sender=other, receiver=user))
    ).filter(id__gt=last_id).order_by('created_at')
    
    messages_data = []
    for msg in messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'sender_id': msg.sender.id,
            'timestamp': msg.created_at.isoformat()  # تنسيق ISO الكامل
        })
    
    return JsonResponse({'messages': messages_data})


@role_required(['trainer'])
def evaluate_view(request, cadet_id):
    trainer = get_session_user(request)
    cadet = get_object_or_404(User, id=cadet_id)
    
    # Security Check: Ensure trainer is assigned to this cadet
    is_assigned = Assignment.objects.filter(trainer=trainer, cadet=cadet).exists()
    if not is_assigned:
        return HttpResponseForbidden("غير مسموح لك بتقييم متدرب غير تحت إشرافك")

    if request.method == 'POST':
        score = int(request.POST.get('score'))
        comment = request.POST.get('comment')
        
        Evaluation.objects.create(trainer=trainer, cadet=cadet, score=score, comments=comment)
        
        if score < 50:
            Notification.objects.create(
                user=cadet, 
                message=f"تنبيه: لقد حصلت على تقييم بدرجة ({score}) نأمل منك التطوير. في حال وجود أي استفسار تواصل مع المدرب."
            )
            
        return redirect('trainer_dashboard')
        
    return render(request, 'evaluation_form.html', {'cadet': cadet})

def mark_read(request, nid):
    user = get_session_user(request)
    if not user: return JsonResponse({'status': 'error'}, status=403)
    
    notif = get_object_or_404(Notification, id=nid, user=user)
    notif.is_read = True
    notif.save()
    return JsonResponse({'status': 'ok'})

def get_unread_messages_count(request):
    user = get_session_user(request)
    if not user:
        return JsonResponse({'status': 'error'}, status=403)
    
    # Get unread messages grouped by sender
    from django.db.models import Count
    counts = Message.objects.filter(receiver=user, is_read=False).values('sender').annotate(count=Count('id'))
    
    unread_data = {item['sender']: item['count'] for item in counts}
        
    return JsonResponse({'counts': unread_data})
