<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <div class="modal-header">
        <h2>Account</h2>
        <button class="close-btn" @click="$emit('close')">
          <X :size="20" />
        </button>
      </div>

      <div class="settings-content">
        <!-- Account Info -->
        <section class="settings-section">
          <h3 class="section-title">ACCOUNT</h3>
          <div class="account-card">
            <div class="account-icon">
              <User :size="24" />
            </div>
            <div class="account-info">
              <span class="account-label">Logged in as</span>
              <span class="account-id">{{ accountId }}</span>
            </div>
          </div>
        </section>

        <!-- Addresses -->
        <section class="settings-section">
          <h3 class="section-title">ADDRESSES</h3>
          
          <div class="form-group">
            <label>
              <Home :size="16" />
              Home Address
            </label>
            <input 
              type="text" 
              v-model="localHomeAddress" 
              class="form-input"
              placeholder="Enter your home address"
            />
          </div>

          <div class="form-group">
            <label>
              <GraduationCap :size="16" />
              School/Work Address
            </label>
            <input 
              type="text" 
              v-model="localSchoolAddress" 
              class="form-input"
              placeholder="Enter your school or work address"
            />
          </div>
        </section>

        <!-- Current Location -->
        <section class="settings-section">
          <h3 class="section-title">CURRENT LOCATION</h3>
          <div class="location-card">
            <div class="location-info">
              <MapPin :size="20" class="location-icon" />
              <div class="location-text">
                <span v-if="locationLoading">Getting location...</span>
                <span v-else-if="currentLocation">
                  {{ currentLocation.latitude.toFixed(6) }}, {{ currentLocation.longitude.toFixed(6) }}
                </span>
                <span v-else class="location-placeholder">Location not available</span>
              </div>
            </div>
            <button class="refresh-btn" @click="refreshLocation" :disabled="locationLoading">
              <RefreshCw :size="16" :class="{ spinning: locationLoading }" />
            </button>
          </div>
        </section>

        <!-- Logout -->
        <section class="settings-section">
          <button class="logout-btn" @click="handleLogout">
            <LogOut :size="18" />
            <span>Logout</span>
          </button>
        </section>
      </div>

      <div class="modal-footer">
        <button class="cancel-btn" @click="$emit('close')">Cancel</button>
        <button class="save-btn" @click="handleSave">Save</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { X, User, Home, GraduationCap, MapPin, RefreshCw, LogOut } from 'lucide-vue-next';

const props = defineProps({
  accountId: { type: String, required: true },
  homeAddress: { type: String, default: '' },
  schoolAddress: { type: String, default: '' }
});

const emit = defineEmits(['close', 'save', 'logout']);

const localHomeAddress = ref(props.homeAddress);
const localSchoolAddress = ref(props.schoolAddress);
const currentLocation = ref(null);
const locationLoading = ref(false);

const refreshLocation = () => {
  if (!navigator.geolocation) {
    alert('Geolocation is not supported by your browser');
    return;
  }

  locationLoading.value = true;

  navigator.geolocation.getCurrentPosition(
    (position) => {
      currentLocation.value = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy: position.coords.accuracy,
        timestamp: new Date().toISOString()
      };
      locationLoading.value = false;
    },
    (error) => {
      console.error('Error getting location:', error);
      locationLoading.value = false;
      alert('Unable to get location. Please check permissions.');
    },
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
  );
};

const handleSave = () => {
  emit('save', {
    homeAddress: localHomeAddress.value,
    schoolAddress: localSchoolAddress.value,
    currentLocation: currentLocation.value
  });
  emit('close');
};

const handleLogout = () => {
  emit('logout');
};

onMounted(() => {
  refreshLocation();
});
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
  width: 420px;
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
  background: none;
  border: none;
  cursor: pointer;
}

.close-btn:hover {
  color: var(--text-primary);
}

.settings-content {
  padding: 20px 24px;
  max-height: 60vh;
  overflow-y: auto;
}

.settings-section {
  margin-bottom: 24px;
}

.settings-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 12px;
}

/* Account Card */
.account-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  background: #F3F4F6;
  border-radius: 12px;
}

.account-icon {
  width: 48px;
  height: 48px;
  background: #E5E7EB;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.account-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.account-label {
  font-size: 12px;
  color: var(--text-secondary);
}

.account-id {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

/* Form Group */
.form-group {
  margin-bottom: 14px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.form-input {
  width: 100%;
  border: 1px solid #E5E7EB;
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-input:focus {
  border-color: #6366F1;
}

/* Location Card */
.location-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  background: #F0FDF4;
  border-radius: 12px;
}

.location-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.location-icon {
  color: #22C55E;
}

.location-text {
  font-size: 14px;
  color: var(--text-primary);
}

.location-placeholder {
  color: var(--text-secondary);
}

.refresh-btn {
  padding: 8px;
  background: white;
  border: none;
  border-radius: 8px;
  color: #22C55E;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.refresh-btn:hover:not(:disabled) {
  background: #DCFCE7;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Logout Button */
.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  width: 100%;
  padding: 12px;
  background: #FEE2E2;
  color: #EF4444;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
}

.logout-btn:hover {
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
