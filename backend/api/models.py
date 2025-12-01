from django.db import models
import uuid


class User(models.Model):
    """用户模型 - 使用account_id作为唯一标识"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account_id = models.CharField(max_length=255, unique=True, db_index=True)
    home_address = models.TextField(blank=True, default='')
    school_address = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.account_id
    
    # Django REST Framework 需要的属性
    @property
    def is_authenticated(self):
        """Always return True for authenticated users."""
        return True
    
    @property
    def is_anonymous(self):
        """Always return False for authenticated users."""
        return False


class UserLocation(models.Model):
    """用户位置记录"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')
    latitude = models.FloatField()
    longitude = models.FloatField()
    accuracy = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'user_locations'
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.account_id} @ {self.latitude}, {self.longitude}"


class AccessToken(models.Model):
    """访问令牌"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    token = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'access_tokens'

    def __str__(self):
        return f"Token for {self.user.account_id}"


class CalendarType(models.Model):
    """日历类型/分类"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='calendar_types')
    type_id = models.CharField(max_length=100)  # e.g., 'general', 'routine', 'events'
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=20)  # e.g., '#6B7280'
    is_visible = models.BooleanField(default=True)
    is_deletable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calendar_types'
        unique_together = ['user', 'type_id']

    def __str__(self):
        return f"{self.user.account_id} - {self.name}"


class UploadedFile(models.Model):
    """上传的文件"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='attachments/')
    original_name = models.CharField(max_length=255)
    size = models.IntegerField()
    mime_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'uploaded_files'

    def __str__(self):
        return self.original_name


class Event(models.Model):
    """事件/任务"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    calendar_type = models.ForeignKey(CalendarType, on_delete=models.SET_NULL, null=True, related_name='events')
    
    title = models.CharField(max_length=500)
    date = models.DateField()
    is_all_day = models.BooleanField(default=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    location = models.TextField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    expanded = models.BooleanField(default=False)
    
    attachment = models.ForeignKey(UploadedFile, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.user.account_id} - {self.title}"


class EventLink(models.Model):
    """事件关联的链接"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='links')
    url = models.URLField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_links'

    def __str__(self):
        return f"{self.event.title} - {self.url}"
