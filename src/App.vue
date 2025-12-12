<template>
  <!-- Loading Screen -->
  <div v-if="isLoading" class="loading-screen">
    <div class="loading-spinner"></div>
    <p>Loading...</p>
  </div>

  <!-- Login Screen -->
  <LoginModal v-else-if="!isLoggedIn" @login="handleLogin" />

  <!-- Main App -->
  <div v-else class="app-wrapper">
    <div class="app-container">
      <Sidebar>
        <template #mini-calendar>
          <MiniCalendar 
            :selectedDate="currentDate" 
            @select-date="handleSelectDate" 
          />
        </template>
        <template #create-button>
          <CreateButton @open-modal="handleOpenModal" />
        </template>
        <template #category-filter>
          <CategoryFilter 
            :categories="calendarTypes" 
            @toggle="handleToggleCategory" 
            @delete-type="handleDeleteType"
          />
        </template>
      </Sidebar>
      
      <main class="main-content">
        <!-- Header Bar -->
        <header class="header-bar">
          <div class="header-left">
            <DateNavigation v-model:date="currentDate" @go-today="goToToday" />
          </div>
          <div class="header-right">
            <button class="header-icon-btn active">
              <Check :size="16" />
              <Calendar :size="16" />
            </button>
            <button class="header-icon-btn" @click="showSettings = true">
              <Settings :size="16" />
            </button>
          </div>
        </header>

        <!-- Content Area -->
        <div class="content-area">
          <!-- Tasks Section -->
          <section class="tasks-section">
            <!-- When has tasks -->
            <template v-if="filteredTasks.length > 0">
              <TaskList 
                :tasks="filteredTasks" 
                @update-task="handleUpdateTask"
                @delete-task="handleDeleteTask"
                @edit-task="handleEditTask"
              />
              <AITaskDialog @submit="handleAITaskSubmit" />
            </template>
            
            <!-- Empty state - same line -->
            <div v-else class="empty-row">
              <span class="empty-text">Have a nice day ☀️</span>
              <AITaskDialog @submit="handleAITaskSubmit" />
            </div>
          </section>

          <!-- Reminder Section -->
          <section class="reminder-section">
            <ReminderCarousel :reminders="reminders" @refresh="handleRefreshReminders" />
          </section>
        </div>
      </main>
    </div>

    <!-- Modals -->
    <CreateCalendarTypeModal 
      v-if="showCreateType" 
      @close="showCreateType = false" 
      @save="handleSaveType"
    />
    <CreateEventModal 
      v-if="showCreateEvent" 
      :calendarTypes="calendarTypes"
      :initialDate="currentDate"
      :editTask="editingTask"
      @close="closeEventModal"
      @save="handleSaveEvent"
      @ai-submit="handleEventAISubmit"
    />
    <SettingsModal 
      v-if="showSettings" 
      :accountId="currentUser.accountId"
      :homeAddress="currentUser.homeAddress"
      :schoolAddress="currentUser.schoolAddress"
      @close="showSettings = false"
      @save="handleSaveSettings"
      @logout="handleLogout"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { format } from 'date-fns';
import { Check, Calendar, Settings } from 'lucide-vue-next';
import Sidebar from './components/layout/Sidebar.vue';
import MiniCalendar from './components/calendar/MiniCalendar.vue';
import CreateButton from './components/layout/CreateButton.vue';
import CategoryFilter from './components/CategoryFilter.vue';
import DateNavigation from './components/calendar/DateNavigation.vue';
import TaskList from './components/tasks/TaskList.vue';
import AITaskDialog from './components/AITaskDialog.vue';
import ReminderCarousel from './components/ReminderCarousel.vue';
import CreateCalendarTypeModal from './components/modals/CreateCalendarTypeModal.vue';
import CreateEventModal from './components/modals/CreateEventModal.vue';
import SettingsModal from './components/modals/SettingsModal.vue';
import LoginModal from './components/modals/LoginModal.vue';
import { authAPI, userAPI, calendarTypesAPI, eventsAPI, filesAPI, agentAPI, setAccessToken, getAccessToken } from './services/api.js';
import './assets/main.css';

// ==================== STATE ====================
const isLoading = ref(true);
const isLoggedIn = ref(false);
const currentUser = ref({
  accountId: '',
  homeAddress: '',
  schoolAddress: '',
  currentLocation: null
});

const showCreateType = ref(false);
const showCreateEvent = ref(false);
const showSettings = ref(false);
const editingTask = ref(null);

const currentDate = ref(new Date());
const calendarTypes = ref([]);
const tasks = ref([]);

const reminders = ref([
  {
    id: 'weather',
    type: 'weather',
    title: '今日天气',
    subtitle: '多云转晴，18°C - 25°C，适合外出',
    bgColor: '#EAF4FD',
    iconBg: '#60A5FA'
  },
  {
    id: 'commute',
    type: 'commute',
    title: '通勤信息',
    subtitle: '前往学校约需 25 分钟，距离 8.5 公里',
    bgColor: '#E8F5E9',
    iconBg: '#4ADE80'
  },
  {
    id: 'birthday',
    type: 'important',
    title: '重要提醒',
    subtitle: '明天是 Kai 的生日，记得准备礼物 🎁',
    bgColor: '#FCE4EC',
    iconBg: '#F472B6'
  }
]);

// ==================== DATA TRANSFORMATION ====================
// 后端 snake_case -> 前端 camelCase
const transformEventFromBackend = (event) => ({
  id: event.id,
  title: event.title,
  date: event.date,
  isAllDay: event.is_all_day,
  startTime: event.start_time,
  endTime: event.end_time,
  location: event.location || '',
  typeId: event.type_id,
  color: event.color,
  completed: event.completed,
  expanded: event.expanded || false,
  links: event.links || [],
  attachment: event.attachment
});

// 前端 camelCase -> 后端 snake_case
const transformEventToBackend = (event) => ({
  title: event.title,
  date: event.date,
  is_all_day: event.isAllDay,
  start_time: event.startTime || null,
  end_time: event.endTime || null,
  location: event.location || '',
  type_id: event.typeId,
  links: event.links || [],
  attachment_id: event.attachmentId || null
});

const transformTypeFromBackend = (type) => ({
  id: type.type_id,
  name: type.name,
  color: type.color,
  visible: type.is_visible,
  isDeletable: type.is_deletable
});

// ==================== API CALLS ====================
const loadUserData = async () => {
  try {
    const userRes = await userAPI.getUser();
    if (userRes.success) {
      currentUser.value = {
        accountId: userRes.data.account_id,
        homeAddress: userRes.data.home_address || '',
        schoolAddress: userRes.data.school_address || '',
        currentLocation: userRes.data.current_location
      };
    }
  } catch (err) {
    console.error('Failed to load user data:', err);
  }
};

const loadCalendarTypes = async () => {
  try {
    const res = await calendarTypesAPI.getAll();
    if (res.success) {
      calendarTypes.value = res.data.map(transformTypeFromBackend);
    }
  } catch (err) {
    console.error('Failed to load calendar types:', err);
  }
};

const loadEvents = async () => {
  try {
    const res = await eventsAPI.getAll();
    if (res.success) {
      tasks.value = res.data.events.map(transformEventFromBackend);
    }
  } catch (err) {
    console.error('Failed to load events:', err);
  }
};

const refreshData = async () => {
  await Promise.all([
    loadUserData(),
    loadCalendarTypes(),
    loadEvents()
  ]);
};

// ==================== INIT ====================
onMounted(async () => {
  // 确保初始状态为未登录
  isLoggedIn.value = false;
  
  // Check for existing token
  const token = getAccessToken();
  if (token) {
    try {
      // 先验证token是否有效，通过获取用户信息
      const userRes = await userAPI.getUser();
      
      // 如果用户API成功，说明token有效，继续加载其他数据
      if (userRes.success) {
        currentUser.value = {
          accountId: userRes.data.account_id,
          homeAddress: userRes.data.home_address || '',
          schoolAddress: userRes.data.school_address || '',
          currentLocation: userRes.data.current_location
        };
        
        // 并行加载其他数据
        const [typesRes, eventsRes] = await Promise.all([
          calendarTypesAPI.getAll(),
          eventsAPI.getAll()
        ]);
        
        if (typesRes.success) {
          calendarTypes.value = typesRes.data.map(transformTypeFromBackend);
        }
        
        if (eventsRes.success) {
          tasks.value = eventsRes.data.events.map(transformEventFromBackend);
        }
        
        // 只有成功加载所有数据后才设置为已登录
        isLoggedIn.value = true;
      } else {
        // API返回失败，清除token
        setAccessToken(null);
        localStorage.removeItem('jarvis_access_token');
      }
    } catch (err) {
      console.error('Session invalid:', err);
      // 任何错误都清除token，显示登录界面
      setAccessToken(null);
      localStorage.removeItem('jarvis_access_token');
      isLoggedIn.value = false;
    }
  }
  isLoading.value = false;
});

// ==================== COMPUTED ====================
const filteredTasks = computed(() => {
  const visibleTypeIds = calendarTypes.value.filter(t => t.visible).map(t => t.id);
  const dateStr = format(currentDate.value, 'yyyy-MM-dd');
  
  return tasks.value.filter(task => {
    const taskDate = task.date;
    const isSameDateStr = taskDate === dateStr;
    const isVisibleType = visibleTypeIds.includes(task.typeId);
    return isSameDateStr && isVisibleType;
  });
});

// ==================== AUTH HANDLERS ====================
const handleLogin = async (accountId) => {
  isLoading.value = true;
  try {
    const res = await authAPI.login(accountId);
    if (res.success) {
      // 直接从登录响应中获取用户信息
      currentUser.value = {
        accountId: res.data.user.account_id,
        homeAddress: res.data.user.home_address || '',
        schoolAddress: res.data.user.school_address || '',
        currentLocation: res.data.user.current_location
      };
      // 加载日历类型和事件
      await Promise.all([loadCalendarTypes(), loadEvents()]);
      isLoggedIn.value = true;
    }
  } catch (err) {
    console.error('Login failed:', err);
    alert('Login failed. Please try again.');
  } finally {
    isLoading.value = false;
  }
};

const handleLogout = async () => {
  isLoading.value = true;
  try {
    await authAPI.logout();
  } catch (err) {
    console.error('Logout error:', err);
  } finally {
    isLoggedIn.value = false;
    showSettings.value = false;
    currentUser.value = { accountId: '', homeAddress: '', schoolAddress: '', currentLocation: null };
    tasks.value = [];
    calendarTypes.value = [];
    isLoading.value = false;
  }
};

// ==================== CALENDAR HANDLERS ====================
const handleSelectDate = (date) => {
  currentDate.value = date;
};

const goToToday = () => {
  currentDate.value = new Date();
};

const handleOpenModal = (type) => {
  if (type === 'calendar-type') showCreateType.value = true;
  if (type === 'event') {
    editingTask.value = null;
    showCreateEvent.value = true;
  }
};

const closeEventModal = () => {
  showCreateEvent.value = false;
  editingTask.value = null;
};

const handleToggleCategory = async (id) => {
  const cat = calendarTypes.value.find(c => c.id === id);
  if (cat) {
    const newVisible = !cat.visible;
    cat.visible = newVisible;
    
    try {
      await calendarTypesAPI.toggleVisibility(id, newVisible);
    } catch (err) {
      console.error('Failed to toggle visibility:', err);
      cat.visible = !newVisible; // revert
    }
  }
};

const handleDeleteType = async (id) => {
  try {
    await calendarTypesAPI.delete(id);
    // Reload data to get updated events
    await Promise.all([loadCalendarTypes(), loadEvents()]);
  } catch (err) {
    console.error('Failed to delete type:', err);
    alert('Failed to delete calendar type');
  }
};

// ==================== TASK HANDLERS ====================
const handleUpdateTask = async (updatedTask) => {
  const index = tasks.value.findIndex(t => t.id === updatedTask.id);
  if (index !== -1) {
    // Optimistic update
    const oldTask = { ...tasks.value[index] };
    tasks.value[index] = { ...tasks.value[index], ...updatedTask };
    
    try {
      if ('completed' in updatedTask && Object.keys(updatedTask).length === 2) {
        // Only completion status changed
        await eventsAPI.toggleComplete(updatedTask.id, updatedTask.completed);
      } else {
        // Other fields changed
        await eventsAPI.update(updatedTask.id, transformEventToBackend(updatedTask));
      }
    } catch (err) {
      console.error('Failed to update task:', err);
      tasks.value[index] = oldTask; // revert
    }
  }
};

const handleDeleteTask = async (taskId) => {
  const index = tasks.value.findIndex(t => t.id === taskId);
  if (index !== -1) {
    const deletedTask = tasks.value[index];
    tasks.value.splice(index, 1);
    
    try {
      await eventsAPI.delete(taskId);
    } catch (err) {
      console.error('Failed to delete task:', err);
      tasks.value.splice(index, 0, deletedTask); // revert
    }
  }
};

const handleEditTask = (task) => {
  editingTask.value = { ...task };
  showCreateEvent.value = true;
};

const handleSaveType = async (newType) => {
  try {
    const res = await calendarTypesAPI.create(newType.name, newType.color);
    if (res.success) {
      calendarTypes.value.push(transformTypeFromBackend(res.data));
      showCreateType.value = false;
    }
  } catch (err) {
    console.error('Failed to create type:', err);
    alert('Failed to create calendar type');
  }
};

const handleSaveEvent = async (eventData) => {
  const type = calendarTypes.value.find(t => t.id === eventData.typeId);
  const color = type?.color || '#6B7280';
  
  try {
    // 处理附件删除
    if (eventData.deleteAttachment) {
      try {
        await filesAPI.delete(eventData.deleteAttachment);
      } catch (e) {
        console.error('Failed to delete attachment:', e);
      }
    }
    
    // 处理文件上传
    let attachmentId = null;
    if (eventData.attachment) {
      if (eventData.attachment.file) {
        // 新文件需要上传
        const uploadRes = await filesAPI.upload(eventData.attachment.file);
        if (uploadRes.success) {
          attachmentId = uploadRes.data.id;
        }
      } else if (eventData.attachment.id) {
        // 已有文件，使用现有ID
        attachmentId = eventData.attachment.id;
      }
    }
    
    // 构建后端数据
    const backendData = {
      ...transformEventToBackend(eventData),
      attachment_id: attachmentId
    };
    
    if (eventData.id) {
      // Edit existing - 需要同步更新链接
      const res = await eventsAPI.update(eventData.id, backendData);
      if (res.success) {
        // 获取原始任务的链接，用于对比
        const originalTask = tasks.value.find(t => t.id === eventData.id);
        const originalLinks = originalTask?.links || [];
        const newLinks = eventData.links || [];
        
        // 删除被移除的链接
        for (const link of originalLinks) {
          if (!newLinks.includes(link)) {
            try {
              await eventsAPI.removeLink(eventData.id, link);
            } catch (e) {
              console.error('Failed to remove link:', e);
            }
          }
        }
        
        // 添加新链接
        for (const link of newLinks) {
          if (!originalLinks.includes(link)) {
            try {
              await eventsAPI.addLink(eventData.id, link);
            } catch (e) {
              console.error('Failed to add link:', e);
            }
          }
        }
        
        // 重新获取更新后的事件数据
        const updatedRes = await eventsAPI.get(eventData.id);
        if (updatedRes.success) {
          const index = tasks.value.findIndex(t => t.id === eventData.id);
          if (index !== -1) {
            tasks.value[index] = transformEventFromBackend(updatedRes.data);
          }
        }
        closeEventModal();
      }
    } else {
      // Create new
      const res = await eventsAPI.create(backendData);
      if (res.success) {
        tasks.value.push(transformEventFromBackend(res.data));
        closeEventModal();
      }
    }
  } catch (err) {
    console.error('Failed to save event:', err);
    alert('Failed to save event');
  }
};

const handleAITaskSubmit = async (text) => {
  // 调用Agent解析任务并直接创建到今天
  try {
    // 优先走本地 agent_service（8001），失败再回退到后端直接创建普通任务
    const AGENT_SERVICE_BASE = import.meta.env.VITE_AGENT_SERVICE_BASE || 'http://localhost:8001';
    const resp = await fetch(`${AGENT_SERVICE_BASE}/parse-task`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_input: text })
    });
    if (!resp.ok) throw new Error(`agent_service ${resp.status}`);
    const res = await resp.json();
    // agent_service 直接返回后端 /agent/parse-task 的响应体
    if (res.event) {
      tasks.value.push(transformEventFromBackend(res.event));
      currentDate.value = new Date();
      return;
    }
  } catch (err) {
    console.error('AI Task creation failed:', err);
  }

  // 如果AI解析失败，回退到直接创建普通任务
  const eventData = {
    title: text,
    date: format(new Date(), 'yyyy-MM-dd'), // 今天
    isAllDay: true,
    typeId: 'general'
  };
  
  try {
    const res = await eventsAPI.create(transformEventToBackend(eventData));
    if (res.success) {
      tasks.value.push(transformEventFromBackend(res.data));
      currentDate.value = new Date();
    }
  } catch (e) {
    console.error('Failed to create task:', e);
  }
};

const handleEventAISubmit = async (text, formRef) => {
  // 调用Agent解析事件
  try {
    const res = await agentAPI.parseEvent({ user_input: text });
    if (res.success && res.data.parsed) {
      // 返回解析结果给表单
      return res.data.parsed;
    }
  } catch (err) {
    console.error('AI Event parse failed:', err);
  }
  return null;
};

// AI Reminder 刷新
const handleRefreshReminders = async () => {
  // 设置超时时间（10秒）
  const TIMEOUT_MS = 10000;
  // 尝试从浏览器获取定位并同步到后端，避免提醒缺少位置
  const syncBrowserLocation = async () => {
    if (!('geolocation' in navigator)) return;
    return new Promise((resolve) => {
      const geoTimeout = setTimeout(() => resolve(null), 3000);
      navigator.geolocation.getCurrentPosition(
        async (pos) => {
          clearTimeout(geoTimeout);
          const { latitude, longitude, accuracy } = pos.coords;
          try {
            await userAPI.updateLocation(latitude, longitude, accuracy || null);
            currentUser.value.currentLocation = { latitude, longitude, accuracy };
          } catch (e) {
            console.warn('updateLocation failed', e);
          }
          resolve(null);
        },
        () => {
          clearTimeout(geoTimeout);
          resolve(null);
        },
        { enableHighAccuracy: true, timeout: 2500, maximumAge: 60000 }
      );
    });
  };
  
  try {
    // 先尝试获取并同步浏览器定位（不阻塞后续流程）
    await syncBrowserLocation();

    // 优先调用本地 agent_service（已封装上下文获取和生成逻辑）
    const AGENT_SERVICE_BASE = import.meta.env.VITE_AGENT_SERVICE_BASE || 'http://localhost:8001';
    const res = await Promise.race([
      fetch(`${AGENT_SERVICE_BASE}/generate-reminders`, { method: 'POST' }),
      new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), TIMEOUT_MS))
    ]);
    if (!res.ok) throw new Error(`agent_service ${res.status}`);
    const body = await res.json();
    const list = Array.isArray(body)
      ? body
      : (body.reminders || (body.data && body.data.reminders) || []);
    if (list.length > 0) {
      reminders.value = list.map(r => ({
        id: r.id,
        type: r.type,
        title: r.title,
        subtitle: r.subtitle,
        bgColor: r.bg_color,
        iconBg: r.icon_bg
      }));
      return;
    }

    // 回退方案：旧逻辑（直接调用后端）保持不变
    const contextRes = await Promise.race([
      agentAPI.getReminderContext(),
      new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), TIMEOUT_MS))
    ]);
    if (!contextRes.success) {
      console.error('Failed to get reminder context');
      return;
    }
    const remindersRes = await Promise.race([
      agentAPI.generateReminders(),
      new Promise((_, reject) => setTimeout(() => reject(new Error('Timeout')), TIMEOUT_MS))
    ]);
    if (remindersRes.success && remindersRes.data && remindersRes.data.length > 0) {
      reminders.value = remindersRes.data.map(r => ({
        id: r.id,
        type: r.type,
        title: r.title,
        subtitle: r.subtitle,
        bgColor: r.bg_color,
        iconBg: r.icon_bg
      }));
    }
  } catch (err) {
    // 超时或其他错误，保持之前的数据不变
    console.error('Failed to refresh reminders:', err);
  }
};

const handleSaveSettings = async (settings) => {
  try {
    await userAPI.updateUser({
      home_address: settings.homeAddress,
      school_address: settings.schoolAddress
    });
    
    currentUser.value.homeAddress = settings.homeAddress;
    currentUser.value.schoolAddress = settings.schoolAddress;
    
    if (settings.currentLocation) {
      await userAPI.updateLocation(
        settings.currentLocation.latitude,
        settings.currentLocation.longitude,
        settings.currentLocation.accuracy
      );
      currentUser.value.currentLocation = settings.currentLocation;
    }
  } catch (err) {
    console.error('Failed to save settings:', err);
    alert('Failed to save settings');
  }
};
</script>

<style scoped>
.loading-screen {
  position: fixed;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #E0E7FF 0%, #F3E8FF 50%, #FCE7F3 100%);
  gap: 16px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #E5E7EB;
  border-top-color: #6366F1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-screen p {
  color: var(--text-secondary);
  font-size: 14px;
}

.app-wrapper {
  width: 100vw;
  height: 100vh;
  background-color: #E8EAED;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.app-container {
  display: flex;
  width: 100%;
  max-width: 1100px;
  height: 100%;
  max-height: 750px;
  background-color: #F8F9FA;
  border-radius: 24px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,0.08);
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #F3F4F6;
  overflow: hidden;
}

.header-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background-color: #F3F4F6;
  min-height: 64px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.header-icon-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  border-radius: 8px;
  color: var(--text-secondary);
  background: transparent;
  border: none;
  cursor: pointer;
}

.header-icon-btn.active {
  background-color: #E0E7FF;
  color: #4F46E5;
}

.header-icon-btn:hover:not(.active) {
  background-color: rgba(0,0,0,0.05);
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 24px 24px;
  overflow-y: auto;
  gap: 20px;
}

.tasks-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reminder-section {
  margin-top: auto;
}

.empty-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 30px 0;
}

.empty-text {
  color: var(--text-secondary);
  font-style: italic;
  font-size: 16px;
}
</style>
