<template>
  <div class="create-wrapper" ref="wrapperRef">
    <button class="create-btn" @click="toggleMenu">
      <Plus :size="20" />
      <span>Create</span>
    </button>

    <div v-if="isOpen" class="popover-menu">
      <div class="menu-item" @click="handleAction('calendar-type')">
        <span class="item-text">Create Calendar Type</span>
      </div>
      <div class="menu-item" @click="handleAction('event')">
        <span class="item-text">Create Event</span>
      </div>
    </div>
    
    <!-- Overlay for background dimming -->
    <div v-if="isOpen" class="overlay" @click="closeMenu"></div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Plus } from 'lucide-vue-next';

const emit = defineEmits(['open-modal']);
const isOpen = ref(false);
const wrapperRef = ref(null);

const toggleMenu = () => {
  isOpen.value = !isOpen.value;
};

const closeMenu = () => {
  isOpen.value = false;
};

const handleAction = (type) => {
  if (type === 'calendar-type') {
    emit('open-modal', 'calendar-type');
  } else if (type === 'event') {
    emit('open-modal', 'event');
  }
  closeMenu();
};
</script>

<style scoped>
.create-wrapper {
  position: relative;
  z-index: 50; /* Higher than normal content */
}

.create-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: white;
  border: 1px solid var(--border-color);
  padding: 12px 24px;
  border-radius: 32px;
  font-weight: 600;
  color: var(--text-primary);
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  transition: all 0.2s;
  width: fit-content;
}

.create-btn:hover {
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transform: translateY(-1px);
}

.popover-menu {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
  min-width: 200px;
  padding: 8px;
  z-index: 101; /* Above overlay */
  animation: fadeIn 0.2s ease-out;
}

.menu-item {
  padding: 10px 16px;
  cursor: pointer;
  border-radius: 8px;
  transition: background-color 0.2s;
  color: var(--text-primary);
  font-size: 14px;
}

.menu-item:hover {
  background-color: #F3F4F6;
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.2); /* Dim background */
  z-index: 100;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>

