import Vue from 'vue'
import moment from 'moment'
import 'moment/locale/zh-cn'
import defaultSettings from '@/config/defaultSettings'
moment.locale('zh-cn')

Vue.filter('NumberFormat', function (value) {
  if (!value) {
    return '0'
  }
  const intPartFormat = value.toString().replace(/(\d)(?=(?:\d{3})+$)/g, '$1,') // 将整数部分逢三一断
  return intPartFormat
})

Vue.filter('dayjs', function (dataStr, pattern = 'YYYY-MM-DD HH:mm:ss') {
  return moment(dataStr).format(pattern)
})

Vue.filter('moment', function (dataStr, pattern = 'YYYY-MM-DD HH:mm:ss') {
  return moment(dataStr).format(pattern)
})

Vue.filter('statusFilter', function (type) {
   return defaultSettings.statusMap[type] ? defaultSettings.statusMap[type].text : ''
})
Vue.filter('statusTypeFilter', function (type) {
   return defaultSettings.statusMap[type] ? defaultSettings.statusMap[type].text : ''
})
Vue.filter('deviceErrorCodeFilter', function (type) {
   return defaultSettings.errorCodeMap[type] ? defaultSettings.errorCodeMap[type].text : ''
})
Vue.filter('accountStatusFilter', function (type) {
   return defaultSettings.accountStatusMap[type] ? defaultSettings.accountStatusMap[type].text : ''
})
Vue.filter('roleFilter', function (type) {
   return defaultSettings.roleMap[type] ? defaultSettings.roleMap[type].text : ''
})
