<template>
  <div class="category-filter">
    <div class="section-header" @click="isCollapsed = !isCollapsed">
      <button class="collapse-btn">
        <ChevronDown v-if="!isCollapsed" :size="16" />
        <ChevronRight v-else :size="16" />
      </button>
      <Calendar :size="16" />
      <span class="section-title">My calendars</span>
    </div>
    
    <div v-show="!isCollapsed" class="filter-list">
      <div v-for="cat in categories" :key="cat.id" class="filter-item">
        <label class="checkbox-label">
          <div class="checkbox-wrapper">
            <input 
              type="checkbox" 
              :checked="cat.visible"
              @change="$emit('toggle', cat.id)"
            >
            <span 
              class="custom-checkbox" 
              :style="{ 
                backgroundColor: cat.visible ? cat.color : 'transparent',
                borderColor: cat.color 
              }"
            >
              <Check v-if="cat.visible" :size="12" color="white" stroke-width="3" />
            </span>
          </div>
          <span class="label-text">{{ cat.name }}</span>
        </label>
        <button 
          v-if="cat.id !== 'general'" 
          class="delete-btn"
          @click.stop="$emit('delete-type', cat.id)"
        >
          <X :size="14" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { Check, ChevronDown, ChevronRight, Calendar, X } from 'lucide-vue-next';

defineProps({
  categories: {
    type: Array,
    default: () => []
  }
});

defineEmits(['toggle', 'delete-type']);

const isCollapsed = ref(false);
</script>

<style scoped>
.category-filter {
  margin-top: 8px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  user-select: none;
}

.section-header:hover {
  color: var(--text-primary);
}

.collapse-btn {
  padding: 2px;
  color: inherit;
}

.section-title {
  font-size: 14px;
  font-weight: 500;
}

.filter-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-left: 24px;
}

.filter-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  flex: 1;
}

.checkbox-wrapper {
  position: relative;
}

.checkbox-wrapper input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
}

.custom-checkbox {
  width: 18px;
  height: 18px;
  border: 2px solid;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.15s;
}

.label-text {
  font-size: 14px;
  color: var(--text-primary);
}

.delete-btn {
  padding: 4px;
  color: var(--text-secondary);
  opacity: 0;
  transition: opacity 0.2s;
}

.filter-item:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  color: #EF4444;
}
</style>
