import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import TeacherDashboard from '../views/TeacherDashboard.vue'
import StudentDashboard from '../views/StudentDashboard.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    component: Login
  },
  { 
    path: '/admin-dashboard', 
    component: AdminDashboard 
  },
  { path: '/teacher-dashboard', 
    component: TeacherDashboard },
  { path: '/student-dashboard',
    component: StudentDashboard },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
