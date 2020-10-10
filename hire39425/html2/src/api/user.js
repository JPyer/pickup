import request from '@/utils/request'
import store from '@/store'
const userApi = {
  create: '/api/user',
  edit: '/api/user',
  delete: '/api/user',
  query: '/api/user/list',
  modify_password: '/api/user/password/modify'
}
// 客户
const customerApi = {
  create: '/api/customer',
  edit: '/api/customer',
  delete: '/api/customer',
  query: '/api/customer/list'
}
// 机构
const organizationApi = {
  create: '/api/organization',
  edit: '/api/organization',
  delete: '/api/organization',
  query: '/api/organization/list'
}

// 机构用户
const orgaUserApi = {
  create: '/api/organization/user',
  edit: '/api/organization/user',
  delete: '/api/organization/user',
  query: '/api/organization/user/list'
}

export default userApi

export function getUserList (parameter) {
  let url = null
  const role = store.getters.roles['creatorId']
  switch (role) {
     case 'superadmin':
        url = customerApi.query
        break
     case 'customer_admin':
        url = organizationApi.query
        break
     case 'org_admin':
        url = orgaUserApi.query
        break
     default:
        url = null
  }
  return request({
    url: url,
    method: 'get',
    params: parameter
  })
}
export function createUser (parameter) {
  let url = null
  const role = store.getters.roles['creatorId']
  switch (role) {
     case 'superadmin':
        url = customerApi.create
        break
     case 'customer_admin':
        url = organizationApi.create
        break
     case 'org_admin':
        url = orgaUserApi.create
        break
     default:
        url = null
  }
  if (parameter['role_uid'] === 'org_user') {
     url = orgaUserApi.create
  } else if (parameter['role_uid'] === 'org_admin') {
     url = organizationApi.create
  }

  return request({
    url: url,
    method: 'post',
    data: parameter
  })
}
export function editUser (parameter) {
  let url = null
  const role = store.getters.roles['creatorId']
  switch (role) {
     case 'superadmin':
        url = customerApi.edit
        break
     case 'customer_admin':
        url = organizationApi.edit
        break
     case 'org_admin':
        url = orgaUserApi.edit
        break
     default:
        url = null
  }
  return request({
    url: url,
    method: 'put',
    data: parameter
  })
}
export function deleteUser (parameter) {
  let url = null
  const role = store.getters.roles['creatorId']
  switch (role) {
     case 'superadmin':
        url = customerApi.create
        break
     case 'customer_admin':
        url = organizationApi.create
        break
     case 'org_admin':
        url = orgaUserApi.create
        break
     default:
        url = null
  }
  return request({
    url: url,
    method: 'delete',
    data: parameter
  })
}

export function modifyPassword (parameter) {
  return request({
    url: userApi.modify_password,
    method: 'post',
    data: parameter
  })
}
