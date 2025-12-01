<template>
  <div 
    class="task-item" 
    :class="{ 'expanded': task.expanded, 'completed': task.completed }"
    :style="{ '--task-color': task.color }"
    ref="taskRef"
  >
    <!-- Collapsed View -->
    <div class="task-row" @click="toggleExpand">
      <div class="color-strip" :style="{ backgroundColor: task.color }"></div>
      
      <div class="task-checkbox" @click.stop="toggleComplete">
        <div class="checkbox-box" :class="{ checked: task.completed }">
          <Check v-if="task.completed" :size="14" color="white" stroke-width="3" />
        </div>
      </div>
      
      <div class="task-info">
        <span class="task-time">{{ task.isAllDay ? 'All day' : timeRange }}</span>
        <span class="task-title" :class="{ 'line-through': task.completed }">{{ task.title }}</span>
        <span v-if="task.attachment" class="attachment-chip" @click.stop="openAttachment">
          <FileText :size="12" color="#DC2626" />
          {{ task.attachment.name }}
        </span>
      </div>
      
      <button class="expand-btn">
        <ChevronUp v-if="task.expanded" :size="20" />
        <ChevronDown v-else :size="20" />
      </button>
    </div>

    <!-- Expanded View -->
    <div v-if="task.expanded" class="task-details">
      <div class="detail-content">
        <div class="detail-title-row">
          <div class="color-strip-vertical" :style="{ backgroundColor: task.color }"></div>
          <div class="detail-info">
            <span class="detail-time">{{ task.isAllDay ? 'All day' : timeRange }}, {{ formattedDate }}</span>
            <h3 class="detail-title">{{ task.title }}</h3>
            <!-- Location -->
            <div v-if="task.location" class="location-row">
              <MapPin :size="14" />
              <span>{{ task.location }}</span>
            </div>
            <span v-if="task.attachment" class="attachment-chip large">
              <FileText :size="14" />
              {{ task.attachment.name }}
            </span>
          </div>
        </div>
        
        <!-- Links Section -->
        <div v-if="task.links && task.links.length > 0" class="links-section">
          <div v-for="(link, index) in task.links" :key="index" class="link-item">
            <Link :size="14" />
            <a :href="link" target="_blank">{{ link }}</a>
          </div>
        </div>
      </div>
      
      <div class="detail-actions">
        <button class="action-btn" @click.stop="showAddLink = true">
          <Link :size="16" />
          <span>Add link</span>
        </button>
        <button class="action-btn icon-only" @click.stop="$emit('edit', task)">
          <Edit :size="16" />
        </button>
        <button class="action-btn icon-only" @click.stop="shareTask">
          <Share2 :size="16" />
        </button>
        <button class="action-btn icon-only" @click.stop="$emit('delete', task.id)">
          <Trash2 :size="16" />
        </button>
        <button class="action-btn icon-only">
          <MoreVertical :size="16" />
        </button>
      </div>
      
      <!-- Add Link Dialog -->
      <div v-if="showAddLink" class="add-link-dialog">
        <input 
          v-model="newLink" 
          type="text" 
          placeholder="Enter URL..."
          @keyup.enter="addLink"
        />
        <button class="link-submit" @click="addLink">Add</button>
        <button class="link-cancel" @click="showAddLink = false">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { format } from 'date-fns';
import { Check, ChevronDown, ChevronUp, FileText, Link, Edit, Share2, Trash2, MoreVertical, MapPin } from 'lucide-vue-next';
import html2canvas from 'html2canvas';

const props = defineProps({
  task: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['update', 'delete', 'edit']);

const taskRef = ref(null);
const showAddLink = ref(false);
const newLink = ref('');

const timeRange = computed(() => {
  if (props.task.isAllDay) return 'All day';
  const start = props.task.startTime || '00:00';
  const end = props.task.endTime || '00:00';
  const formatTime = (t) => {
    const [h, m] = t.split(':');
    const hour = parseInt(h);
    const suffix = hour >= 12 ? 'PM' : 'AM';
    const hour12 = hour % 12 || 12;
    return `${hour12}${m !== '00' ? ':' + m : ''}${suffix}`;
  };
  return `${formatTime(start)} to ${formatTime(end)}`;
});

const formattedDate = computed(() => {
  try {
    const date = new Date(props.task.date);
    return format(date, 'EEEE, MMMM d');
  } catch {
    return '';
  }
});

const toggleExpand = () => {
  emit('update', { ...props.task, expanded: !props.task.expanded });
};

const toggleComplete = () => {
  emit('update', { ...props.task, completed: !props.task.completed });
};

const openAttachment = () => {
  if (props.task.attachment?.url) {
    window.open(props.task.attachment.url, '_blank');
  }
};

const addLink = () => {
  if (!newLink.value.trim()) return;
  const links = props.task.links || [];
  emit('update', { ...props.task, links: [...links, newLink.value.trim()] });
  newLink.value = '';
  showAddLink.value = false;
};

const shareTask = async () => {
  if (!taskRef.value) return;
  
  try {
    const canvas = await html2canvas(taskRef.value, {
      backgroundColor: '#ffffff',
      scale: 2
    });
    
    canvas.toBlob((blob) => {
      if (blob) {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `task-${props.task.id}.png`;
        a.click();
        URL.revokeObjectURL(url);
      }
    });
  } catch (err) {
    console.error('Screenshot failed:', err);
    alert('截图功能暂时不可用');
  }
};
</script>

<style scoped>
.task-item {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  transition: all 0.2s;
}

.task-item:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.task-row {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  gap: 12px;
  cursor: pointer;
  position: relative;
}

.color-strip {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
}

.task-checkbox {
  margin-left: 8px;
}

.checkbox-box {
  width: 20px;
  height: 20px;
  border: 2px solid var(--task-color);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.checkbox-box.checked {
  background-color: var(--task-color);
}

.task-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
}

.task-time {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
  min-width: 80px;
}

.task-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-title.line-through {
  text-decoration: line-through;
  color: var(--text-secondary);
}

.attachment-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background-color: #FEF2F2;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  color: var(--text-primary);
  border: 1px dashed #FECACA;
  cursor: pointer;
  white-space: nowrap;
}

.attachment-chip.large {
  padding: 6px 12px;
  font-size: 13px;
  background-color: #FEF3C7;
  border-color: #FDE68A;
}

.expand-btn {
  color: var(--text-secondary);
  padding: 4px;
}

/* Expanded Details */
.task-details {
  border-top: 1px solid #F3F4F6;
  background-color: #FFFBEB;
  padding: 16px;
}

.detail-content {
  margin-bottom: 16px;
}

.detail-title-row {
  display: flex;
  gap: 12px;
}

.color-strip-vertical {
  width: 4px;
  border-radius: 2px;
  align-self: stretch;
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.detail-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.location-row {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--text-secondary);
  font-size: 13px;
  margin-top: 4px;
}

.links-section {
  margin-top: 12px;
  padding-left: 16px;
}

.link-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #3B82F6;
  margin-bottom: 4px;
}

.link-item a {
  color: inherit;
  text-decoration: none;
}

.link-item a:hover {
  text-decoration: underline;
}

.detail-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  border-top: 1px solid rgba(0,0,0,0.05);
  padding-top: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border-radius: 20px;
  font-size: 13px;
  color: var(--text-primary);
  background: white;
  border: 1px solid #E5E7EB;
  cursor: pointer;
  transition: all 0.15s;
}

.action-btn:hover {
  background-color: #F9FAFB;
}

.action-btn.icon-only {
  padding: 8px;
  border: none;
  background: transparent;
}

.action-btn.icon-only:hover {
  background-color: rgba(0,0,0,0.05);
}

/* Add Link Dialog */
.add-link-dialog {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid rgba(0,0,0,0.05);
}

.add-link-dialog input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  font-size: 13px;
  outline: none;
}

.add-link-dialog input:focus {
  border-color: #6366F1;
}

.link-submit, .link-cancel {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
}

.link-submit {
  background-color: #6366F1;
  color: white;
  border: none;
}

.link-cancel {
  background: white;
  border: 1px solid #E5E7EB;
  color: var(--text-secondary);
}
</style>
