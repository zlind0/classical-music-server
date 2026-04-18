import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../pages/Login.vue'),
  },
  {
    path: '/',
    component: () => import('../layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'Player',
        component: () => import('../pages/Player.vue'),
      },
      {
        path: 'search',
        name: 'Search',
        component: () => import('../pages/Search.vue'),
      },
      {
        path: 'library',
        name: 'Library',
        component: () => import('../pages/Library.vue'),
      },
      {
        path: 'admin',
        name: 'Admin',
        component: () => import('../pages/Admin.vue'),
        meta: { requiresAdmin: true },
      },
    ],
  },
  // Catch-all route - redirect to home
  {
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// Fix initial route if accessing /index.html
if (typeof window !== 'undefined' && window.location.pathname === '/index.html') {
  console.log('🔄 Detected /index.html, redirecting to /');
  window.history.replaceState({}, '', '/');
}

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore();
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);
  const requiresAdmin = to.matched.some((record) => record.meta.requiresAdmin);

  console.log('🔄 Route navigation:', {
    to: to.path,
    from: _from.path,
    hasToken: !!authStore.token,
    token: authStore.token?.substring(0, 20) + '...',
    requiresAuth,
  });

  if (requiresAuth && !authStore.token) {
    console.log('❌ No token, redirecting to /login');
    next('/login');
  } else if (requiresAdmin && authStore.role !== 'admin') {
    console.log('❌ Not admin, redirecting to /');
    next('/');
  } else {
    console.log('✅ Allowing navigation');
    next();
  }
});

router.afterEach((to) => {
  console.log('✅ Route changed to:', to.path);
});

export default router;
