//封装网络请求
import axios from 'axios'
import { getToken, logout } from '@/utils/auth.js'
import { ElMessage } from 'element-plus'
import router from '@/router/index.js'
const baseURL = "http://127.0.0.1:8000"
const service = axios.create({
  baseURL:baseURL,
  timeout: 30000,
})
//请求拦截器的配置
service.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => {
  return  Promise.reject(error)
})
//返回拦截器配置
service.interceptors.response.use((res) => {
  const data = res.data
  if (data.code !== 200) {
    ElMessage.error(data.message || "请求失败")
    if (data.code === 401) {
      logout()
      router.push('/login')
      return Promise.reject(data)
    }
  }
  return data
}, (error) => {
  if(error.response) {
    const httpStatusCode = error.response.status
    if (httpStatusCode === 401) {
      ElMessage.error('登录状态已失效请重新登录')
      logout()
      router.push('/login')
    }else{
      ElMessage.error(error.response.data?.message || '请求失败')
    }
  }else{
    // 后端没启动，网络异常了
    ElMessage.error('网络异常，请检查后端服务')
  }
  return Promise.reject(error)
})
export default service