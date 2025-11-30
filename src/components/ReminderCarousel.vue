<template>
  <div class="reminder-carousel">
    <div class="carousel-header">
      <Sparkles :size="16" />
      <span>Reminder</span>
    </div>
    
    <div class="carousel-wrapper">
      <div 
        class="carousel-track" 
        :style="{ transform: `translateX(-${currentIndex * 100}%)` }"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
      >
        <div 
          v-for="reminder in reminders" 
          :key="reminder.id" 
          class="carousel-slide"
        >
          <div class="reminder-card" :style="{ backgroundColor: reminder.bgColor }">
            <div class="card-icon" :style="{ backgroundColor: reminder.iconBg }">
              <Cloud v-if="reminder.type === 'weather'" :size="24" color="white" />
              <Navigation v-else-if="reminder.type === 'commute'" :size="24" color="white" />
              <CalendarHeart v-else :size="24" color="white" />
            </div>
            <div class="card-content">
              <h4 class="card-title">{{ reminder.title }}</h4>
              <p class="card-subtitle">{{ reminder.subtitle }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="carousel-dots">
      <button 
        v-for="(_, index) in reminders" 
        :key="index"
        class="dot"
        :class="{ active: index === currentIndex }"
        @click="currentIndex = index"
      ></button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { Sparkles, Cloud, Navigation, CalendarHeart } from 'lucide-vue-next';

const props = defineProps({
  reminders: {
    type: Array,
    default: () => []
  }
});

const currentIndex = ref(0);
let autoPlayTimer = null;
let touchStartX = 0;

const startAutoPlay = () => {
  if (props.reminders.length <= 1) return;
  autoPlayTimer = setInterval(() => {
    currentIndex.value = (currentIndex.value + 1) % props.reminders.length;
  }, 5000);
};

const stopAutoPlay = () => {
  if (autoPlayTimer) {
    clearInterval(autoPlayTimer);
    autoPlayTimer = null;
  }
};

const handleTouchStart = (e) => {
  touchStartX = e.touches[0].clientX;
  stopAutoPlay();
};

const handleTouchMove = () => {};

const handleTouchEnd = (e) => {
  const touchEndX = e.changedTouches[0].clientX;
  const diff = touchStartX - touchEndX;
  
  if (Math.abs(diff) > 50) {
    if (diff > 0 && currentIndex.value < props.reminders.length - 1) {
      currentIndex.value++;
    } else if (diff < 0 && currentIndex.value > 0) {
      currentIndex.value--;
    }
  }
  startAutoPlay();
};

onMounted(startAutoPlay);
onUnmounted(stopAutoPlay);
</script>

<style scoped>
.reminder-carousel {
  width: 100%;
}

.carousel-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
}

.carousel-wrapper {
  overflow: hidden;
  border-radius: 16px;
}

.carousel-track {
  display: flex;
  transition: transform 0.4s ease;
}

.carousel-slide {
  min-width: 100%;
  flex-shrink: 0;
}

.reminder-card {
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  border-radius: 16px;
  min-height: 100px;
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-content {
  flex: 1;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 4px 0;
}

.card-subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.4;
}

.carousel-dots {
  display: flex;
  justify-content: center;
  gap: 6px;
  margin-top: 12px;
}

.dot {
  width: 24px;
  height: 6px;
  border-radius: 3px;
  background-color: #E5E7EB;
  padding: 0;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.dot.active {
  background-color: #9CA3AF;
}
</style>
