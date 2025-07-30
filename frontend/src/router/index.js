import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import SignupView from '../views/SignupView.vue'
import UserdashView from '../views/UserdashView.vue'
import BookingView from '@/views/BookingView.vue'
import AdmindashView from '../views/AdmindashView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue'),
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignupView,
    },
    {
      path: '/userdash',
      name: 'userdash',
      component: UserdashView,
    },
    {
      path: '/booking',
      name: 'booking',
      component: BookingView
    },
    {
      path: '/admindash',
      name: 'admindash',
      component: AdmindashView
    }
  ],
})

export default router
