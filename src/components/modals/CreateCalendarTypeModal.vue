<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <!-- AI Input -->
      <div class="ai-input-row">
        <Sparkles :size="16" class="ai-icon" />
        <textarea 
          ref="aiTextarea"
          v-model="aiInput"
          placeholder="Describe the calendar type..." 
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
        <div class="form-group">
          <label>Type Name</label>
          <input 
            type="text" 
            v-model="typeName" 
            placeholder="e.g. Work, Fitness" 
            class="form-input"
          />
        </div>

        <div class="form-group">
          <label>Color</label>
          <div class="color-select" @click="showDropdown = !showDropdown">
            <div class="color-preview">
              <span class="color-dot" :style="{ backgroundColor: selectedColor.value }"></span>
              <span>{{ selectedColor.name }}</span>
            </div>
            <ChevronDown :size="16" />
          </div>
          
          <div v-if="showDropdown" class="dropdown">
            <div 
              v-for="color in colorOptions" 
              :key="color.name" 
              class="dropdown-item"
              @click="selectColor(color)"
            >
              <span class="color-dot" :style="{ backgroundColor: color.value }"></span>
              <span>{{ color.name }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Save Button -->
      <button class="save-btn" @click="handleSave" :disabled="!typeName.trim()">
        Save
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { X, Sparkles, ChevronDown, Send } from 'lucide-vue-next';
import { agentAPI } from '../../services/api.js';

const emit = defineEmits(['close', 'save', 'ai-submit']);

const aiTextarea = ref(null);
const typeName = ref('');
const aiInput = ref('');
const showDropdown = ref(false);
const isLoading = ref(false);

// 自动调整textarea高度
const autoResizeTextarea = () => {
  if (aiTextarea.value) {
    aiTextarea.value.style.height = 'auto';
    aiTextarea.value.style.height = Math.min(aiTextarea.value.scrollHeight, 120) + 'px';
  }
};

const colorOptions = [
  { name: 'Amber', value: '#F59E0B' },
  { name: 'Pink', value: '#EC4899' },
  { name: 'Blue', value: '#3B82F6' },
  { name: 'Green', value: '#22C55E' },
  { name: 'Purple', value: '#A855F7' },
  { name: 'Red', value: '#EF4444' },
];

const selectedColor = ref(colorOptions[0]);

const selectColor = (color) => {
  selectedColor.value = color;
  showDropdown.value = false;
};

const handleAISubmit = async () => {
  if (!aiInput.value.trim() || isLoading.value) return;
  
  isLoading.value = true;
  try {
    // 优先调用本地 agent_service（两阶段逻辑已封装）
    const AGENT_SERVICE_BASE = import.meta.env.VITE_AGENT_SERVICE_BASE || 'http://localhost:8001';
    const resp = await fetch(`${AGENT_SERVICE_BASE}/parse-calendar-type`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_input: aiInput.value.trim() })
    });
    if (!resp.ok) throw new Error(`agent_service ${resp.status}`);
    const res = await resp.json();

    // agent_service 会直接返回后端 /agent/parse-calendar-type 的 data
    const parsed = res.parsed || (res.data && res.data.parsed);
    if (parsed) {
      if (parsed.name) typeName.value = parsed.name;
      if (parsed.color) {
        const matchedColor = colorOptions.find(c => c.value.toLowerCase() === parsed.color.toLowerCase());
        if (matchedColor) selectedColor.value = matchedColor;
      }
      // 清空AI输入并重置高度
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
  if (!typeName.value.trim()) return;
  emit('save', {
    name: typeName.value.trim(),
    color: selectedColor.value.value
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
  width: 380px;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.ai-input-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  border: 1px solid #E5E7EB;
  border-radius: 16px;
  padding: 12px 16px;
  margin-bottom: 24px;
  min-height: 44px;
}

.ai-icon {
  color: #6B7280;
  flex-shrink: 0;
  margin-top: 2px;
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
  gap: 20px;
  margin-bottom: 24px;
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

.color-select {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 12px 14px;
  cursor: pointer;
}

.color-preview {
  display: flex;
  align-items: center;
  gap: 10px;
}

.color-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

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
  max-height: 200px;
  overflow-y: auto;
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

.save-btn {
  width: 100%;
  background-color: #6366F1;
  color: white;
  padding: 12px;
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
