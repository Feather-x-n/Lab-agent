<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { uploadFileApi } from '@/api/file.js'
import { ElMessage } from 'element-plus'
import { getUserInfo } from '@/utils/auth.js'
import { getUserInfoApi, updateUserInfoAPi } from '@/api/user.js'
import { useUser } from '@/utils/user.js'
const { updateUser } = useUser()
//定义表单状态
const formRef = ref()
const loading = ref(false)
const submitting = ref(false)
const form = reactive({
  username: '',
  name:'',
  role:'',
  email:'',
  phone:'',
  avatar:'',
})
//定义表单验证规则
const rules = {
  name:[{required:true,message:"请输入名称",trigger:'blur'}],
  email:[{type:"email",message:"邮箱格式错误",trigger:'blur'}],
  phone:[{pattern:/^1[3-9]\d{9}$/,message:"手机号格式错误",trigger:'blur'}],
}
//角色的中文映射
const roleLabel = computed(()=>{
  return form.role === "admin"?"管理员":form.role ==="student"?"学生":"未知角色"
})
//定义提交功能
const handelSubmit = async ()=> {
  const valid = await formRef.value.validate().catch(()=>false)
  if (!valid) {
    return false
  }
  submitting.value = true
  try {
    const res = await updateUserInfoAPi(form)
    if (res.code === 200) {
      ElMessage.success("更新成功")
      updateUser(res.data)
    }
  }finally {
    submitting.value = false
  }

}
//定义上传图片的接口函数
const handelFileLoad = async ({file})=> {
  try{
      const res = await uploadFileApi(file)
      if (res.code === 200) {
        form.avatar = res.data?.url
      }
  }catch{
  }
}
//上传图片前的验证
const beforeAvatarUpload = async (file)=> {
  const imageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
  if (!imageTypes.includes(file.type)) {
    ElMessage.error('只能上传图片')
    return false
  }
  if (file.size / 1024 / 1024 > 2) {
    ElMessage.error('上传图片大小不能超过2M')
    return false
  }
  return true
}
//加载用户信息
const loadUserInfo = async () => {
  loading.value = true
  try {
    const res = await getUserInfoApi()
    if (res.code === 200) {
      Object.assign(form, res.data)
    }
  }finally {
    loading.value = false
  }
}
//
onMounted(()=>{
  loadUserInfo()
})
</script>

<template>
  <div class="profile-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>个人信息</span>
        </div>
      </template>
        <el-form
          ref="formRef"
          :rules="rules"
          :model="form"
          label-width="100px"
          v-loading="loading"
          style="
          width: 100%;
">
          <el-form-item>
            <el-upload
              class="avatar-uploader"
              :http-request="handelFileLoad"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              accept="image/jpeg,image/png,image/gif,image/webp"
            >
              <img v-if="form.avatar" :src="form.avatar" class="avatar" />
              <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
            </el-upload>
          </el-form-item>
          <el-form-item label="账号" >
            <el-input v-model="form.username" placeholder="请输入账号" disabled />
          </el-form-item>
          <el-form-item label="昵称" prop="name">
            <el-input v-model="form.name" placeholder="请输入昵称" />
          </el-form-item>
          <el-form-item label="角色">
            <el-input disabled v-model="roleLabel"/>
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="form.email" placeholder="请输入邮箱" />
          </el-form-item>
          <el-form-item label="手机号" prop="phone">
            <el-input v-model="form.phone" placeholder="请输入手机号" />
          </el-form-item>
          <el-form-item>
            <el-button  :loading="submitting" type="primary" style="width: 75%" @click="handelSubmit">保存修改</el-button>
          </el-form-item>
        </el-form>
      <template #footer>智能实验室预约系统</template>
    </el-card>
  </div>
</template>

<style scoped>
.profile-container {
  width: 50%;
  margin-left: 25%;
}
.card-header {
  font-size: 16px;
  font-weight: bold;
}
</style>
<style scoped>
.avatar-uploader .avatar {
  width: 130px;
  height: 130px;
  display: block;
}
</style>
<style>
.avatar-uploader .el-upload {
  border: 1px dashed var(--el-border-color);
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: var(--el-transition-duration-fast);
}
.avatar-uploader .el-upload:hover {
  border-color: var(--el-color-primary);
}
.el-icon.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 130px;
  height: 130px;
  text-align: center;
}
</style>