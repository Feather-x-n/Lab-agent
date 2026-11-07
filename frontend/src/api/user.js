import  request  from '../utils/request.js'

export function getUserInfoApi(){
  return request({
    url: '/api/user/me',
    method: 'get',
  })
}
export function updateUserInfoAPi(data){
  return request({
    url: '/api/user/me',
    method: 'put',
    data
  })
}
export function updatePasswordAPi(data){
  return request({
    url: '/api/user/password',
    method: 'put',
    data
  })
}
export function getUserListApi(params){
  return request({
    url: '/api/user/list',
    method: 'get',
    params
  })
}
export function createUserAPI(data){
  return request({
    url: '/api/user',
    method: 'post',
    data
  })
}
export function updateUserAPI(userId,data){
  return request({
    url: `/api/user/${userId}`,
    method: 'put',
    data
  })
}
export function deleteUserAPI(userId){
  return request({
    url: `/api/user/${userId}`,
    method: 'delete'
  })
}