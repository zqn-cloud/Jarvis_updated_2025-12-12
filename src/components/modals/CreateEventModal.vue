<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <!-- AI Input -->
      <div class="ai-input-row">
        <Sparkles :size="16" class="ai-icon" />
        <textarea 
          ref="aiTextarea"
          v-model="aiInput" 
          placeholder="chat with ai to create event..." 
          class="ai-input"
          rows="1"
          @keydown.enter.exact.prevent="handleAISubmit"
          @input="autoResizeTextarea"
        ></textarea>
        <button class="ai-submit-btn" @click="handleAISubmit" :disabled="!aiInput.trim() || isLoading">
          <Send v-if="!isLoading" :size="16" />
          <div v-else class="loading-spinner-small"></div>
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
              <span v-if="!hasValidAttachment">Choose file...</span>
              <span v-else class="file-name">{{ form.attachment.name }}</span>
            </div>
            <button v-if="hasValidAttachment" class="clear-file" @click.stop="clearFile" type="button">
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
import { agentAPI } from '../../services/api.js';

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
const aiTextarea = ref(null);
const aiInput = ref('');
const showTypeDropdown = ref(false);
const newLink = ref('');
const isLoading = ref(false);

// 自动调整textarea高度
const autoResizeTextarea = () => {
  if (aiTextarea.value) {
    aiTextarea.value.style.height = 'auto';
    aiTextarea.value.style.height = Math.min(aiTextarea.value.scrollHeight, 120) + 'px';
  }
};

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

// 重置表单为创建模式
const resetForm = () => {
  form.title = '';
  form.date = formatDateForInput(props.initialDate);
  form.isAllDay = false;
  form.startTime = '09:00';
  form.endTime = '10:00';
  form.location = '';
  form.links = [];
  form.typeId = props.calendarTypes[0]?.id || 'general';
  form.attachment = null;
  newLink.value = '';
  if (fileInput.value) {
    fileInput.value.value = '';
  }
};

// If editing, populate form; otherwise reset
watch(() => props.editTask, (task) => {
  // 清除file input的值，确保可以重新选择相同文件
  if (fileInput.value) {
    fileInput.value.value = '';
  }
  
  if (task) {
    // 编辑模式：填充表单数据
    form.title = task.title || '';
    form.date = task.date || formatDateForInput(props.initialDate);
    form.isAllDay = task.isAllDay !== undefined ? task.isAllDay : false;
    form.startTime = task.startTime || '09:00';
    form.endTime = task.endTime || '10:00';
    form.location = task.location || '';
    // 深拷贝links数组，确保可以独立编辑
    form.links = task.links ? JSON.parse(JSON.stringify(task.links)) : [];
    form.typeId = task.typeId || 'general';
    // 深拷贝attachment，保留id和name用于后端识别和前端显示
    form.attachment = task.attachment ? { ...task.attachment } : null;
  } else {
    // 创建模式：重置表单
    resetForm();
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
    // 如果已有附件（有id），先标记为待删除
    const oldAttachmentId = form.attachment?.id;
    
    form.attachment = {
      name: file.name,
      file: file,
      url: URL.createObjectURL(file),
      // 保存旧附件ID用于删除
      replaceOldId: oldAttachmentId || null
    };
  }
};

const clearFile = () => {
  // 标记为删除（如果是已有附件）
  if (form.attachment && form.attachment.id) {
    form.attachment = { id: form.attachment.id, deleted: true };
  } else {
    form.attachment = null;
  }
  // 清除文件输入
  if (fileInput.value) {
    fileInput.value.value = '';
  }
};

// 检查是否有有效的附件显示
const hasValidAttachment = computed(() => {
  return form.attachment && !form.attachment.deleted;
});

const addLink = () => {
  if (!newLink.value.trim()) return;
  if (!form.links) form.links = [];
  form.links.push(newLink.value.trim());
  newLink.value = '';
};

const removeLink = (index) => {
  form.links.splice(index, 1);
};

const handleAISubmit = async () => {
  if (!aiInput.value.trim() || isLoading.value) return;
  
  isLoading.value = true;
  try {
    // 优先调用本地 agent_service（两阶段解析已封装，返回 parsed）
    const AGENT_SERVICE_BASE = import.meta.env.VITE_AGENT_SERVICE_BASE || 'http://localhost:8001';
    const resp = await fetch(`${AGENT_SERVICE_BASE}/parse-event`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_input: aiInput.value.trim() })
    });
    if (!resp.ok) throw new Error(`agent_service ${resp.status}`);
    const res = await resp.json();
    const parsed = res.parsed || (res.data && res.data.parsed);

    if (parsed) {
      if (parsed.title) form.title = parsed.title;
      if (parsed.date) form.date = parsed.date;
      if (parsed.is_all_day !== undefined) form.isAllDay = parsed.is_all_day;
      if (parsed.start_time) form.startTime = parsed.start_time;
      if (parsed.end_time) form.endTime = parsed.end_time;
      if (parsed.location) form.location = parsed.location;
      if (parsed.type_id) {
        const typeExists = props.calendarTypes.some(t => t.id === parsed.type_id);
        if (typeExists) form.typeId = parsed.type_id;
      }
      aiInput.value = '';
      if (aiTextarea.value) aiTextarea.value.style.height = 'auto';
    }
  } catch (err) {
    console.error('AI parse failed:', err);
  } finally {
    isLoading.value = false;
  }
};

const handleSave = () => {
  if (!form.title.trim()) return;
  
  // 处理附件：如果被标记为删除，传 null；否则传实际值
  let attachmentToSave = null;
  let attachmentToDelete = null;
  
  if (form.attachment) {
    if (form.attachment.deleted) {
      // 用户点击了清除按钮
      attachmentToDelete = form.attachment.id;
    } else if (form.attachment.file) {
      // 有新文件要上传
      attachmentToSave = form.attachment;
      // 如果是替换旧附件，标记旧附件待删除
      if (form.attachment.replaceOldId) {
        attachmentToDelete = form.attachment.replaceOldId;
      }
    } else if (form.attachment.id) {
      // 保留原有附件
      attachmentToSave = form.attachment;
    }
  }
  
  emit('save', {
    id: props.editTask?.id,
    title: form.title.trim(),
    date: form.date,
    isAllDay: form.isAllDay,
    startTime: form.isAllDay ? null : form.startTime,
    endTime: form.isAllDay ? null : form.endTime,
    location: form.location,
    links: [...form.links], // 确保传递副本
    typeId: form.typeId,
    attachment: attachmentToSave,
    // 需要删除的附件ID
    deleteAttachment: attachmentToDelete
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
  align-items: flex-start;
  gap: 10px;
  border: 2px solid #6366F1;
  border-radius: 16px;
  padding: 12px 16px;
  margin-bottom: 24px;
  min-height: 44px;
}

.ai-input-row .ai-icon {
  margin-top: 2px;
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
  resize: none;
  min-height: 20px;
  max-height: 120px;
  line-height: 1.4;
  font-family: inherit;
  overflow-y: auto;
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
  margin-top: 2px;
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
  margin-top: 2px;
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

.loading-spinner-small {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
