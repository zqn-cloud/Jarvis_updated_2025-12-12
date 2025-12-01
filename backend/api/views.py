from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from datetime import timedelta, date
import uuid
import os

from .models import User, UserLocation, AccessToken, CalendarType, Event, EventLink, UploadedFile
from .serializers import (
    UserSerializer, UserLocationSerializer, CalendarTypeSerializer,
    CalendarTypeCreateSerializer, EventSerializer, EventCreateSerializer,
    EventUpdateSerializer, EventCompleteSerializer, LinkSerializer,
    LoginSerializer, LocationUpdateSerializer, UserUpdateSerializer,
    UploadedFileSerializer
)
from .authentication import TokenAuthentication


def make_response(data=None, message=None, success=True, status_code=200):
    """统一响应格式"""
    response = {
        'success': success,
        'server_time': timezone.now().isoformat()
    }
    if data is not None:
        response['data'] = data
    if message:
        response['message'] = message
    return Response(response, status=status_code)


def make_error_response(code, message, details=None, status_code=400):
    """统一错误响应格式"""
    error = {
        'code': code,
        'message': message
    }
    if details:
        error['details'] = details
    return Response({
        'success': False,
        'error': error,
        'server_time': timezone.now().isoformat()
    }, status=status_code)


def create_default_calendar_types(user):
    """为新用户创建默认日历类型"""
    default_types = [
        {'type_id': 'general', 'name': 'General', 'color': '#6B7280', 'is_deletable': False},
        {'type_id': 'routine', 'name': 'Routine', 'color': '#EC4899', 'is_deletable': True},
        {'type_id': 'events', 'name': 'Events', 'color': '#F59E0B', 'is_deletable': True},
        {'type_id': 'holidays', 'name': 'Holidays', 'color': '#3B82F6', 'is_deletable': True},
        {'type_id': 'school', 'name': 'School', 'color': '#22C55E', 'is_deletable': True},
    ]
    for type_data in default_types:
        CalendarType.objects.create(user=user, **type_data)


# ==================== AUTH ====================

@api_view(['POST'])
@authentication_classes([])
@permission_classes([AllowAny])
def auth_login(request):
    """用户登录"""
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return make_error_response('VALIDATION_ERROR', 'Invalid data', serializer.errors)
    
    account_id = serializer.validated_data['account_id']
    
    with transaction.atomic():
        user, is_new = User.objects.get_or_create(account_id=account_id)
        
        if is_new:
            create_default_calendar_types(user)
        
        # 创建新token
        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(days=7)
        
        AccessToken.objects.create(
            user=user,
            token=token,
            expires_at=expires_at
        )
    
    user_serializer = UserSerializer(user)
    
    return make_response({
        'access_token': token,
        'expires_in': 7 * 24 * 3600,
        'is_new_user': is_new,
        'user': user_serializer.data
    })


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def auth_logout(request):
    """用户登出"""
    if request.auth:
        request.auth.is_active = False
        request.auth.save()
    return make_response(message='Logged out successfully')


# ==================== TIME ====================

@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def get_server_time(request):
    """获取服务器时间"""
    now = timezone.now()
    return make_response({
        'server_time': now.isoformat(),
        'timezone': 'UTC',
        'date': now.strftime('%Y-%m-%d'),
        'timestamp': int(now.timestamp() * 1000)
    })


# ==================== USER ====================

@api_view(['GET', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_detail(request):
    """获取/更新用户信息"""
    user = request.user
    
    if request.method == 'GET':
        serializer = UserSerializer(user)
        return make_response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = UserUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return make_error_response('VALIDATION_ERROR', 'Invalid data', serializer.errors)
        
        if 'home_address' in serializer.validated_data:
            user.home_address = serializer.validated_data['home_address']
        if 'school_address' in serializer.validated_data:
            user.school_address = serializer.validated_data['school_address']
        user.save()
        
        return make_response(UserSerializer(user).data)


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def user_location(request):
    """获取/更新用户位置"""
    user = request.user
    
    if request.method == 'GET':
        latest_location = user.locations.first()
        if not latest_location:
            return make_response(None)
        
        return make_response({
            'latitude': latest_location.latitude,
            'longitude': latest_location.longitude,
            'accuracy': latest_location.accuracy,
            'timestamp': latest_location.timestamp.isoformat()
        })
    
    elif request.method == 'POST':
        serializer = LocationUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return make_error_response('VALIDATION_ERROR', 'Invalid data', serializer.errors)
        
        location = UserLocation.objects.create(
            user=user,
            latitude=serializer.validated_data['latitude'],
            longitude=serializer.validated_data['longitude'],
            accuracy=serializer.validated_data.get('accuracy')
        )
        
        # 只保留最新的2条位置记录，删除其他的
        old_locations = user.locations.order_by('-timestamp')[2:]
        for old_loc in old_locations:
            old_loc.delete()
        
        return make_response({
            'location_id': str(location.id),
            'latitude': location.latitude,
            'longitude': location.longitude,
            'accuracy': location.accuracy,
            'timestamp': location.timestamp.isoformat()
        })


# ==================== CALENDAR TYPES ====================

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def calendar_types_list(request):
    """获取/创建日历类型"""
    user = request.user
    
    if request.method == 'GET':
        types = CalendarType.objects.filter(user=user)
        serializer = CalendarTypeSerializer(types, many=True)
        return make_response(serializer.data)
    
    elif request.method == 'POST':
        serializer = CalendarTypeCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return make_error_response('VALIDATION_ERROR', 'Invalid data', serializer.errors)
        
        # 生成type_id
        name = serializer.validated_data['name']
        type_id = name.lower().replace(' ', '_') + '_' + str(uuid.uuid4())[:8]
        
        calendar_type = CalendarType.objects.create(
            user=user,
            type_id=type_id,
            name=name,
            color=serializer.validated_data['color'],
            is_deletable=True
        )
        
        return make_response(
            CalendarTypeSerializer(calendar_type).data,
            status_code=201
        )


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def calendar_type_detail(request, type_id):
    """获取/更新/删除日历类型"""
    user = request.user
    
    try:
        calendar_type = CalendarType.objects.get(user=user, type_id=type_id)
    except CalendarType.DoesNotExist:
        return make_error_response('NOT_FOUND', 'Calendar type not found', status_code=404)
    
    if request.method == 'GET':
        return make_response(CalendarTypeSerializer(calendar_type).data)
    
    elif request.method == 'PUT':
        if 'name' in request.data:
            calendar_type.name = request.data['name']
        if 'color' in request.data:
            calendar_type.color = request.data['color']
        calendar_type.save()
        return make_response(CalendarTypeSerializer(calendar_type).data)
    
    elif request.method == 'DELETE':
        if not calendar_type.is_deletable:
            return make_error_response('TYPE_NOT_DELETABLE', 'Cannot delete default type')
        
        # 将该类型的事件移到general
        general_type = CalendarType.objects.filter(user=user, type_id='general').first()
        events_count = Event.objects.filter(calendar_type=calendar_type).update(calendar_type=general_type)
        
        calendar_type.delete()
        
        return make_response(
            {'events_moved': events_count},
            message=f'Calendar type deleted. {events_count} events moved to General.'
        )


@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def calendar_type_visibility(request, type_id):
    """切换日历类型可见性"""
    user = request.user
    
    try:
        calendar_type = CalendarType.objects.get(user=user, type_id=type_id)
    except CalendarType.DoesNotExist:
        return make_error_response('NOT_FOUND', 'Calendar type not found', status_code=404)
    
    is_visible = request.data.get('is_visible')
    if is_visible is not None:
        calendar_type.is_visible = is_visible
        calendar_type.save()
    
    return make_response(CalendarTypeSerializer(calendar_type).data)


# ==================== EVENTS ====================

@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def events_list(request):
    """获取/创建事件"""
    user = request.user
    
    if request.method == 'GET':
        events = Event.objects.filter(user=user).select_related('calendar_type', 'attachment').prefetch_related('links')
        
        # 过滤
        date = request.query_params.get('date')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        type_id = request.query_params.get('type_id')
        completed = request.query_params.get('completed')
        
        if date:
            events = events.filter(date=date)
        if start_date:
            events = events.filter(date__gte=start_date)
        if end_date:
            events = events.filter(date__lte=end_date)
        if type_id:
            events = events.filter(calendar_type__type_id=type_id)
        if completed is not None:
            completed_bool = completed.lower() == 'true'
            events = events.filter(completed=completed_bool)
        
        serializer = EventSerializer(events, many=True, context={'request': request})
        return make_response({
            'events': serializer.data,
            'total': events.count()
        })
    
    elif request.method == 'POST':
        serializer = EventCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return make_error_response('VALIDATION_ERROR', 'Invalid data', serializer.errors)
        
        data = serializer.validated_data
        
        # 获取日历类型
        try:
            calendar_type = CalendarType.objects.get(user=user, type_id=data['type_id'])
        except CalendarType.DoesNotExist:
            return make_error_response('NOT_FOUND', f"Calendar type '{data['type_id']}' not found", status_code=404)
        
        # 获取附件
        attachment = None
        if data.get('attachment_id'):
            try:
                attachment = UploadedFile.objects.get(id=data['attachment_id'], user=user)
            except UploadedFile.DoesNotExist:
                pass
        
        with transaction.atomic():
            event = Event.objects.create(
                user=user,
                calendar_type=calendar_type,
                title=data['title'],
                date=data['date'],
                is_all_day=data['is_all_day'],
                start_time=data.get('start_time'),
                end_time=data.get('end_time'),
                location=data.get('location', ''),
                description=data.get('description', ''),
                attachment=attachment
            )
            
            # 创建链接
            for url in data.get('links', []):
                EventLink.objects.create(event=event, url=url)
        
        return make_response(
            EventSerializer(event, context={'request': request}).data,
            message='Event created successfully',
            status_code=201
        )


@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def event_detail(request, event_id):
    """获取/更新/删除事件"""
    user = request.user
    
    try:
        event = Event.objects.select_related('calendar_type', 'attachment').prefetch_related('links').get(id=event_id, user=user)
    except Event.DoesNotExist:
        return make_error_response('NOT_FOUND', 'Event not found', status_code=404)
    
    if request.method == 'GET':
        return make_response(EventSerializer(event, context={'request': request}).data)
    
    elif request.method == 'PUT':
        serializer = EventUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return make_error_response('VALIDATION_ERROR', 'Invalid data', serializer.errors)
        
        data = serializer.validated_data
        
        if 'title' in data:
            event.title = data['title']
        if 'date' in data:
            event.date = data['date']
        if 'is_all_day' in data:
            event.is_all_day = data['is_all_day']
        if 'start_time' in data:
            event.start_time = data['start_time']
        if 'end_time' in data:
            event.end_time = data['end_time']
        if 'location' in data:
            event.location = data['location']
        if 'description' in data:
            event.description = data['description']
        if 'completed' in data:
            event.completed = data['completed']
            if data['completed']:
                event.completed_at = timezone.now()
            else:
                event.completed_at = None
        if 'expanded' in data:
            event.expanded = data['expanded']
        
        if 'type_id' in data:
            try:
                calendar_type = CalendarType.objects.get(user=user, type_id=data['type_id'])
                event.calendar_type = calendar_type
            except CalendarType.DoesNotExist:
                pass
        
        event.save()
        
        return make_response(
            EventSerializer(event, context={'request': request}).data,
            message='Event updated successfully'
        )
    
    elif request.method == 'DELETE':
        # 删除关联的附件文件
        if event.attachment:
            attachment = event.attachment
            # 删除物理文件
            if attachment.file:
                try:
                    if os.path.isfile(attachment.file.path):
                        os.remove(attachment.file.path)
                except Exception as e:
                    print(f"Failed to delete file: {e}")
            # 删除数据库记录
            attachment.delete()
        
        event.delete()
        return make_response(message='Event deleted successfully')


@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def event_complete(request, event_id):
    """切换事件完成状态"""
    user = request.user
    
    try:
        event = Event.objects.get(id=event_id, user=user)
    except Event.DoesNotExist:
        return make_error_response('NOT_FOUND', 'Event not found', status_code=404)
    
    serializer = EventCompleteSerializer(data=request.data)
    if not serializer.is_valid():
        return make_error_response('VALIDATION_ERROR', 'Invalid data', serializer.errors)
    
    event.completed = serializer.validated_data['completed']
    if event.completed:
        event.completed_at = timezone.now()
    else:
        event.completed_at = None
    event.save()
    
    return make_response({
        'id': str(event.id),
        'completed': event.completed,
        'completed_at': event.completed_at.isoformat() if event.completed_at else None
    })


@api_view(['POST', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def event_links(request, event_id):
    """添加/删除事件链接"""
    user = request.user
    
    try:
        event = Event.objects.prefetch_related('links').get(id=event_id, user=user)
    except Event.DoesNotExist:
        return make_error_response('NOT_FOUND', 'Event not found', status_code=404)
    
    serializer = LinkSerializer(data=request.data)
    if not serializer.is_valid():
        return make_error_response('VALIDATION_ERROR', 'Invalid data', serializer.errors)
    
    url = serializer.validated_data['url']
    
    if request.method == 'POST':
        EventLink.objects.create(event=event, url=url)
        links = [link.url for link in event.links.all()]
        return make_response({'links': links})
    
    elif request.method == 'DELETE':
        EventLink.objects.filter(event=event, url=url).delete()
        links = [link.url for link in event.links.all()]
        return make_response({'links': links})


# ==================== FILES ====================

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def file_upload(request):
    """上传文件"""
    user = request.user
    
    if 'file' not in request.FILES:
        return make_error_response('VALIDATION_ERROR', 'No file provided')
    
    uploaded_file = request.FILES['file']
    
    # 检查文件大小 (10MB)
    if uploaded_file.size > 10 * 1024 * 1024:
        return make_error_response('FILE_TOO_LARGE', 'File size exceeds 10MB limit', status_code=413)
    
    file_obj = UploadedFile.objects.create(
        user=user,
        file=uploaded_file,
        original_name=uploaded_file.name,
        size=uploaded_file.size,
        mime_type=uploaded_file.content_type or 'application/octet-stream'
    )
    
    return make_response(
        UploadedFileSerializer(file_obj, context={'request': request}).data,
        status_code=201
    )


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def file_delete(request, file_id):
    """删除文件"""
    user = request.user
    
    try:
        file_obj = UploadedFile.objects.get(id=file_id, user=user)
    except UploadedFile.DoesNotExist:
        return make_error_response('NOT_FOUND', 'File not found', status_code=404)
    
    # 删除实际文件
    if file_obj.file:
        if os.path.isfile(file_obj.file.path):
            os.remove(file_obj.file.path)
    
    file_obj.delete()
    
    return make_response(message='File deleted successfully')


# ==================== REMINDERS (Placeholder) ====================

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def reminders_list(request):
    """获取智能提醒 - 返回静态数据作为占位"""
    # AI相关功能暂不实现，返回示例数据
    reminders = [
        {
            'id': 'rem_weather',
            'type': 'weather',
            'title': '今日天气',
            'subtitle': '多云转晴，18°C - 25°C，适合外出',
            'bg_color': '#EAF4FD',
            'icon_bg': '#60A5FA',
            'data': {
                'condition': 'partly_cloudy',
                'temp_min': 18,
                'temp_max': 25,
                'humidity': 65,
                'wind_speed': 12
            }
        },
        {
            'id': 'rem_commute',
            'type': 'commute',
            'title': '通勤信息',
            'subtitle': '前往学校约需 25 分钟，距离 8.5 公里',
            'bg_color': '#E8F5E9',
            'icon_bg': '#4ADE80',
            'data': {
                'from': 'home',
                'to': 'school',
                'duration_minutes': 25,
                'distance_km': 8.5,
                'traffic_status': 'normal'
            },
            'action_url': 'https://maps.google.com/'
        },
        {
            'id': 'rem_important',
            'type': 'important',
            'title': '重要提醒',
            'subtitle': '查看今日待办事项',
            'bg_color': '#FCE4EC',
            'icon_bg': '#F472B6',
            'data': {}
        }
    ]
    return make_response(reminders)


# ==================== COMMUTE (Placeholder) ====================

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def location_commute(request):
    """获取通勤信息 - 返回占位数据"""
    user = request.user
    
    from_param = request.query_params.get('from', 'home')
    to_param = request.query_params.get('to', 'school')
    
    return make_response({
        'from': {
            'type': from_param,
            'address': user.home_address if from_param == 'home' else user.school_address,
            'coordinates': {'lat': 22.3964, 'lng': 114.1095}
        },
        'to': {
            'type': to_param,
            'address': user.school_address if to_param == 'school' else user.home_address,
            'coordinates': {'lat': 22.4196, 'lng': 114.2068}
        },
        'routes': [
            {
                'mode': 'driving',
                'duration_minutes': 25,
                'distance_km': 8.5,
                'traffic_status': 'normal'
            },
            {
                'mode': 'transit',
                'duration_minutes': 35,
                'distance_km': 9.2,
                'transit_details': 'MTR East Rail Line'
            }
        ],
        'maps_url': 'https://maps.google.com/'
    })


# ==================== AGENT API ====================

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def agent_info(request):
    """
    为AI Agent提供完整的用户和日程信息
    包括：用户信息、位置、所有日历类型、所有事件
    """
    user = request.user
    
    # 获取用户位置
    current_location = None
    previous_location = None
    locations = list(user.locations.order_by('-timestamp')[:2])
    if len(locations) > 0:
        current_location = {
            'latitude': locations[0].latitude,
            'longitude': locations[0].longitude,
            'accuracy': locations[0].accuracy,
            'timestamp': locations[0].timestamp.isoformat()
        }
    if len(locations) > 1:
        previous_location = {
            'latitude': locations[1].latitude,
            'longitude': locations[1].longitude,
            'accuracy': locations[1].accuracy,
            'timestamp': locations[1].timestamp.isoformat()
        }
    
    # 获取所有日历类型
    calendar_types = CalendarType.objects.filter(user=user)
    types_data = [
        {
            'id': t.type_id,
            'name': t.name,
            'color': t.color,
            'is_visible': t.is_visible,
            'is_deletable': t.is_deletable,
            'event_count': t.events.count()
        }
        for t in calendar_types
    ]
    
    # 获取指定日期范围的事件（默认未来30天）
    from datetime import date, timedelta
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if not start_date:
        start_date = date.today()
    else:
        start_date = date.fromisoformat(start_date)
    
    if not end_date:
        end_date = start_date + timedelta(days=30)
    else:
        end_date = date.fromisoformat(end_date)
    
    events = Event.objects.filter(
        user=user,
        date__gte=start_date,
        date__lte=end_date
    ).select_related('calendar_type', 'attachment').prefetch_related('links').order_by('date', 'start_time')
    
    events_data = [
        {
            'id': str(e.id),
            'title': e.title,
            'date': e.date.isoformat(),
            'is_all_day': e.is_all_day,
            'start_time': e.start_time.strftime('%H:%M') if e.start_time else None,
            'end_time': e.end_time.strftime('%H:%M') if e.end_time else None,
            'location': e.location,
            'description': e.description,
            'type_id': e.calendar_type.type_id if e.calendar_type else 'general',
            'color': e.calendar_type.color if e.calendar_type else '#6B7280',
            'completed': e.completed,
            'links': [link.url for link in e.links.all()],
            'has_attachment': e.attachment is not None
        }
        for e in events
    ]
    
    # 统计信息
    total_events = events.count()
    completed_events = events.filter(completed=True).count()
    today_events = events.filter(date=date.today()).count()
    
    return make_response({
        'user': {
            'account_id': user.account_id,
            'home_address': user.home_address,
            'school_address': user.school_address
        },
        'location': {
            'current': current_location,
            'previous': previous_location
        },
        'calendar_types': types_data,
        'events': events_data,
        'summary': {
            'total_events': total_events,
            'completed_events': completed_events,
            'pending_events': total_events - completed_events,
            'today_events': today_events,
            'date_range': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        },
        'server_time': timezone.now().isoformat()
    })


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def agent_action(request):
    """
    Agent代理执行操作
    支持的操作:
    - create_event: 创建事件
    - update_event: 更新事件
    - delete_event: 删除事件
    - complete_event: 标记事件完成
    - create_calendar_type: 创建日历类型
    """
    user = request.user
    
    action = request.data.get('action')
    payload = request.data.get('payload', {})
    reason = request.data.get('reason', '')
    
    if not action:
        return make_error_response('VALIDATION_ERROR', 'Action is required')
    
    result = {'action': action, 'status': 'unknown', 'reason': reason}
    
    try:
        if action == 'create_event':
            # 创建事件
            calendar_type = CalendarType.objects.filter(
                user=user, 
                type_id=payload.get('type_id', 'general')
            ).first()
            
            if not calendar_type:
                calendar_type = CalendarType.objects.filter(user=user, type_id='general').first()
            
            event = Event.objects.create(
                user=user,
                calendar_type=calendar_type,
                title=payload.get('title', 'New Event'),
                date=payload.get('date', date.today()),
                is_all_day=payload.get('is_all_day', True),
                start_time=payload.get('start_time'),
                end_time=payload.get('end_time'),
                location=payload.get('location', ''),
                description=payload.get('description', '')
            )
            
            # 添加链接
            for url in payload.get('links', []):
                EventLink.objects.create(event=event, url=url)
            
            result['status'] = 'success'
            result['event_id'] = str(event.id)
            result['message'] = f"Event '{event.title}' created successfully"
        
        elif action == 'update_event':
            event_id = payload.get('event_id')
            event = Event.objects.get(id=event_id, user=user)
            
            if 'title' in payload:
                event.title = payload['title']
            if 'date' in payload:
                event.date = payload['date']
            if 'is_all_day' in payload:
                event.is_all_day = payload['is_all_day']
            if 'start_time' in payload:
                event.start_time = payload['start_time']
            if 'end_time' in payload:
                event.end_time = payload['end_time']
            if 'location' in payload:
                event.location = payload['location']
            if 'description' in payload:
                event.description = payload['description']
            
            event.save()
            result['status'] = 'success'
            result['message'] = f"Event '{event.title}' updated successfully"
        
        elif action == 'delete_event':
            event_id = payload.get('event_id')
            event = Event.objects.get(id=event_id, user=user)
            title = event.title
            event.delete()
            result['status'] = 'success'
            result['message'] = f"Event '{title}' deleted successfully"
        
        elif action == 'complete_event':
            event_id = payload.get('event_id')
            completed = payload.get('completed', True)
            event = Event.objects.get(id=event_id, user=user)
            event.completed = completed
            event.completed_at = timezone.now() if completed else None
            event.save()
            result['status'] = 'success'
            result['message'] = f"Event '{event.title}' marked as {'completed' if completed else 'incomplete'}"
        
        elif action == 'create_calendar_type':
            name = payload.get('name')
            color = payload.get('color', '#6B7280')
            
            type_id = name.lower().replace(' ', '_') + '_' + str(uuid.uuid4())[:8]
            
            calendar_type = CalendarType.objects.create(
                user=user,
                type_id=type_id,
                name=name,
                color=color,
                is_deletable=True
            )
            
            result['status'] = 'success'
            result['type_id'] = type_id
            result['message'] = f"Calendar type '{name}' created successfully"
        
        else:
            result['status'] = 'error'
            result['message'] = f"Unknown action: {action}"
    
    except Event.DoesNotExist:
        result['status'] = 'error'
        result['message'] = 'Event not found'
    except Exception as e:
        result['status'] = 'error'
        result['message'] = str(e)
    
    return make_response(result)
