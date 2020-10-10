import request from '@/utils/request'
// import api from "@/api/manage"

const deviceApi = {
  create: '/api/device',
  edit: '/api/device',
  delete: '/api/device',
  device_list: '/api/device/list',
  option: '/api/device/option',
  device_discovery: '/api/device/discovery',
  audio_channel_info: '/api/device/audio/channel',
  audio_set: '/api/device/audio'
}
const deviceGroupApi = {
  option: '/api/device/group/option',
  create: '/api/device/group',
  edit: '/api/device/group',
  delete: '/api/device/group',
  query: '/api/device/group/list'
}

export default deviceApi

export function createDevice (parameter) {
  return request({
    url: deviceApi.create,
    method: 'post',
    data: parameter
  })
}
export function editDevice (parameter) {
  return request({
    url: deviceApi.edit,
    method: 'put',
    data: parameter
  })
}
export function deleteDevice (parameter) {
  return request({
    url: deviceApi.delete,
    method: 'delete',
    data: parameter
  })
}
export function getDeviceList (parameter) {
  return request({
    url: deviceApi.device_list,
    method: 'get',
    params: parameter
  })
}
export function discoveryDevice (parameter) {
  return request({
    url: deviceApi.device_discovery,
    method: 'get',
    params: parameter
  })
}
export function getDeviceGroupList (parameter) {
  return request({
    url: deviceGroupApi.query,
    method: 'get',
    params: parameter
  })
}
export function createDeviceGroup (parameter) {
  return request({
    url: deviceGroupApi.create,
    method: 'post',
    data: parameter
  })
}
export function editDeviceGroup (parameter) {
  return request({
    url: deviceGroupApi.edit,
    method: 'put',
    data: parameter
  })
}
export function deleteDeviceGroup (parameter) {
  return request({
    url: deviceGroupApi.delete,
    method: 'delete',
    data: parameter
  })
}
export function getDeviceGroupOption (parameter) {
  return request({
    url: deviceGroupApi.option,
    method: 'get',
    params: parameter
  })
}

export function getDeviceOption (parameter) {
  return request({
    url: deviceApi.option,
    method: 'get',
    params: parameter
  })
}
export function getDeviceAudioChannelInfo (parameter) {
  return request({
    url: deviceApi.audio_channel_info,
    method: 'get',
    params: parameter
  })
}

export function updateDeviceAudioChannelInfo (parameter) {
  return request({
    url: deviceApi.audio_channel_info,
    method: 'put',
    data: parameter
  })
}
export function getDeviceAudioSetting (parameter) {
  return request({
    url: deviceApi.audio_set,
    method: 'get',
    params: parameter
  })
}
export function updateDeviceAudioSetting (parameter) {
  return request({
    url: deviceApi.audio_set,
    method: 'put',
    data: parameter
  })
}
