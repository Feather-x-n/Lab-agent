import  request  from '../utils/request.js'
//获取实验室列表
export function getLabList(params) {
  return request({
    url: `/api/lab/list`,
    method: 'get',
    params,
  })
}
//创建新实验室
export function createLabApi(data){
  return request({
    url: `/api/lab`,
    method: 'post',
    data,
  })
}
//修改实验室信息
export function updateLabApi(lab_id,data){
  return request({
    url: `/api/lab/${lab_id}`,
    method: 'put',
    data,
  })
}
//删除实验室信息
export function deleteLab(lab_id){
  return request({
    url: `/api/lab/${lab_id}`,
    method: 'delete',
  })
}
/**
 * 根据ID查询实验室详情
 * @param {Number} lab_id
 * @returns
 */
export function getLab(lab_id) {
  return request({
    url: `/api/lab/${lab_id}`,
    method: 'get'
  })
}