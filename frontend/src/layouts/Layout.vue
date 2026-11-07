<script setup>
import {
  Menu as IconMenu,
  House,
  Setting,
  User,
  OfficeBuilding,
  Tickets,
  Document,
  ChatDotRound,
  DocumentChecked
} from '@element-plus/icons-vue'
import router from '@/router/index.js'
import { logout } from '@/utils/auth.js'
import {useUser} from '@/utils/user.js'

//获取信息
const {userInfo} = useUser()
// 登出按钮
const handleCommand = (command)=>{
  if(command === 'profile'){
    router.push('/manager/profile')
  }else if(command === 'password'){
    router.push('/manager/password')
  }else if(command === 'exit'){
    logout()
    router.push('/login')
  }
}

</script>

<template>
  <div class="common-layout">
    <!--    头部-->
    <el-container style="min-height: 100vh">
      <el-header style="display: flex;align-items: center; border-bottom: 1px solid #ddd; background-color: #fff">
        <div
          style="flex: 1; display: flex; align-items: center; font-size: 24px; font-weight: bold"
        >
          <img style="width: 40px" src="@/assets/images/logo.png" alt="" />
          <div style="margin-left: 5px">智能实验室预约系统</div>
        </div>
        <div style="cursor: pointer" >
          <el-dropdown @command="handleCommand">
            <div style="display: flex; align-items: center">
              <img v-if="userInfo?.avatar" :src="userInfo.avatar" alt=""  style="width: 25px; height: 25px; border-radius: 50%; object-fit: cover" />
              <div style="margin-left:6px">{{userInfo?.name}}</div>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="password">修改密码</el-dropdown-item>
                <el-dropdown-item divided command="exit">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-container>
        <!--        侧边栏-->
        <el-aside width="220px">
          <el-menu router style="height: 100%" default-active="/home">
            <el-menu-item index="/manager/home">
              <el-icon><icon-menu /></el-icon>
              <span>系统首页</span>
            </el-menu-item>
            <el-menu-item index="/manager/lablist" v-if="userInfo?.role === 'student'">
              <el-icon><OfficeBuilding /></el-icon>
              实验室列表
            </el-menu-item>
            <el-menu-item v-if="userInfo?.role === 'admin'"  index="/manager/lab">
              <el-icon><House/></el-icon>
              <span>实验室管理</span>
            </el-menu-item>
            <el-menu-item v-if="userInfo?.role === 'admin'" index="/manager/equipment">
              <el-icon><Setting /></el-icon>
              <span>设备管理</span>
            </el-menu-item>
            <el-menu-item index="/manager/my-reservation" v-if="userInfo?.role === 'student'">
              <el-icon><Tickets /></el-icon>
              我的预约
            </el-menu-item>
            <el-menu-item index="/manager/audit-reservation" v-if="userInfo?.role === 'admin'">
              <el-icon><DocumentChecked /></el-icon>
              预约审核
            </el-menu-item>
            <el-menu-item v-if="userInfo?.role === 'admin'" index="/manager/user">
              <el-icon><User /></el-icon>
              用户管理
            </el-menu-item>
            <el-menu-item index="/manager/ai-chat">
              <el-icon><ChatDotRound /></el-icon>
              AI智能助手
            </el-menu-item>
          </el-menu>
        </el-aside>
        <!--        主体部分-->
        <el-main>
          <router-view/>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>