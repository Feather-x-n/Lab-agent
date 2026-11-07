<script setup>
import { Search, Plus } from '@element-plus/icons-vue'
import { onMounted, reactive, ref } from 'vue'
import { create_equipment, delete_equipment, get_equipment_list, update_equipment } from '@/api/Euipment.js'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getLabList } from '@/api/lab.js'
import { uploadFileApi } from '@/api/file.js'
const dialogVisible =ref(false)
const createEquipment = () => {
  dialogVisible.value = true
}
const formCancel = ()=>{
  dialogVisible.value = false
}
const formRef = ref()
const loading = ref(false)
//定义表单渲染数据
const tableData = ref([])
//定义选择列表
const labOptions =ref([])
// 定义列表总数
const total = ref(0)
//定义表单状态
const tableloading =ref(false)
//定义查询得params参数
const params = reactive({
  page: 1,
  page_size: 10,
  keywords: '',
})
//定义验证规则
const rules = {
  lab_id: [{ required: true, message: '请选择实验室', trigger: 'change' }],
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }]
}
//定义保存按钮状态
const saveLoading = ref(false)
//定义form表单
const form = reactive({
  id: null,
  lab_id: null,
  name: '',
  description: '',
  img: '',
  spec: '',
  quantity: 1,
  status: 1
})
//清空表单
const resetForm = () => {
  Object.assign(form,{
    id: null,
    lab_id: null,
    name: '',
    description: '',
    img: '',
    spec: '',
    quantity: 1,
    status: 1
  })
}
//新建设备方法
const handleSave = async () => {
  saveLoading.value = true
  try{
    const res = form.id ? await update_equipment(form.id,form) : await create_equipment(form)
    if (res.code == 200){
      dialogVisible.value = false
      ElMessage.success("操作成功")
      load()
    }
  }finally{
    saveLoading.value = false
  }
}
//定义基础加载数据函数
const load = async ()=>{
  tableloading.value = true
  try{
   const res = await get_equipment_list(params)
    if(res.code === 200){
      tableData.value = res.data?.list
      total.value = res.data?.total
    }
  }finally {
    tableloading.value = false
  }
}
//定义查询实验室列表方法
const loadLabs = async () => {
  const res = await getLabList({ page: 1, page_size: 100 })
  if (res.code === 200) {
    labOptions.value = res.data?.list
  }
}
//搜索方法
const handleSearch = async () => {
  params.page = 1
  load()
}
//图片验证和上传方法
const beforeAvatarUpload = (file) => {
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
const handleFileUpload = async ({ file }) => {
  try {
    const res = await uploadFileApi(file)
    if (res.code === 200) {
      form.img = res.data?.url
    }
  } catch {}
}
const handleEdit = (row) => {
  resetForm()
  Object.assign(form, {
    id: row.id,
    lab_id: row.lab_id,
    name: row.name,
    description: row.description,
    img: row.img,
    spec: row.spec,
    quantity: row.quantity,
    status: row.status
  })
  dialogVisible.value = true
}
const handleDelete = (row) => {
  ElMessageBox.confirm(`确认删除实验室设备 [${row.name}] ？`, '确认删除', { type: 'warning' }).then(
    async () => {
      const res = await delete_equipment(row.id)
      if (res.code === 200) {
        ElMessage.success('删除成功')
        load()
      }
    }
  )
}

onMounted(()=>{
  loadLabs()
  load()
})
</script>

<template>
    <div>
      <el-card>
        <template #header>
          <span style="font-weight: bold;font-size:16px">设备管理</span>
        </template>
        <div>
          <el-input placeholder="请输入需要查询的设备" style="width:30%;margin-right: 6px"
                    v-model="params.keywords"
                    clearable
                    @keyup.enter="handleSearch"
                    @clear="handleSearch"></el-input>
          <el-select
            placeholder="请选择实验室"
            v-model="params.lab_id"
            style="width: 200px; margin-right: 8px"
            clearable
            @change="handleSearch"
            @clear="handleSearch"
          >
            <el-option v-for="item in labOptions" :key="item.id" :value="item.id" :label="item.name">
            </el-option>
          </el-select>
          <el-button style="width: 15%;margin-right: 6px" @click = "createEquipment">新建</el-button>
          <el-button type="primary" style="width: 15%" @click="handleSearch" >查询</el-button>
        </div>
        <el-table
          :data="tableData"
          :load = "tableloading"
        >
          <el-table-column label="所属实验室" prop="lab_name"></el-table-column>
          <el-table-column label="设备名称" prop="name"></el-table-column>
          <el-table-column label="图片">
            <template #default="{ row }">
              <div style="min-height: 50px">
                <img
                  v-if="row.img"
                  style="display: block; width: 50px; height: 50px; border-radius: 6px"
                  :src="row.img"
                  alt=""
                />
              </div>
            </template>
          </el-table-column>
          <el-table-column label="型号规格" prop="spec" ></el-table-column>
          <el-table-column label="数量"  prop="quantity"></el-table-column>
          <el-table-column label="状态" prop="status">
            <template #default="{ row }">
              <el-tag :type="row.status === 1 ? 'success' : 'danger'">
                {{ row.status === 1 ? '正常' : '维修' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" >
            <template #default="{ row }">
              <el-button type="primary" text bg @click="handleEdit(row)" >编辑</el-button>
              <el-button type="danger" text bg @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div style="margin-top: 10px; display: flex; justify-content: flex-end">
          <el-pagination
            v-model:current-page="params.page"
            v-model:page-size="params.page_size"
            :total="total"
            background
            layout="total, prev, pager, next"
            @current-change="load"
          />
        </div>
      </el-card>
      <el-dialog v-model="dialogVisible" :title="form.id ? '编辑' : '新增'">
        <el-form
          ref="formRef"
          :rules="rules"
          :model="form"
          label-width="100px"
          style="width: 100%; padding-right: 30px; padding-top: 16px"
          v-loading="loading"
        >
          <el-form-item label="所属实验室" prop="lab_id">
            <el-select v-model="form.lab_id" placeholder="请选择实验室" style="width: 100%">
              <el-option
                v-for="item in labOptions"
                :key="item.id"
                :label="item.name"
                :value="item.id"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="设备名称" prop="name">
            <el-input  placeholder="请输入设备名称" v-model="form.name" />
          </el-form-item>
          <el-form-item label="说明">
            <el-input  type="textarea" :rows="3" placeholder="请输入说明"  v-model="form.description"/>
          </el-form-item>
          <el-form-item label="图片">
            <el-upload
              class="avatar-uploader"
              :http-request="handleFileUpload"
              :show-file-list="false"
              accept="image/jpeg,image/png,image/gif,image/webp"
              :before-upload="beforeAvatarUpload"
            >
              <img v-if="form.img" :src="form.img" class="avatar" />
              <el-icon v-else class="avatar-uploader-icon"><Plus /></el-icon>
            </el-upload>
          </el-form-item>
          <el-form-item label="型号规格">
            <el-input  placeholder="例如 RTX4090 24G" v-model="form.spec" />
          </el-form-item>
          <el-form-item label="数量"  prop="quantity">
            <el-input-number  :min="1" :max="999"  v-model="form.quantity" />
          </el-form-item>
          <el-form-item label="状态">
            <el-radio-group  v-model="form.status">
              <el-radio :value="1">正常</el-radio>
              <el-radio :value="0">维修</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="formCancel">取消</el-button>
          <el-button type="primary" :loading="saveLoading" @click="handleSave" >保存</el-button>
        </template>
      </el-dialog>
    </div>
</template>

<style scoped>

</style>