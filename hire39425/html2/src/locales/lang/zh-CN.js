import antd from 'ant-design-vue/es/locale-provider/zh_CN'
import momentCN from 'moment/locale/zh-cn'

const components = {
  antLocale: antd,
  momentName: 'zh-cn',
  momentLocale: momentCN
}

const locale = {
  'message': '-',
  'menu.home': '主页',
  'menu.dashboard': '仪表盘',
  'menu.dashboard.analysis': '分析页',
  'menu.dashboard.monitor': '监控页',
  'menu.dashboard.workplace': '工作台',
  'layouts.usermenu.dialog.title': '消息',
  'layouts.usermenu.dialog.content': '确定退出登录？',
  'app.setting.pagestyle': '页面风格设置',
  'app.setting.pagestyle.light': '清新风格',
  'app.setting.pagestyle.dark': '暗黑风格',
  'app.setting.pagestyle.realdark': 'RealDark style',
  'app.setting.themecolor': '主题颜色',
  'app.setting.navigationmode': 'Navigation Mode',
  'app.setting.content-width': 'Content Width',
  'app.setting.fixedheader': '固定头部',
  'app.setting.fixedsidebar': '固定边栏',
  'app.setting.sidemenu': 'Side Menu Layout',
  'app.setting.topmenu': 'Top Menu Layout',
  'app.setting.content-width.fixed': '定宽',
  'app.setting.content-width.fluid': '流式',
  'app.setting.othersettings': '其他设置',
  'app.setting.weakmode': '色弱模式',
  'app.setting.copy': '拷贝配置',
  'app.setting.loading': 'Loading theme',
  'app.setting.copyinfo': 'copy success，please replace defaultSettings in src/models/setting.js',
  'app.setting.production.hint': '重置主题会刷新页面，当前页面内容不会保留，确认重置？'
}

export default {
  ...components,
  ...locale
}
