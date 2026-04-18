import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';

console.log('🚀 Starting Classical Music Player...');

const app = createApp(App);
app.use(createPinia());
app.use(router);

app.config.errorHandler = (err, instance, info) => {
  console.error('❌ Vue Error:', err, info);
};

console.log('📦 Mounting app to #app...');
app.mount('#app');
console.log('✅ App mounted successfully!');

// Register service worker (only in production)
if (import.meta.env.PROD) {
  if (typeof (window as any).__PWA_REGISTER__ === 'function') {
    const { registerSW } = (window as any).__PWA_REGISTER__;
    registerSW();
  }
}
