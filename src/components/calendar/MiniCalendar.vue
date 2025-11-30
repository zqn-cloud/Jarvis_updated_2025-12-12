<template>
  <div class="mini-calendar">
    <div class="calendar-header">
      <span class="month-year">{{ monthYearText }}</span>
      <div class="nav-buttons">
        <button class="nav-btn" @click="prevMonth">
          <ChevronUp :size="18" />
        </button>
        <button class="nav-btn" @click="nextMonth">
          <ChevronDown :size="18" />
        </button>
      </div>
    </div>
    
    <div class="calendar-grid">
      <div v-for="day in weekDays" :key="day" class="weekday-label">{{ day }}</div>
      <div 
        v-for="(day, index) in calendarDays" 
        :key="index"
        class="day-cell"
        :class="{ 
          'other-month': !day.isCurrentMonth,
          'today': day.isToday,
          'selected': day.isSelected
        }"
        @click="onSelectDate(day.date)"
      >
        {{ day.dayNumber }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { 
  format, 
  startOfMonth, 
  endOfMonth, 
  startOfWeek, 
  endOfWeek, 
  eachDayOfInterval, 
  isSameMonth, 
  isSameDay, 
  addMonths, 
  subMonths,
  getDate 
} from 'date-fns';
import { ChevronUp, ChevronDown } from 'lucide-vue-next';

const props = defineProps({
  selectedDate: {
    type: Date,
    default: () => new Date()
  }
});

const emit = defineEmits(['select-date']);

const weekDays = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
const viewDate = ref(new Date(props.selectedDate));
const today = new Date();

// Watch for external selectedDate changes
watch(() => props.selectedDate, (newVal) => {
  viewDate.value = new Date(newVal);
});

const monthYearText = computed(() => format(viewDate.value, 'MMMM yyyy'));

const calendarDays = computed(() => {
  const monthStart = startOfMonth(viewDate.value);
  const monthEnd = endOfMonth(viewDate.value);
  const calendarStart = startOfWeek(monthStart, { weekStartsOn: 0 });
  const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 0 });
  
  const days = eachDayOfInterval({ start: calendarStart, end: calendarEnd });
  
  return days.map(date => ({
    date,
    dayNumber: getDate(date),
    isCurrentMonth: isSameMonth(date, viewDate.value),
    isToday: isSameDay(date, today),
    isSelected: isSameDay(date, props.selectedDate)
  }));
});

const prevMonth = () => {
  viewDate.value = subMonths(viewDate.value, 1);
};

const nextMonth = () => {
  viewDate.value = addMonths(viewDate.value, 1);
};

const onSelectDate = (date) => {
  emit('select-date', date);
};
</script>

<style scoped>
.mini-calendar {
  width: 100%;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.month-year {
  font-weight: 500;
  font-size: 14px;
  color: var(--text-primary);
}

.nav-buttons {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.nav-btn {
  padding: 2px;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-btn:hover {
  color: var(--text-primary);
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  text-align: center;
}

.weekday-label {
  font-size: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  padding: 4px 0;
}

.day-cell {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  border-radius: 50%;
  cursor: pointer;
  color: var(--text-primary);
  margin: 0 auto;
}

.day-cell.other-month {
  color: #D1D5DB;
}

.day-cell:hover:not(.today):not(.selected) {
  background-color: #F3F4F6;
}

.day-cell.today {
  background-color: #6366F1;
  color: white;
  font-weight: 600;
}

.day-cell.selected:not(.today) {
  background-color: #1F2937;
  color: white;
  font-weight: 600;
  border-radius: 8px;
}
</style>
