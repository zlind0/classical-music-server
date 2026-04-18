<template>
  <div id="app">
    <router-view />
    <!-- Debug: Show if router-view is empty -->
    <div v-if="isDebug" style="position: fixed; bottom: 10px; right: 10px; background: #333; color: #0f0; padding: 10px; font-size: 12px; font-family: monospace; z-index: 9999; max-width: 300px; word-break: break-all;">
      <div>Token: {{ authStore.token ? 'YES ✓' : 'NO ✗' }}</div>
      <div>Route: {{ $route.path }}</div>
      <div>App loaded: ✓</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from './stores/auth';
import { useRouter, useRoute } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();
const route = useRoute();
const isDebug = ref(true);

console.log('🎨 App.vue mounted, authStore:', {
  hasToken: !!authStore.token,
  username: authStore.username,
});

onMounted(async () => {
  console.log('📱 App.vue onMounted');
  // Check if user has valid token
  const token = localStorage.getItem('token');
  if (token) {
    console.log('🔑 Found token in localStorage');
    authStore.setToken(token);
  } else {
    console.log('⚠️ No token in localStorage');
  }
});
</script>

<style scoped>
#app {
  min-height: 100vh;
  background: #f5f5f5;
}
</style>
