import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layouts/Layout.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import { getToken } from '@/utils/auth.js'
import Profile from '@/views/Profile.vue'
import Password from '@/views/Password.vue'
import User from '@/views/User.vue'
import Lab from '@/views/Lab.vue'
import Equipment from '@/views/Equipment.vue'
import LabList from '@/views/LabList.vue'
import LabEquipment from '@/views/LabEquipment.vue'
import AIChat from '@/views/AIChat.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {path: '/', redirect: '/manager/home'},
    {path: '/manager',name:'Layout',
      component: Layout,
      children:[
        {
          path: 'home',
          name: 'Home',
          component: () => import('@/views/Home.vue')
        },
        {
          path: 'lab',
          name: 'Lab',
          component: () => import('@/views/Lab.vue')
        },
        {
          path:'profile',
          name:'Profile',
          component:Profile
        },
        {
          path:'password',
          name:'Password',
          component:Password
        },
        {
          path:'user',
          name:'User',
          component:User
        },
        {
          path:'lab',
          name:'Lab',
          component:Lab
        },
        {
          path:'equipment',
          name:'Equipment',
          component:Equipment
        },
        {
          path:'lablist',
          name:'LabList',
          component:LabList
        },
        {
          path:'lab-equipment',
          name:'LabEquipment',
          component:LabEquipment
        },
        {
          path: 'my-reservation',
          name: 'MyReservation',
          component: () => import('@/views/MyReservation.vue')
        },
        {
          path: 'audit-reservation',
          name: 'AuditReservation',
          component: () => import('@/views/AuditReservation.vue')
        },
        {
          path: 'ai-chat',
          name: 'AIChat',
          component:AIChat
        }
      ] },
    {path:'/login',name:'Login',component:Login},
    {path:'/register',name:'Register',component:Register},
  ],
})
// 路由守卫
router.beforeEach((to) => {
  const token = getToken()
  if (to.path === '/login' || to.path === '/register') {
    return true
  } else {
    return token ? true : '/login'
  }
})
export default router
