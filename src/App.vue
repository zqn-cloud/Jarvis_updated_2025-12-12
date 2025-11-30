<template>
  <div class="app-wrapper">
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
            <DateNavigation v-model:date="currentDate" />
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
            <ReminderCarousel :reminders="reminders" />
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
      @close="showSettings = false"
      @save="handleSaveSettings"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
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
import './assets/main.css';

// State
const showCreateType = ref(false);
const showCreateEvent = ref(false);
const showSettings = ref(false);
const editingTask = ref(null);
const currentDate = ref(new Date(2025, 10, 30)); // November 30, 2025

const calendarTypes = ref([
  { id: 'general', name: 'General', color: '#6B7280', visible: true },
  { id: 'routine', name: 'Routine', color: '#EC4899', visible: true },
  { id: 'events', name: 'Events', color: '#F59E0B', visible: true },
  { id: 'holidays', name: 'Holidays', color: '#3B82F6', visible: true },
  { id: 'school', name: 'School', color: '#22C55E', visible: true },
]);

const tasks = ref([
  // November 28, 2025
  {
    id: '101',
    title: 'Gym Session',
    isAllDay: false,
    startTime: '07:00',
    endTime: '08:30',
    date: '2025-11-28',
    typeId: 'routine',
    color: '#EC4899',
    completed: false,
    expanded: false
  },
  {
    id: '102',
    title: 'Black Friday Shopping',
    isAllDay: true,
    date: '2025-11-28',
    typeId: 'events',
    color: '#F59E0B',
    completed: true,
    expanded: false
  },
  // November 29, 2025
  {
    id: '103',
    title: 'Weekend Brunch',
    isAllDay: false,
    startTime: '10:00',
    endTime: '12:00',
    date: '2025-11-29',
    typeId: 'events',
    color: '#F59E0B',
    completed: false,
    expanded: false
  },
  {
    id: '104',
    title: 'Study for Exams',
    isAllDay: false,
    startTime: '14:00',
    endTime: '18:00',
    date: '2025-11-29',
    typeId: 'school',
    color: '#22C55E',
    completed: false,
    expanded: false
  },
  // November 30, 2025 (Today)
  {
    id: '1',
    title: 'KAI BIRTHDAY TOMORROW',
    isAllDay: true,
    date: '2025-11-30',
    typeId: 'events',
    color: '#F59E0B',
    completed: false,
    expanded: false
  },
  {
    id: '2',
    title: 'SIGN UP TO UNI',
    isAllDay: true,
    date: '2025-11-30',
    typeId: 'events',
    color: '#F59E0B',
    completed: true,
    attachment: { name: 'DOcs.pdf', url: '#' },
    expanded: false,
    links: ['https://university.edu/apply']
  },
  {
    id: '3',
    title: 'Therapy',
    isAllDay: false,
    startTime: '15:00',
    endTime: '17:00',
    date: '2025-11-30',
    typeId: 'routine',
    color: '#EC4899',
    completed: false,
    expanded: false
  },
  {
    id: '105',
    title: 'Morning Yoga',
    isAllDay: false,
    startTime: '06:30',
    endTime: '07:30',
    date: '2025-11-30',
    typeId: 'routine',
    color: '#EC4899',
    completed: true,
    expanded: false
  },
  // December 1, 2025
  {
    id: '106',
    title: "Kai's Birthday Party",
    isAllDay: false,
    startTime: '18:00',
    endTime: '22:00',
    date: '2025-12-01',
    typeId: 'events',
    color: '#F59E0B',
    completed: false,
    expanded: false,
    location: "Kai's House"
  },
  {
    id: '107',
    title: 'Start of Advent',
    isAllDay: true,
    date: '2025-12-01',
    typeId: 'holidays',
    color: '#3B82F6',
    completed: false,
    expanded: false
  },
  // December 2, 2025
  {
    id: '108',
    title: 'Project Deadline',
    isAllDay: true,
    date: '2025-12-02',
    typeId: 'school',
    color: '#22C55E',
    completed: false,
    expanded: false,
    attachment: { name: 'Project_Brief.pdf', url: '#' }
  },
  {
    id: '109',
    title: 'Team Meeting',
    isAllDay: false,
    startTime: '10:00',
    endTime: '11:00',
    date: '2025-12-02',
    typeId: 'general',
    color: '#6B7280',
    completed: false,
    expanded: false
  },
  // December 3, 2025
  {
    id: '110',
    title: 'Doctor Appointment',
    isAllDay: false,
    startTime: '09:00',
    endTime: '10:00',
    date: '2025-12-03',
    typeId: 'routine',
    color: '#EC4899',
    completed: false,
    expanded: false,
    location: 'City Hospital'
  }
]);

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

// Computed - Filter tasks by selected date AND visible types
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

// Methods
const handleSelectDate = (date) => {
  currentDate.value = date;
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

const handleToggleCategory = (id) => {
  const cat = calendarTypes.value.find(c => c.id === id);
  if (cat) cat.visible = !cat.visible;
};

const handleDeleteType = (id) => {
  // Move all tasks of this type to "general"
  tasks.value = tasks.value.map(task => {
    if (task.typeId === id) {
      const generalType = calendarTypes.value.find(t => t.id === 'general');
      return { ...task, typeId: 'general', color: generalType?.color || '#6B7280' };
    }
    return task;
  });
  
  // Remove the type
  calendarTypes.value = calendarTypes.value.filter(c => c.id !== id);
};

const handleUpdateTask = (updatedTask) => {
  const index = tasks.value.findIndex(t => t.id === updatedTask.id);
  if (index !== -1) {
    tasks.value[index] = { ...tasks.value[index], ...updatedTask };
  }
};

const handleDeleteTask = (taskId) => {
  tasks.value = tasks.value.filter(t => t.id !== taskId);
};

const handleEditTask = (task) => {
  editingTask.value = { ...task };
  showCreateEvent.value = true;
};

const handleSaveType = (newType) => {
  calendarTypes.value.push({
    id: Date.now().toString(),
    name: newType.name,
    color: newType.color,
    visible: true
  });
};

const handleSaveEvent = (eventData) => {
  const type = calendarTypes.value.find(t => t.id === eventData.typeId);
  const color = type?.color || '#6B7280';
  
  if (eventData.id) {
    // Edit existing
    const index = tasks.value.findIndex(t => t.id === eventData.id);
    if (index !== -1) {
      tasks.value[index] = {
        ...tasks.value[index],
        ...eventData,
        color
      };
    }
  } else {
    // Create new
    tasks.value.push({
      id: Date.now().toString(),
      ...eventData,
      color,
      completed: false,
      expanded: false
    });
  }
};

const handleAITaskSubmit = (text) => {
  // TODO: Call AI API to parse natural language
  console.log('AI Task Input:', text);
  const type = calendarTypes.value.find(t => t.id === 'general');
  tasks.value.push({
    id: Date.now().toString(),
    title: text,
    isAllDay: true,
    date: format(currentDate.value, 'yyyy-MM-dd'),
    typeId: 'general',
    color: type?.color || '#6B7280',
    completed: false,
    expanded: false
  });
};

const handleEventAISubmit = (text) => {
  console.log('Event AI Input:', text);
};

const handleSaveSettings = (newSettings) => {
  console.log('Settings saved:', newSettings);
  // TODO: Call API to save settings
};
</script>

<style scoped>
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
