import request from '@/utils/request'
// import api from "@/api/manage"

const audioApi = {
  edit: '/api/audio',
  delete: '/api/audio',
  open: '/api/audio/channel/open',
  close: '/api/audio/channel/close',
  audio_list: '/api/audio/list',
  play: '/api/audio/play'
}

export function editAudio (parameter) {
  return request({
    url: audioApi.edit,
    method: 'put',
    data: parameter
  })
}
export function deleteAudio (parameter) {
  return request({
    url: audioApi.delete,
    method: 'delete',
    data: parameter
  })
}
export function getAudioList (parameter) {
  return request({
    url: audioApi.audio_list,
    method: 'get',
    params: parameter
  })
}
export function openAudio (parameter) {
  return request({
    url: audioApi.open,
    method: 'post',
    data: parameter
  })
}
export function closeAudio (parameter) {
  return request({
    url: audioApi.close,
    method: 'post',
    data: parameter
  })
}
export function playAudio (parameter) {
  return request({
    url: audioApi.play,
    method: 'get',
    params: parameter,
    responseType: 'arraybuffer' // 后台返回的为语音的流数据
    // responseType: "arraybuffer" // 后台返回的为语音的流数据
  })
}

export default {
  audioApi,
  editAudio,
  openAudio,
  closeAudio,
  getAudioList,
  deleteAudio,
  playAudio
}
