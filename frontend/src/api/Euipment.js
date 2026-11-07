import  request  from '../utils/request.js'
export function get_equipment_list(params) {
  return request({
    method: 'GET',
    url: '/api/equipment/list',
    params
  })
}
export function create_equipment(data) {
  return request({
    method: 'POST',
    url: '/api/equipment',
    data
  })
}
export function update_equipment(equ_id,data) {
  return request({
    method: 'PUT',
    url: `/api/equipment/${equ_id}`,
    data
  })
}
export function delete_equipment(equ_id) {
  return request({
    method: 'DELETE',
    url: `/api/equipment/${equ_id}`,
  })
}