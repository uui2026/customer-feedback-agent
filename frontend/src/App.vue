<template>
  <el-container class="app-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="app-aside">
      <div class="logo-area">
        <img src="/vite.svg" alt="Logo" class="logo-icon" v-if="!isCollapse" />
        <span v-if="!isCollapse" class="logo-text">反馈管理系统</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        router
        background-color="#001529"
        text-color="#ffffffa6"
        active-text-color="#ffffff"
        class="side-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>仪表盘</template>
        </el-menu-item>
        <el-menu-item index="/feedbacks">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>反馈列表</template>
        </el-menu-item>
        <el-menu-item index="/tickets">
          <el-icon><Tickets /></el-icon>
          <template #title>工单列表</template>
        </el-menu-item>
        <el-menu-item index="/knowledge">
          <el-icon><Document /></el-icon>
          <template #title>知识库</template>
        </el-menu-item>
        <el-menu-item index="/pipeline">
          <el-icon><Cpu /></el-icon>
          <template #title>智能体管线</template>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="app-header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <span class="page-title">{{ currentTitle }}</span>
        </div>
        <div class="header-right">
          <el-badge :value="pendingCount" :hidden="pendingCount === 0" class="notification-badge">
            <el-icon :size="20" class="header-icon"><Bell /></el-icon>
          </el-badge>
          <el-dropdown trigger="click">
            <span class="user-info">
              <el-avatar :size="32" class="user-avatar">管</el-avatar>
              <span class="user-name">管理员</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人设置</el-dropdown-item>
                <el-dropdown-item divided>退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  DataAnalysis,
  ChatDotRound,
  Tickets,
  Document,
  Cpu,
  Fold,
  Expand,
  Bell
} from '@element-plus/icons-vue'

const route = useRoute()
const isCollapse = ref(false)
const pendingCount = ref(3)

const activeMenu = computed(() => route.path)
const currentTitle = computed(() => route.meta?.title || '首页')
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.app-container {
  height: 100vh;
}

.app-aside {
  background-color: #001529;
  transition: width 0.3s;
  overflow: hidden;
}

.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-bottom: 1px solid #ffffff1a;
}

.logo-icon {
  width: 28px;
  height: 28px;
}

.logo-text {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.side-menu {
  border-right: none;
}

.app-header {
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  height: 60px;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #333;
}

.collapse-btn:hover {
  color: #409eff;
}

.page-title {
  font-size: 18px;
  font-weight: 500;
  color: #333;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-icon {
  cursor: pointer;
  color: #666;
}

.header-icon:hover {
  color: #409eff;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.user-name {
  font-size: 14px;
  color: #333;
}

.app-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
