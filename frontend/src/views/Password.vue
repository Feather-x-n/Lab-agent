<script setup>
import { reactive, ref } from 'vue'
import { updatePasswordAPi } from '@/api/user.js'
import { ElMessage } from 'element-plus'
import { logout } from '@/utils/auth.js'
import router from '@/router/index.js'
//定义表单状态
const formRef = ref()
//定义提交状态
const submitting = ref(false)
//定义字段
const form = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})
//定义验证规则
const validatePass = (rule, value, callback) => {
  if (value === '') {
    callback(new Error('不能为空'))
  } else {
    if (value !== form.newPassword) {
      callback(new Error('两次密码不一致'))
    }else{
      callback()
    }
  }
}
const rules = {
  oldPassword: [{required:true,message:"请输入原密码",trigger:"blur"}],
  newPassword:[{required:true,message:"请输入新密码",trigger:"blur"}],
  confirmPassword:[{validator: validatePass, trigger: "blur" }],
}
//定义数据处理函数
const handleSubmit = async () => {
  const valid = await formRef.value.validate().catch(()=>false)
  if (!valid) {
    return false
  }
  submitting.value = true
  try {
    const res = await updatePasswordAPi({
      old_password: form.oldPassword,
      new_password: form.newPassword
    })
    if (res.code === 200) {
      ElMessage.success("密码修改成功")
      logout()
      await router.push('/login')
    }
  }finally {
    submitting.value = false
  }
}
</script>

<template>
  <el-card class="form-card" >
    <template #header>
      <div class="card-header" style="font-size: 16px;font-weight: bold">
        <span>修改密码</span>
      </div>
    </template>
    <el-form ref="formRef" :rules="rules" :model="form" label-width="150px">
      <el-form-item label="原密码" prop="oldPassword" class="form-input">
        <el-input  type="password" show-password v-model="form.oldPassword" placeholder="请输入原密码" />
      </el-form-item>
      <el-form-item label="请设置新密码" prop="newPassword" class="form-input">
        <el-input type="password" show-password v-model="form.newPassword" placeholder="请输入密码" />
      </el-form-item>
      <el-form-item label="请确认密码" prop="confirmPassword" class="form-input">
        <el-input  type="password" show-password v-model="form.confirmPassword" placeholder="请输入确认密码" />
      </el-form-item>
      <el-form-item>
        <el-button :loading="submitting" type="primary" @click="handleSubmit" >保存修改</el-button>
      </el-form-item>
    </el-form>
    <template #footer>智能实验室预约系统</template>
  </el-card>
</template>
<style scoped>
.form-card{
  width: 50vw;
  margin: 0 auto;
}
.form-input{
  width: 75%;
}
</style>