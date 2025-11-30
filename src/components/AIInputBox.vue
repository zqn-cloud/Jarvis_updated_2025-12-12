<template>
  <div class="ai-input-box">
    <div class="input-wrapper">
      <div class="ai-icon">
        <Sparkles :size="18" />
      </div>
      <input 
        v-model="inputValue" 
        type="text" 
        placeholder="Type/Speak anything you should do today...." 
        @keyup.enter="sendMessage"
      />
      <button class="mic-btn" @click="toggleRecording" :class="{ 'recording': isRecording }">
        <Mic v-if="!isRecording" :size="20" />
        <div v-else class="waveform">
           <div class="bar"></div>
           <div class="bar"></div>
           <div class="bar"></div>
           <div class="bar"></div>
        </div>
      </button>
      <button class="send-btn" @click="sendMessage" v-if="inputValue">
        <ArrowUp :size="18" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Sparkles, Mic, ArrowUp } from 'lucide-vue-next';

const inputValue = ref('');
const isRecording = ref(false);

const toggleRecording = () => {
  isRecording.value = !isRecording.value;
  if (isRecording.value) {
    // Simulate recording stop after 3s
    setTimeout(() => {
      isRecording.value = false;
      inputValue.value = "Buy milk on the way home";
    }, 3000);
  }
};

const sendMessage = () => {
  if (!inputValue.value) return;
  console.log('Sent AI command:', inputValue.value);
  // Emit or process
  inputValue.value = '';
};
</script>

<style scoped>
.ai-input-box {
  width: 100%;
  margin-top: auto; /* Push to bottom if in flex container, though it's sectioned in MainContent */
}

.input-wrapper {
  background: white;
  border-radius: 16px; /* Rounded pill shape */
  padding: 8px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid transparent;
  transition: all 0.2s;
  height: 64px;
}

.input-wrapper:focus-within {
  border-color: var(--primary-blue);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.15);
}

.ai-icon {
  color: var(--primary-blue); /* Sparkles color */
  display: flex;
  align-items: center;
  justify-content: center;
}

input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 16px;
  color: var(--text-primary);
}

input::placeholder {
  color: #9CA3AF;
}

.mic-btn, .send-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.mic-btn:hover, .send-btn:hover {
  background-color: #F3F4F6;
  color: var(--text-primary);
}

.send-btn {
  background-color: var(--text-primary);
  color: white !important;
}

.send-btn:hover {
  background-color: #1F2937;
  transform: scale(1.05);
}

/* Recording Animation */
.mic-btn.recording {
  color: #EF4444;
  background-color: #FEF2F2;
}

.waveform {
  display: flex;
  align-items: center;
  gap: 2px;
  height: 16px;
}

.bar {
  width: 3px;
  background-color: #EF4444;
  border-radius: 2px;
  animation: wave 0.5s ease-in-out infinite;
}

.bar:nth-child(1) { height: 6px; animation-delay: 0s; }
.bar:nth-child(2) { height: 12px; animation-delay: 0.1s; }
.bar:nth-child(3) { height: 8px; animation-delay: 0.2s; }
.bar:nth-child(4) { height: 10px; animation-delay: 0.3s; }

@keyframes wave {
  0%, 100% { transform: scaleY(1); }
  50% { transform: scaleY(1.5); }
}
</style>

