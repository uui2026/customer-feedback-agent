import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { title: '仪表盘' }
  },
  {
    path: '/feedbacks',
    name: 'FeedbackList',
    component: () => import('@/views/FeedbackList.vue'),
    meta: { title: '反馈列表' }
  },
  {
    path: '/tickets',
    name: 'TicketList',
    component: () => import('@/views/TicketList.vue'),
    meta: { title: '工单列表' }
  },
  {
    path: '/knowledge',
    name: 'KnowledgeBase',
    component: () => import('@/views/KnowledgeBase.vue'),
    meta: { title: '知识库' }
  },
  {
    path: '/pipeline',
    name: 'AgentPipeline',
    component: () => import('@/views/AgentPipeline.vue'),
    meta: { title: '智能体管线' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '首页'} - 客户反馈管理系统`
  next()
})

export default router
