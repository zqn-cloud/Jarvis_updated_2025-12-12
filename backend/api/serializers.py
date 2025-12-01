from rest_framework import serializers
from .models import User, UserLocation, CalendarType, Event, EventLink, UploadedFile


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    current_location = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['account_id', 'home_address', 'school_address', 'current_location', 'created_at', 'updated_at']
        read_only_fields = ['account_id', 'created_at', 'updated_at']
    
    def get_current_location(self, obj):
        latest_location = obj.locations.first()
        if latest_location:
            return {
                'latitude': latest_location.latitude,
                'longitude': latest_location.longitude,
                'accuracy': latest_location.accuracy,
                'timestamp': latest_location.timestamp.isoformat()
            }
        return None


class UserLocationSerializer(serializers.ModelSerializer):
    """用户位置序列化器"""
    class Meta:
        model = UserLocation
        fields = ['id', 'latitude', 'longitude', 'accuracy', 'timestamp']
        read_only_fields = ['id', 'timestamp']


class CalendarTypeSerializer(serializers.ModelSerializer):
    """日历类型序列化器"""
    event_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CalendarType
        fields = ['id', 'type_id', 'name', 'color', 'is_visible', 'is_deletable', 'event_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_event_count(self, obj):
        return obj.events.count()


class CalendarTypeCreateSerializer(serializers.Serializer):
    """创建日历类型的序列化器"""
    name = serializers.CharField(max_length=100)
    color = serializers.CharField(max_length=20)


class UploadedFileSerializer(serializers.ModelSerializer):
    """上传文件序列化器"""
    url = serializers.SerializerMethodField()
    name = serializers.CharField(source='original_name')
    
    class Meta:
        model = UploadedFile
        fields = ['id', 'name', 'url', 'size', 'mime_type', 'created_at']
        read_only_fields = ['id', 'url', 'size', 'mime_type', 'created_at']
    
    def get_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class EventLinkSerializer(serializers.ModelSerializer):
    """事件链接序列化器"""
    class Meta:
        model = EventLink
        fields = ['id', 'url', 'created_at']
        read_only_fields = ['id', 'created_at']


class EventSerializer(serializers.ModelSerializer):
    """事件序列化器"""
    links = serializers.SerializerMethodField()
    attachment = UploadedFileSerializer(read_only=True)
    color = serializers.SerializerMethodField()
    type_id = serializers.CharField(source='calendar_type.type_id', read_only=True)
    
    class Meta:
        model = Event
        fields = [
            'id', 'title', 'date', 'is_all_day', 'start_time', 'end_time',
            'location', 'description', 'type_id', 'color', 'completed', 'completed_at',
            'expanded', 'links', 'attachment', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'color', 'completed_at', 'created_at', 'updated_at']
    
    def get_links(self, obj):
        return [link.url for link in obj.links.all()]
    
    def get_color(self, obj):
        if obj.calendar_type:
            return obj.calendar_type.color
        return '#6B7280'


class EventCreateSerializer(serializers.Serializer):
    """创建/更新事件的序列化器"""
    title = serializers.CharField(max_length=500)
    date = serializers.DateField()
    is_all_day = serializers.BooleanField(default=True)
    start_time = serializers.TimeField(required=False, allow_null=True)
    end_time = serializers.TimeField(required=False, allow_null=True)
    location = serializers.CharField(required=False, allow_blank=True, default='')
    description = serializers.CharField(required=False, allow_blank=True, default='')
    type_id = serializers.CharField(max_length=100)
    # 使用CharField而不是URLField，允许更灵活的链接格式
    links = serializers.ListField(child=serializers.CharField(max_length=2000), required=False, default=list)
    attachment_id = serializers.UUIDField(required=False, allow_null=True)


class EventUpdateSerializer(serializers.Serializer):
    """更新事件的序列化器"""
    title = serializers.CharField(max_length=500, required=False)
    date = serializers.DateField(required=False)
    is_all_day = serializers.BooleanField(required=False)
    start_time = serializers.TimeField(required=False, allow_null=True)
    end_time = serializers.TimeField(required=False, allow_null=True)
    location = serializers.CharField(required=False, allow_blank=True)
    description = serializers.CharField(required=False, allow_blank=True)
    type_id = serializers.CharField(max_length=100, required=False)
    completed = serializers.BooleanField(required=False)
    expanded = serializers.BooleanField(required=False)


class EventCompleteSerializer(serializers.Serializer):
    """完成事件的序列化器"""
    completed = serializers.BooleanField()


class LinkSerializer(serializers.Serializer):
    """链接序列化器"""
    url = serializers.CharField(max_length=2000)  # 使用CharField允许更灵活的链接格式


class LoginSerializer(serializers.Serializer):
    """登录序列化器"""
    account_id = serializers.CharField(max_length=255)


class LocationUpdateSerializer(serializers.Serializer):
    """位置更新序列化器"""
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    accuracy = serializers.FloatField(required=False, allow_null=True)


class UserUpdateSerializer(serializers.Serializer):
    """用户信息更新序列化器"""
    home_address = serializers.CharField(required=False, allow_blank=True)
    school_address = serializers.CharField(required=False, allow_blank=True)

