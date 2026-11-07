//封装网络请求
import  request  from '../utils/request.js'

export function loginApi(data){
  return request({
    url:'/api/auth/login',
    method:'POST',
    data
  })
}
export function registerApi(data){
  return request({
    url:'/api/auth/register',
    method:'POST',
    data
  })
}