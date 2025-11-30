<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <div class="brand">
        <div class="logo">
          <span>31</span>
        </div>
        <span class="brand-name">Jarvis</span>
      </div>
    </div>

    <div class="sidebar-content">
      <slot name="mini-calendar"></slot>
      <slot name="create-button"></slot>
      <slot name="category-filter"></slot>
    </div>
  </aside>
</template>

<script setup>
</script>

<style scoped>
.sidebar {
  width: 300px;
  height: 100%;
  background-color: #F8F9FA;
  display: flex;
  flex-direction: column;
  padding: 16px 20px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  margin-bottom: 24px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo {
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #4285F4 0%, #34A853 50%, #FBBC05 75%, #EA4335 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo span {
  background: white;
  color: #4285F4;
  font-weight: 700;
  font-size: 14px;
  padding: 2px 5px;
  border-radius: 3px;
}

.brand-name {
  font-size: 22px;
  font-weight: 500;
  color: var(--text-primary);
}

.sidebar-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}
</style>
