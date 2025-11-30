<template>
  <div class="date-navigation">
    <button class="today-btn" @click="goToday">
      <CalendarIcon :size="16" />
      <span>Today</span>
    </button>
    
    <h1 class="current-date">{{ formattedDate }}</h1>
    
    <div class="nav-arrows">
      <button class="nav-btn" @click="prevDay">
        <ChevronLeft :size="20" />
      </button>
      <button class="nav-btn" @click="nextDay">
        <ChevronRight :size="20" />
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { format, addDays, subDays } from 'date-fns';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight } from 'lucide-vue-next';

const props = defineProps({
  date: {
    type: Date,
    default: () => new Date()
  }
});

const emit = defineEmits(['update:date']);

const formattedDate = computed(() => {
  return format(props.date, "d, MMMM, yyyy");
});

const goToday = () => {
  emit('update:date', new Date());
};

const prevDay = () => {
  emit('update:date', subDays(props.date, 1));
};

const nextDay = () => {
  emit('update:date', addDays(props.date, 1));
};
</script>

<style scoped>
.date-navigation {
  display: flex;
  align-items: center;
  gap: 20px;
}

.today-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.2s;
}

.today-btn:hover {
  background-color: #F9FAFB;
}

.current-date {
  font-size: 22px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0;
}

.nav-arrows {
  display: flex;
  gap: 4px;
}

.nav-btn {
  padding: 6px;
  color: var(--text-secondary);
  border-radius: 50%;
}

.nav-btn:hover {
  background-color: rgba(0,0,0,0.05);
  color: var(--text-primary);
}
</style>
