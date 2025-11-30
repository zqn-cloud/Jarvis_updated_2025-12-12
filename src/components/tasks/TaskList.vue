<template>
  <div class="task-list">
    <template v-if="tasks.length > 0">
      <TaskItem 
        v-for="task in tasks" 
        :key="task.id" 
        :task="task" 
        @update="handleUpdate"
        @delete="handleDelete"
        @edit="handleEdit"
      />
    </template>
    
    <!-- Empty State with Add Button inline -->
    <div v-if="tasks.length === 0" class="empty-state-row">
      <span class="empty-text">Have a nice day ☀️</span>
    </div>
  </div>
</template>

<script setup>
import TaskItem from './TaskItem.vue';

defineProps({
  tasks: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['update-task', 'delete-task', 'edit-task']);

const handleUpdate = (task) => {
  emit('update-task', task);
};

const handleDelete = (taskId) => {
  emit('delete-task', taskId);
};

const handleEdit = (task) => {
  emit('edit-task', task);
};
</script>

<style scoped>
.task-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.empty-state-row {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.empty-text {
  color: var(--text-secondary);
  font-style: italic;
  font-size: 16px;
}
</style>
