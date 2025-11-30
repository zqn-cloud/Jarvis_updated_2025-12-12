<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <!-- AI Input -->
      <div class="ai-input-row">
        <Sparkles :size="16" class="ai-icon" />
        <input 
          v-model="aiInput" 
          type="text" 
          placeholder="chat with ai to create event..." 
          class="ai-input"
          @keyup.enter="handleAISubmit"
        />
        <button class="ai-submit-btn" @click="handleAISubmit" :disabled="!aiInput.trim()">
          <Send :size="16" />
        </button>
        <button class="close-btn" @click="$emit('close')">
          <X :size="18" />
        </button>
      </div>

      <!-- Form -->
      <div class="form-content">
        <!-- Title -->
        <div class="form-group">
          <label>Title</label>
          <input type="text" v-model="form.title" placeholder="Event title" class="form-input" />
        </div>

        <!-- Date & All Day -->
        <div class="form-row">
          <div class="form-group flex-1">
            <label>Date</label>
            <div class="date-picker-wrapper">
              <CalendarIcon :size="16" />
              <input 
                type="date" 
                v-model="form.date" 
                class="date-input"
              />
              <span class="date-display">{{ formattedDate }}</span>
            </div>
          </div>
          <div class="form-group all-day-group">
            <label>All day</label>
            <button 
              class="toggle-switch" 
              :class="{ active: form.isAllDay }" 
              @click="form.isAllDay = !form.isAllDay"
            >
              <span class="toggle-knob"></span>
            </button>
          </div>
        </div>

        <!-- Time Range -->
        <div class="form-row" v-if="!form.isAllDay">
          <div class="form-group flex-1">
            <label>Start Time</label>
            <div class="time-input-wrapper">
              <Clock :size="16" />
              <input type="time" v-model="form.startTime" class="time-input" />
              <Clock :size="16" class="right-icon" />
            </div>
          </div>
          <div class="form-group flex-1">
            <label>End Time</label>
            <div class="time-input-wrapper">
              <Clock :size="16" />
              <input type="time" v-model="form.endTime" class="time-input" />
              <Clock :size="16" class="right-icon" />
            </div>
          </div>
        </div>

        <!-- Location -->
        <div class="form-group">
          <label>Location</label>
          <div class="icon-input">
            <MapPin :size="16" />
            <input type="text" v-model="form.location" placeholder="Add location" />
          </div>
        </div>

        <!-- Calendar Type -->
        <div class="form-group">
          <label>Calendar Type</label>
          <div class="type-select" @click="showTypeDropdown = !showTypeDropdown">
            <div class="type-preview">
              <span class="type-dot" :style="{ backgroundColor: selectedType?.color }"></span>
              <span>{{ selectedType?.name || 'Select type' }}</span>
            </div>
            <ChevronDown :size="16" />
          </div>
          
          <div v-if="showTypeDropdown" class="dropdown">
            <div 
              v-for="type in calendarTypes" 
              :key="type.id" 
              class="dropdown-item"
              @click="selectType(type)"
            >
              <span class="type-dot" :style="{ backgroundColor: type.color }"></span>
              <span>{{ type.name }}</span>
            </div>
          </div>
        </div>

        <!-- Links -->
        <div class="form-group">
          <label>Links</label>
          <div v-if="form.links && form.links.length > 0" class="links-list">
            <div v-for="(link, index) in form.links" :key="index" class="link-item">
              <LinkIcon :size="14" />
              <span class="link-text">{{ link }}</span>
              <button class="remove-link" @click="removeLink(index)">
                <X :size="14" />
              </button>
            </div>
          </div>
          <div class="add-link-row">
            <div class="icon-input">
              <LinkIcon :size="16" />
              <input 
                type="text" 
                v-model="newLink" 
                placeholder="Add URL" 
                @keyup.enter="addLink"
              />
            </div>
            <button class="add-link-btn" @click="addLink" :disabled="!newLink.trim()">
              <Plus :size="16" />
            </button>
          </div>
        </div>

        <!-- File Upload -->
        <div class="form-group">
          <label>Attachment</label>
          <div class="file-upload-wrapper">
            <input 
              type="file" 
              ref="fileInput"
              @change="handleFileChange"
              class="file-input"
            />
            <div class="file-upload-btn" @click="$refs.fileInput.click()">
              <Paperclip :size="16" />
              <span v-if="!form.attachment">Choose file...</span>
              <span v-else class="file-name">{{ form.attachment.name }}</span>
            </div>
            <button v-if="form.attachment" class="clear-file" @click="clearFile">
              <X :size="14" />
            </button>
          </div>
        </div>
      </div>

      <!-- Save Button -->
      <button class="save-btn" @click="handleSave" :disabled="!form.title.trim()">
        {{ editTask ? 'Update Event' : 'Save Event' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue';
import { format } from 'date-fns';
import { X, Sparkles, Send, Calendar as CalendarIcon, Clock, MapPin, Link as LinkIcon, ChevronDown, Paperclip, Plus } from 'lucide-vue-next';

const props = defineProps({
  calendarTypes: {
    type: Array,
    default: () => []
  },
  initialDate: {
    type: Date,
    default: () => new Date()
  },
  editTask: {
    type: Object,
    default: null
  }
});

const emit = defineEmits(['close', 'save', 'ai-submit']);

const fileInput = ref(null);
const aiInput = ref('');
const showTypeDropdown = ref(false);
const newLink = ref('');

const formatDateForInput = (date) => {
  return format(date, 'yyyy-MM-dd');
};

const form = reactive({
  title: '',
  date: formatDateForInput(props.initialDate),
  isAllDay: false,
  startTime: '09:00',
  endTime: '10:00',
  location: '',
  links: [],
  typeId: props.calendarTypes[0]?.id || 'general',
  attachment: null
});

// If editing, populate form
watch(() => props.editTask, (task) => {
  if (task) {
    form.title = task.title || '';
    form.date = task.date || formatDateForInput(props.initialDate);
    form.isAllDay = task.isAllDay || false;
    form.startTime = task.startTime || '09:00';
    form.endTime = task.endTime || '10:00';
    form.location = task.location || '';
    form.links = task.links ? [...task.links] : [];
    form.typeId = task.typeId || 'general';
    form.attachment = task.attachment || null;
  }
}, { immediate: true });

const selectedType = computed(() => {
  return props.calendarTypes.find(t => t.id === form.typeId) || props.calendarTypes[0];
});

const formattedDate = computed(() => {
  try {
    const date = new Date(form.date);
    return format(date, 'MMMM do, yyyy');
  } catch {
    return '';
  }
});

const selectType = (type) => {
  form.typeId = type.id;
  showTypeDropdown.value = false;
};

const handleFileChange = (e) => {
  const file = e.target.files[0];
  if (file) {
    form.attachment = {
      name: file.name,
      file: file,
      url: URL.createObjectURL(file)
    };
  }
};

const clearFile = () => {
  form.attachment = null;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
};

const addLink = () => {
  if (!newLink.value.trim()) return;
  if (!form.links) form.links = [];
  form.links.push(newLink.value.trim());
  newLink.value = '';
};

const removeLink = (index) => {
  form.links.splice(index, 1);
};

const handleAISubmit = () => {
  if (!aiInput.value.trim()) return;
  emit('ai-submit', aiInput.value.trim());
};

const handleSave = () => {
  if (!form.title.trim()) return;
  emit('save', {
    id: props.editTask?.id,
    title: form.title.trim(),
    date: form.date,
    isAllDay: form.isAllDay,
    startTime: form.isAllDay ? null : form.startTime,
    endTime: form.isAllDay ? null : form.endTime,
    location: form.location,
    links: form.links,
    typeId: form.typeId,
    attachment: form.attachment
  });
  emit('close');
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  width: 420px;
  max-height: 90vh;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  overflow-y: auto;
}

.ai-input-row {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 2px solid #6366F1;
  border-radius: 24px;
  padding: 10px 16px;
  margin-bottom: 24px;
}

.ai-icon {
  color: #6B7280;
  flex-shrink: 0;
}

.ai-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  color: var(--text-primary);
}

.ai-input::placeholder {
  color: #9CA3AF;
}

.ai-submit-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background-color: #6366F1;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.2s;
}

.ai-submit-btn:hover:not(:disabled) {
  background-color: #4F46E5;
}

.ai-submit-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.close-btn {
  color: #6B7280;
  padding: 4px;
  flex-shrink: 0;
}

.close-btn:hover {
  color: var(--text-primary);
}

.form-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
}

.form-row {
  display: flex;
  gap: 12px;
}

.flex-1 {
  flex: 1;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: relative;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-input {
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 12px 14px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #6366F1;
}

/* Date Picker */
.date-picker-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 12px 14px;
  position: relative;
}

.date-input {
  position: absolute;
  opacity: 0;
  width: 100%;
  height: 100%;
  left: 0;
  top: 0;
  cursor: pointer;
}

.date-display {
  font-size: 14px;
  color: var(--text-primary);
}

/* All Day Toggle */
.all-day-group {
  align-items: center;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 8px 14px;
  flex-direction: row !important;
  justify-content: space-between;
  min-width: 120px;
}

.toggle-switch {
  width: 44px;
  height: 24px;
  background-color: #E5E7EB;
  border-radius: 12px;
  position: relative;
  cursor: pointer;
  transition: background-color 0.2s;
  border: none;
  padding: 2px;
}

.toggle-switch.active {
  background-color: #6366F1;
}

.toggle-knob {
  width: 20px;
  height: 20px;
  background: white;
  border-radius: 50%;
  position: absolute;
  top: 2px;
  left: 2px;
  transition: transform 0.2s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.toggle-switch.active .toggle-knob {
  transform: translateX(20px);
}

/* Time Input */
.time-input-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 12px 14px;
}

.time-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  color: var(--text-primary);
}

.right-icon {
  color: #9CA3AF;
}

/* Icon Input */
.icon-input {
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 12px 14px;
  color: #9CA3AF;
  flex: 1;
}

.icon-input input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 14px;
  color: var(--text-primary);
}

.icon-input input::placeholder {
  color: #9CA3AF;
}

/* Type Select */
.type-select {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 12px 14px;
  cursor: pointer;
}

.type-preview {
  display: flex;
  align-items: center;
  gap: 10px;
}

.type-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

/* Dropdown */
.dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  margin-top: 4px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  z-index: 10;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
}

.dropdown-item:hover {
  background-color: #F9FAFB;
}

/* Links */
.links-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 8px;
}

.link-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #F3F4F6;
  border-radius: 8px;
  font-size: 13px;
}

.link-text {
  flex: 1;
  color: #3B82F6;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remove-link {
  color: var(--text-secondary);
  padding: 2px;
}

.remove-link:hover {
  color: #EF4444;
}

.add-link-row {
  display: flex;
  gap: 8px;
}

.add-link-btn {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background-color: #F3F4F6;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.add-link-btn:hover:not(:disabled) {
  background-color: #E5E7EB;
  color: var(--text-primary);
}

.add-link-btn:disabled {
  opacity: 0.4;
}

/* File Upload */
.file-upload-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-input {
  display: none;
}

.file-upload-btn {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 1px dashed #E5E7EB;
  border-radius: 12px;
  padding: 12px 14px;
  cursor: pointer;
  color: #9CA3AF;
  transition: all 0.2s;
}

.file-upload-btn:hover {
  border-color: #6366F1;
  color: #6366F1;
}

.file-name {
  color: var(--text-primary);
}

.clear-file {
  padding: 8px;
  color: var(--text-secondary);
}

.clear-file:hover {
  color: #EF4444;
}

/* Save Button */
.save-btn {
  width: 100%;
  background-color: #6366F1;
  color: white;
  padding: 14px;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
}

.save-btn:hover:not(:disabled) {
  background-color: #4F46E5;
}

.save-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
