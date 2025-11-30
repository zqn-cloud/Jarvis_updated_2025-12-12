<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <!-- AI Input -->
      <div class="ai-input-row">
        <Sparkles :size="16" class="ai-icon" />
        <input 
          v-model="aiInput"
          type="text" 
          placeholder="Describe the calendar type..." 
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

const emit = defineEmits(['close', 'save', 'ai-submit']);

const typeName = ref('');
const aiInput = ref('');
const showDropdown = ref(false);

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

const handleAISubmit = () => {
  if (!aiInput.value.trim()) return;
  // TODO: Call AI API to parse and fill form
  emit('ai-submit', aiInput.value.trim());
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
  align-items: center;
  gap: 10px;
  border: 1px solid #E5E7EB;
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
</style>
