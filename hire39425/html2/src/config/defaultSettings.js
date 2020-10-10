/**
 * 项目默认配置项
 * primaryColor - 默认主题色, 如果修改颜色不生效，请清理 localStorage
 * navTheme - sidebar theme ['dark', 'light'] 两种主题
 * colorWeak - 色盲模式
 * layout - 整体布局方式 ['sidemenu', 'topmenu'] 两种布局
 * fixedHeader - 固定 Header : boolean
 * fixSiderbar - 固定左侧菜单栏 ： boolean
 * contentWidth - 内容区布局： 流式 |  固定
 *
 * storageOptions: {} - Vue-ls 插件配置项 (localStorage/sessionStorage)
 *
 */

export default {
  navTheme: 'dark', // theme for nav menu
  primaryColor: '#52C41A', // primary color of ant design
  layout: 'sidemenu', // nav menu position: `sidemenu` or `topmenu`
  contentWidth: 'Fluid', // layout of content: `Fluid` or `Fixed`, only works when layout is topmenu
  fixedHeader: false, // sticky header
  fixSiderbar: false, // sticky siderbar
  colorWeak: false,
  menu: {
    locale: true
  },
  title: 'Sg设备管理系统',
  pwa: false,
  iconfontUrl: '',
  production: process.env.NODE_ENV === 'production' && process.env.VUE_APP_PREVIEW !== 'true',
  baseUrl: 'http://localhost:8000',
  statusMap: {
      0: {
        status: 'default',
        text: '关闭'
      },
      1: {
        status: 'processing',
        text: '运行中'
      },
      2: {
        status: 'success',
        text: '录音中'
      },
      3: {
        status: 'error',
        text: '异常'
      }
  },
  errorCodeMap: {
      0: {
        status: 0,
        text: '正常'
      },
      1: {
        status: 1,
        text: '错误'
      }
  },
  accountStatusMap: {
      false: {
        status: false,
        text: '禁用'
      },
      true: {
        status: true,
        text: '启用'
      }
  },
  roleMap: {
      'org_admin': {
        value: 'org_admin',
        text: '机构管理员'
      },
      'org_user': {
        value: 'org_user',
        text: '机构子用户'
      }
  }
}
