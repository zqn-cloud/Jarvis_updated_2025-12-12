import { ref, computed } from 'vue';
import { startOfMonth, endOfMonth, startOfWeek, endOfWeek, eachDayOfInterval, addMonths, subMonths, isSameMonth, isSameDay, isToday } from 'date-fns';

export function useCalendar() {
  const currentDate = ref(new Date());
  const selectedDate = ref(new Date());

  const calendarDays = computed(() => {
    const start = startOfWeek(startOfMonth(currentDate.value));
    const end = endOfWeek(endOfMonth(currentDate.value));
    return eachDayOfInterval({ start, end });
  });

  const nextMonth = () => {
    currentDate.value = addMonths(currentDate.value, 1);
  };

  const prevMonth = () => {
    currentDate.value = subMonths(currentDate.value, 1);
  };

  const selectDate = (date) => {
    selectedDate.value = date;
  };

  const checkIsSameMonth = (date) => isSameMonth(date, currentDate.value);
  const checkIsToday = (date) => isToday(date);
  const checkIsSelected = (date) => isSameDay(date, selectedDate.value);

  return {
    currentDate,
    selectedDate,
    calendarDays,
    nextMonth,
    prevMonth,
    selectDate,
    checkIsSameMonth,
    checkIsToday,
    checkIsSelected
  };
}

