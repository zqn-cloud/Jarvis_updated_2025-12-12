<template>
  <main class="main-content">
    <header class="top-bar">
      <!-- Date Navigation Placeholder -->
      <div class="date-nav-container">
        <slot name="date-nav"></slot>
      </div>
      
      <div class="top-actions">
        <div class="icon-btn"><Search :size="20" /></div>
        <div class="icon-btn"><Settings :size="20" /></div>
        <div class="icon-btn"><Grid :size="20" /></div>
        <div class="avatar">
          <img src="https://i.pravatar.cc/150?img=32" alt="User" />
        </div>
      </div>
    </header>

    <div class="workspace-scroll-area">
      <!-- Reminder Carousel Placeholder -->
      <section class="reminders-section">
        <slot name="reminders"></slot>
      </section>

      <!-- Task List Placeholder -->
      <section class="tasks-section">
        <slot name="tasks"></slot>
      </section>

      <!-- AI Input Placeholder -->
      <section class="ai-input-section">
        <slot name="ai-input"></slot>
      </section>
    </div>
  </main>
</template>

<script setup>
import { Search, Settings, Grid } from 'lucide-vue-next';
</script>

<style scoped>
.main-content {
  flex: 1;
  height: 100%;
  background-color: var(--bg-color); /* Or slightly different shade if needed */
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-top-left-radius: 24px; /* As per design curvature */
  border-bottom-left-radius: 24px;
  background: #E5E7EB; /* Darker gray border simulation */
  padding: 8px 0 8px 8px; /* Gap for border effect */
}

.workspace-scroll-area {
  background: #F3F4F6; /* Light gray background for main area */
  border-radius: 16px 0 0 16px; /* Rounded corners */
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 24px;
  background-color: var(--bg-color);
}

/* Fix the Main Content wrapper to match design clean look */
.main-content {
  background: transparent;
  padding: 0;
  border-radius: 0;
}

.workspace-scroll-area {
  border-radius: 24px 0 0 24px;
  background-color: #E5E6EB; /* slightly darker than white */
  padding: 0;
  position: relative;
}

/* The actual white/card area is likely inside components, but the main background is gray */

.top-bar {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  margin-bottom: 16px;
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-primary);
  cursor: pointer;
}

.icon-btn:hover {
  background-color: rgba(0,0,0,0.05);
}

.avatar img {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  object-fit: cover;
}
</style>

