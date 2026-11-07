<script setup>
import { Search, Plus } from '@element-plus/icons-vue'
import { onMounted, reactive, ref } from 'vue'
import { createUserAPI, deleteUserAPI, getUserListApi, updateUserAPI } from '@/api/user.js'
import { ElMessage, ElMessageBox } from 'element-plus'

//表单校验状态
const formRef = ref()
//定义Table组件的渲染数据列表
const tableData = ref([])
//定义查询状态
const searchLoading = ref(false)
//定义表单状态
const tableLoading = ref(false)
//定义总查询数
const total = ref(0)
//定义对话卡片的状态
const dialogVisible = ref(false)
//定义保存按钮状态
const createSaving = ref(false);
//定义请求数据表单
const form = reactive({
  username: '',
  name: '',
  role: 'student',
  email: '',
  phone: '',
  avatar: '',
  status: 1
})
//定义表单校验规则
const rules = {
  username:[{required:true,message:"账号不能为空", trigger:'blur'}],
  name:[{required:true,message:"请输入名称",trigger:'blur'}],
  email:[{type:"email",message:"邮箱格式错误",trigger:'blur'}],
  phone:[{pattern:/^1[3-9]\d{9}$/,message:"手机号格式错误",trigger:'blur'}],
}
//定义查询参数列表
const params = reactive({
  page: 1,
  pageSize: 10,
  keywords: '',
})
//加载分页数据
const load = async () => {
  tableLoading.value = true
  try {
    const res = await getUserListApi({
      page: params.page,
      page_size: params.pageSize,
      keywords: params.keywords
    })
    if (res.code === 200) {
      tableData.value = res.data?.list
      total.value = res.data?.total
    }
  }finally {
    tableLoading.value = false
  }
}
//查询功能
const handleSearch = async () => {
  searchLoading.value = true
  try{
    params.page = 1
    load()
    searchLoading.value = false
  }finally {
    tableLoading.value = false
  }
}
//编写覆盖表单功能
const resetForm = () => {
  Object.assign(form, {
    id: null,
    username: '',
    name: '',
    role: 'student',
    email: '',
    phone: '',
    avatar: '',
    status: 1
  })
}
const handleCreate = () => {
  resetForm()
  dialogVisible.value = true
}
//编写保存按钮功能
const handleSave = async () => {
  const valid = await formRef.value.validate().catch(()=>false)
  if (!valid) {
    return false
  }
  createSaving.value = true
  try{
    const res = form.id ? await updateUserAPI(form.id,form) : await createUserAPI(form)
    if (res.code === 200) {
      createSaving.value = false
      load()
      dialogVisible.value = false
      ElMessage.success("操作成功")
    }
  }finally {
    createSaving.value = false
  }
}
//定义编辑按钮
const handleEdit = (row) => {
  resetForm()
  Object.assign(form, {
    id: row.id,
    username: row.username,
    name: row.name,
    role: row.role,
    email: row.email,
    phone: row.phone,
    avatar: row.avatar,
    status: row.status
  })
  dialogVisible.value = true
}
//编写删除功能
const handleDelete = async (row) => {
  ElMessageBox.confirm(`确认删除用户 [${row.username}] ？`, '确认删除', { type: 'warning' }).then(
    async () => {
      const res = await deleteUserAPI(row.id)
      if (res.code === 200) {
        ElMessage.success('删除用户成功')
        load()
      }
    }
  )
}
//挂载
onMounted(()=>{
  load()
})
</script>

<template>
  <div>
    <el-card>
      <template #header>
        <div class="User-form-header">
          用户管理
        </div>
      </template>
      <div style="margin-bottom: 10px;">
        <el-input
          v-model="params.keywords"
          placeholder="请输入需要查询的昵称或者账号"
          style="width:30%; margin-left:6px"
          clearable
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        ></el-input>
        <el-button  style="width: 15%;margin-left: 6px" plain @click="handleCreate" :icon="Plus">新建</el-button>
        <el-button :loading="searchLoading" type="primary" style="width: 15%" @click="handleSearch" :icon="Search">查询</el-button>
      </div>
      <el-table
        :data="tableData"
        style="width: 100%;"
        v-loading="tableLoading"
      >
        <el-table-column prop="username" label="账号" width="180" />
        <el-table-column prop="name" label="昵称" width="180" />
        <el-table-column prop="avatar" label="头像" width="180" >
          <template #default="{row}">
            <div style="min-height: 50px">
              <img
                v-if="row.avatar"
                style="display: block; width: 50px; height: 50px; border-radius: 50%"
                :src="row.avatar"
                alt=""
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" width="180" />
        <el-table-column prop="phone" label="手机号" width="180" />
        <el-table-column prop="role" label="角色" width="180" >
          <template #default="{ row }">
            {{ row.role === 'admin' ? '管理员' : '学生' }}
          </template>
        </el-table-column>>
        <el-table-column prop="status" label="状态" width="180" >
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'error'">
              {{ row.status === 1 ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>>
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" text bg @click="handleEdit(row)" >编辑</el-button>
            <el-button type="danger" text bg @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="User-pagination">
          <el-pagination
            v-model:current-page="params.page"
            v-model:page-size="params.pageSize"
            :total="total"
            background
            layout="total, prev, pager, next"
            @current-change="load"
          />
      </div>
    </el-card>
    <el-dialog
      v-model="dialogVisible"
      :title="form.id ? '编辑' : '新增'"
      width="450"
    >
      <el-form
        ref="formRef"
        :rules="rules"
        :model="form"
        label-width="100px"
        style="
          width: 100%;
">
        <el-form-item label="账号" prop="username" >
          <el-input :disabled="!!form.id"  v-model="form.username" placeholder="请输入账号"/>
        </el-form-item>
        <el-form-item label="昵称" prop="name">
          <el-input v-model="form.name" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role">
            <el-option label="学生" value="student"></el-option>
            <el-option label="管理员" value="admin"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="form.status">
            <el-radio :value="1">正常</el-radio>
            <el-radio :value="0">禁用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button    style="width: 25%"  plain @click="dialogVisible = false" >取消</el-button>
        <el-button  :loading="createSaving" type="primary" style="width: 25%" @click="handleSave" >保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.User-form-header {
  font-weight: bold;
  font-size: 16px;
}
.User-pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>