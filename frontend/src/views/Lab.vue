<script setup>
import { Search, Plus } from '@element-plus/icons-vue'
import { onMounted, reactive, ref } from 'vue'
import { createLabApi,updateLabApi,getLabList,deleteLab } from '@/api/lab.js'
import { uploadFileApi } from '@/api/file.js'
import { ElMessage, ElMessageBox } from 'element-plus'
//定义table组件渲染数组
const tableData = ref([])
//定义table组件状态
const tableLoading = ref(false)
//定义查询按钮状态
const serachLoading = ref(false)
//弹出表单状态
const dialogVisible = ref(false)
//创建信息按钮状态
const createSaving = ref(false)
//定义表单数据
const formRef = ref()
const total = ref(0)
//定义查询参数列表
const params = reactive({
  page: 1,
  pageSize: 10,
  keywords: '',
})
//验证规则
const rules = {
  name: [{ required: true, message: '请输入实验室名称', trigger: 'blur' }],
  capacity: [{ required: true, message: '请输入容纳人数', trigger: 'blur' }]
}
//定义表单数据
const form = reactive({
  id: null,
  name: '',
  location: '',
  capacity: 20,
  open_time: '08:00',
  close_time: '18:00',
  description: '',
  img: '',
  status: 1
})
// 加载数据方法
const load = async ()=>{
  tableLoading.value = true
  try{
    const res = await getLabList({
      page: params.page,
      page_size: params.pageSize,
      keywords: params.keywords
      }
    )
    if(res.code === 200){
      tableData.value = res.data?.list
      total.value = res.data?.total
    }
  }finally{
    tableLoading.value = false
  }
}
//重置表单
const resetForm = () => {
  Object.assign(form, {
    id: null,
    name: '',
    location: '',
    capacity: 20,
    open_time: '08:00',
    close_time: '18:00',
    description: '',
    img: '',
    status: 1
  })
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
//上传图片
const handelFileLoad = async ({file}) => {
  try{
    const res = await uploadFileApi(file)
    if (res.code === 200) {
      form.img = res.data?.url
    }
  }catch{
  }
}
//保存
const handleSave = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  createSaving.value = true
  if (!valid) return
  try{
    const res = form.id ? await updateLabApi(form.id, form) : await createLabApi(form)
    if (res.code === 200) {
      dialogVisible.value = false
      ElMessage.success('操作成功')
      load()
    }
  }finally{
    createSaving.value = false
  }
}
//编辑
const handleEdit = (row) => {
  resetForm()
  Object.assign(form, {
    id: row.id,
    name: row.name,
    location: row.location,
    capacity: row.capacity,
    open_time: row.open_time,
    close_time: row.close_time,
    description: row.description,
    img: row.img,
    status: row.status
  })
  dialogVisible.value = true
}
//删除
const handleDelete = (row) => {
  ElMessageBox.confirm(`确认删除实验室 [${row.name}] ？`, '确认删除', { type: 'warning' }).then(
    async () => {
      const res = await deleteLab(row.id)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        load()
      }
    }
  )
}
//新建
const handleCreate = () => {
  resetForm()
  dialogVisible.value = true
}
//搜索
const handleSearch = () => {
  params.page = 1
  load()
}
onMounted(()=>{
  load()
})
</script>

<template>
 <div class="lab-container">
   <el-card>
     <template #header>
       实验室管理
     </template>
     <div class="lab-input">
       <el-input
         v-model="params.keywords"
         placeholder="请输入需要查询的昵称或者账号"
         style="width:30%; margin-right:6px"
         clearable
         @keyup.enter="handleSearch"
         @clear="handleSearch">
       </el-input>
       <el-button style="width:15%" :icon="Plus" @click="handleCreate" >新建</el-button>
       <el-button :icon="Search" type="primary" style="width: 15%" :loading="serachLoading" @click="handleSearch">查询</el-button>
     </div>
     <el-table
       :data="tableData"
       style="width: 100%;"
       v-loading="tableLoading"
     >
       <el-table-column prop="name" label="名称" width="180" />
       <el-table-column prop="description" label="简介" width="180" />
       <el-table-column prop="img" label="图片" width="180" >
         <template #default="{row}">
           <div style="min-height: 50px">
             <img
               v-if="row.img"
               style="display: block; width: 50px; height: 50px; border-radius: 50%"
               :src="row.img"
               alt=""
             />
           </div>
         </template>
       </el-table-column>
       <el-table-column prop="location" label="位置" width="180" />
       <el-table-column prop="capacity" label="容纳人数" width="180" />
       <el-table-column label="开放时间" width="180" >
         <template #default="{ row }">
           {{ row.open_time && row.close_time ? `${row.open_time} - ${row.close_time}` : '-' }}
         </template>
       </el-table-column>
       <el-table-column prop="status" label="状态" width="180" >
         <template #default="{ row }">
           <el-tag :type="row.status === 1 ? 'success' : 'error'">
             {{ row.status === 1 ? '开放' : '关闭' }}
           </el-tag>
         </template>
       </el-table-column>>
       <el-table-column label="操作" width="160">
         <template #default="{ row }">
           <el-button type="primary" text bg @click = "handleEdit(row)" >编辑</el-button>
           <el-button type="danger" text bg @click = "handleDelete(row)">删除</el-button>
         </template>
       </el-table-column>
     </el-table>
     <div class="lab-pagination">
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
       <el-form-item label="封面">
         <el-upload
           class="avatar-uploader"
           :http-request="handelFileLoad"
           :show-file-list="false"
           :before-upload="beforeAvatarUpload"
           accept="image/jpeg,image/png,image/gif,image/webp"
         >
           <img v-if="form.img" :src="form.img" class="avatar" />
           <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
         </el-upload>
       </el-form-item>
       <el-form-item label="名称" prop="name" >
         <el-input  v-model="form.name" placeholder="请输入名称"/>
       </el-form-item>
       <el-form-item label="位置" prop="location">
         <el-input v-model="form.location" placeholder="请输入地址" />
       </el-form-item>
       <el-form-item label="容纳人数" prop="capacity">
         <el-input-number v-model="form.capacity" :min="1" :max="500" />
       </el-form-item>
       <el-form-item label="简介">
         <el-input
           v-model="form.description"
           type="textarea"
           :rows="3"
           placeholder="请输入简介"
         />
       </el-form-item>
       <el-form-item label="开放时间">
         <el-time-picker
           v-model="form.open_time"
           format="HH:mm"
           value-format="HH:mm"
           placeholder="开始"
           style="width: 140px; margin-right: 8px"
         />
         <el-time-picker
           v-model="form.close_time"
           format="HH:mm"
           value-format="HH:mm"
           placeholder="结束"
           style="width: 140px"
         />
       </el-form-item>
       <el-form-item label="状态">
         <el-radio-group v-model="form.status">
           <el-radio :value="1">开放</el-radio>
           <el-radio :value="0">关闭</el-radio>
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
.lab-container {
  font-size: 16px;
  font-weight: bold;
}
.lab-pagination{
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
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