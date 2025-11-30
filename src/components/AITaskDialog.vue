<template>
  <div class="ai-task-dialog">
    <button class="trigger-btn" @click="isExpanded = !isExpanded">
      <span class="ai-label">AI</span>
      <Sparkles :size="16" />
      <span>Add a Task for Today</span>
    </button>
    
    <div v-if="isExpanded" class="input-panel">
      <input 
        v-model="inputText"
        type="text" 
        placeholder="Type/Speak anything you should do today...."
        @keyup.enter="handleSubmit"
      />
      <div class="input-actions">
        <button class="mic-btn" @click="toggleRecording" :class="{ recording: isRecording }">
          <Mic :size="18" />
        </button>
        <button class="send-btn" @click="handleSubmit" :disabled="!inputText.trim()">
          <ArrowUp :size="18" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Sparkles, Mic, ArrowUp } from 'lucide-vue-next';

const emit = defineEmits(['submit']);

const isExpanded = ref(false);
const inputText = ref('');
const isRecording = ref(false);

const toggleRecording = () => {
  isRecording.value = !isRecording.value;
};

const handleSubmit = () => {
  if (!inputText.value.trim()) return;
  emit('submit', inputText.value.trim());
  inputText.value = '';
  isExpanded.value = false;
};
</script>

<style scoped>
.ai-task-dialog {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.trigger-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background-color: #FEF3C7;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  color: #1F2937;
  cursor: pointer;
  width: fit-content;
  transition: all 0.2s;
}

.trigger-btn:hover {
  background-color: #FDE68A;
}

.ai-label {
  font-weight: 700;
  font-size: 12px;
}

.input-panel {
  display: flex;
  align-items: center;
  gap: 12px;
  background: #FFFBEB;
  border-radius: 12px;
  padding: 12px 16px;
  width: 100%;
  max-width: 500px;
}

.input-panel input {
  flex: 1;
  border: none;
  background: transparent;
  outline: none;
  font-size: 14px;
  color: var(--text-primary);
}

.input-panel input::placeholder {
  color: #9CA3AF;
}

.input-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mic-btn, .send-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.mic-btn {
  color: var(--text-secondary);
  background: transparent;
}

.mic-btn:hover {
  background-color: rgba(0,0,0,0.05);
}

.mic-btn.recording {
  color: #EF4444;
  background-color: #FEE2E2;
}

.send-btn {
  background-color: #1F2937;
  color: white;
}

.send-btn:hover:not(:disabled) {
  background-color: #374151;
}

.send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
</style>
