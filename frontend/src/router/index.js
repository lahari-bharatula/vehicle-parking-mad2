import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import UserdashView from '@/views/UserdashView.vue'
import AdmindashView from '@/views/AdmindashView.vue'
import bookingView from '@/views/bookingView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/userDash',
      name: 'userdash',
      component: UserdashView
    },
    {
      path: '/adminDash',
      name: 'adminDash',
      component: AdmindashView
    },
    {
      path: '/booking',
      name: 'booking',
      component: bookingView
    }

  ],
})

export default router
