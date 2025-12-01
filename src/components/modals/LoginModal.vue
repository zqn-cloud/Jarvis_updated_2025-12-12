<template>
  <div class="login-screen">
    <div class="login-container">
      <div class="login-header">
        <div class="logo">
          <div class="logo-icon">
            <span>31</span>
          </div>
          <span class="logo-text">Jarvis</span>
        </div>
        <p class="subtitle">Sign in to your calendar</p>
      </div>

      <div class="login-form">
        <div class="form-group">
          <label for="accountId">Account ID</label>
          <input 
            id="accountId"
            type="text" 
            v-model="accountId" 
            class="form-input"
            placeholder="e.g. jarvis@cuhk.com"
            @keyup.enter="handleLogin"
            autofocus
          />
        </div>

        <button class="login-btn" @click="handleLogin" :disabled="!accountId.trim()">
          <LogIn :size="18" />
          <span>Sign In</span>
        </button>

        <p class="hint">Enter your account ID to access your calendar</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { LogIn } from 'lucide-vue-next';

const emit = defineEmits(['login']);

const accountId = ref('');

const handleLogin = () => {
  if (!accountId.value.trim()) return;
  emit('login', accountId.value.trim());
};
</script>

<style scoped>
.login-screen {
  position: fixed;
  inset: 0;
  background: linear-gradient(135deg, #E0E7FF 0%, #F3E8FF 50%, #FCE7F3 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.login-container {
  background: white;
  width: 400px;
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.12);
}

.login-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 16px;
}

.logo-icon {
  width: 52px;
  height: 52px;
  background: linear-gradient(135deg, #4285F4 0%, #34A853 50%, #FBBC05 75%, #EA4335 100%);
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon span {
  background: white;
  color: #4285F4;
  font-weight: 700;
  font-size: 18px;
  padding: 4px 7px;
  border-radius: 5px;
}

.logo-text {
  font-size: 32px;
  font-weight: 600;
  color: var(--text-primary);
}

.subtitle {
  color: var(--text-secondary);
  font-size: 15px;
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-input {
  border: 2px solid #E5E7EB;
  border-radius: 12px;
  padding: 14px 16px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.form-input:focus {
  border-color: #6366F1;
}

.form-input::placeholder {
  color: #9CA3AF;
}

.login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.login-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hint {
  text-align: center;
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}
</style>

