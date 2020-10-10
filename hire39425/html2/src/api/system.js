import request from '@/utils/request'

const systemApi = {
  info: '/api/system/info'

}
export function systemInfo (parameter) {
  return request({
    url: systemApi.info,
    method: 'get',
    params: parameter
  })
}

export default {
  systemInfo
}
