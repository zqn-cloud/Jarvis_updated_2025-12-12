<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <div class="modal-header">
        <h2>Settings</h2>
        <button class="close-btn" @click="$emit('close')">
          <X :size="20" />
        </button>
      </div>

      <div class="settings-content">
        <!-- Profile Section -->
        <section class="settings-section">
          <h3 class="section-title">Profile</h3>
          <div class="profile-card">
            <div class="avatar-wrapper">
              <img :src="settings.avatar" alt="User Avatar" class="avatar" />
              <button class="change-avatar">
                <Camera :size="14" />
              </button>
            </div>
            <div class="profile-info">
              <input 
                type="text" 
                v-model="settings.name" 
                class="name-input"
                placeholder="Your Name"
              />
              <input 
                type="email" 
                v-model="settings.email" 
                class="email-input"
                placeholder="your@email.com"
              />
            </div>
          </div>
        </section>

        <!-- Preferences Section -->
        <section class="settings-section">
          <h3 class="section-title">Preferences</h3>
          
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">Language</span>
              <span class="setting-desc">Choose your preferred language</span>
            </div>
            <select v-model="settings.language" class="setting-select">
              <option value="en">English</option>
              <option value="zh">中文</option>
              <option value="ja">日本語</option>
            </select>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">Time Format</span>
              <span class="setting-desc">12-hour or 24-hour format</span>
            </div>
            <select v-model="settings.timeFormat" class="setting-select">
              <option value="12h">12-hour</option>
              <option value="24h">24-hour</option>
            </select>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">Week Starts On</span>
              <span class="setting-desc">First day of the week</span>
            </div>
            <select v-model="settings.weekStart" class="setting-select">
              <option value="sunday">Sunday</option>
              <option value="monday">Monday</option>
            </select>
          </div>
        </section>

        <!-- Notifications Section -->
        <section class="settings-section">
          <h3 class="section-title">Notifications</h3>
          
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">Push Notifications</span>
              <span class="setting-desc">Receive reminders for events</span>
            </div>
            <button 
              class="toggle-switch" 
              :class="{ active: settings.pushNotifications }"
              @click="settings.pushNotifications = !settings.pushNotifications"
            >
              <span class="toggle-knob"></span>
            </button>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">Email Notifications</span>
              <span class="setting-desc">Daily summary of your schedule</span>
            </div>
            <button 
              class="toggle-switch" 
              :class="{ active: settings.emailNotifications }"
              @click="settings.emailNotifications = !settings.emailNotifications"
            >
              <span class="toggle-knob"></span>
            </button>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">Reminder Time</span>
              <span class="setting-desc">Default time before events</span>
            </div>
            <select v-model="settings.reminderTime" class="setting-select">
              <option value="5">5 minutes</option>
              <option value="10">10 minutes</option>
              <option value="15">15 minutes</option>
              <option value="30">30 minutes</option>
              <option value="60">1 hour</option>
            </select>
          </div>
        </section>

        <!-- AI Settings Section -->
        <section class="settings-section">
          <h3 class="section-title">AI Assistant</h3>
          
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">AI Suggestions</span>
              <span class="setting-desc">Get smart scheduling suggestions</span>
            </div>
            <button 
              class="toggle-switch" 
              :class="{ active: settings.aiSuggestions }"
              @click="settings.aiSuggestions = !settings.aiSuggestions"
            >
              <span class="toggle-knob"></span>
            </button>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">Voice Input</span>
              <span class="setting-desc">Enable voice commands</span>
            </div>
            <button 
              class="toggle-switch" 
              :class="{ active: settings.voiceInput }"
              @click="settings.voiceInput = !settings.voiceInput"
            >
              <span class="toggle-knob"></span>
            </button>
          </div>
        </section>

        <!-- Danger Zone -->
        <section class="settings-section danger-zone">
          <h3 class="section-title">Danger Zone</h3>
          
          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">Clear All Data</span>
              <span class="setting-desc">Delete all events and settings</span>
            </div>
            <button class="danger-btn">Clear</button>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <span class="setting-label">Delete Account</span>
              <span class="setting-desc">Permanently delete your account</span>
            </div>
            <button class="danger-btn">Delete</button>
          </div>
        </section>
      </div>

      <div class="modal-footer">
        <button class="cancel-btn" @click="$emit('close')">Cancel</button>
        <button class="save-btn" @click="handleSave">Save Changes</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { X, Camera } from 'lucide-vue-next';

const emit = defineEmits(['close', 'save']);

const settings = reactive({
  name: 'User Name',
  email: 'user@example.com',
  avatar: 'https://i.pravatar.cc/150?img=32',
  language: 'en',
  timeFormat: '12h',
  weekStart: 'sunday',
  pushNotifications: true,
  emailNotifications: false,
  reminderTime: '15',
  aiSuggestions: true,
  voiceInput: true
});

const handleSave = () => {
  emit('save', { ...settings });
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
  width: 500px;
  max-height: 85vh;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #E5E7EB;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  color: var(--text-secondary);
  padding: 4px;
}

.close-btn:hover {
  color: var(--text-primary);
}

.settings-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
}

.settings-section {
  margin-bottom: 28px;
}

.settings-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 16px;
}

/* Profile Card */
.profile-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #F9FAFB;
  border-radius: 12px;
}

.avatar-wrapper {
  position: relative;
}

.avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  object-fit: cover;
}

.change-avatar {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 24px;
  height: 24px;
  background: #6366F1;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.name-input, .email-input {
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  padding: 8px 12px;
  font-size: 14px;
  outline: none;
}

.name-input {
  font-weight: 500;
}

.email-input {
  color: var(--text-secondary);
}

.name-input:focus, .email-input:focus {
  border-color: #6366F1;
}

/* Setting Item */
.setting-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #F3F4F6;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.setting-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.setting-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.setting-select {
  padding: 8px 12px;
  border: 1px solid #E5E7EB;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  cursor: pointer;
  background: white;
}

.setting-select:focus {
  border-color: #6366F1;
}

/* Toggle Switch */
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

/* Danger Zone */
.danger-zone .section-title {
  color: #EF4444;
}

.danger-btn {
  padding: 8px 16px;
  background: #FEE2E2;
  color: #EF4444;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
}

.danger-btn:hover {
  background: #FECACA;
}

/* Footer */
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #E5E7EB;
}

.cancel-btn {
  padding: 10px 20px;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
}

.cancel-btn:hover {
  background: #F9FAFB;
}

.save-btn {
  padding: 10px 20px;
  background: #6366F1;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.save-btn:hover {
  background: #4F46E5;
}
</style>
