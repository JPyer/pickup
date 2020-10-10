// eslint-disable-next-line
import { UserLayout, BasicLayout, BlankLayout } from '@/layouts'
import { bxAnaalyse } from '@/core/icons'

const RouteView = {
  name: 'RouteView',
  render: (h) => h('router-view')
}

export const asyncRouterMap = [

  {
    path: '/',
    name: 'index',
    component: BasicLayout,
    meta: { title: 'menu.home' },
    redirect: '/dashboard/workplace',
    children: [
      // dashboard
      {
        path: '/dashboard',
        name: 'dashboard',
        redirect: '/dashboard/workplace',
        component: RouteView,
        meta: { title: '仪表盘', keepAlive: true, icon: bxAnaalyse, permission: [ 'dashboard' ] },
        children: [
          {
            path: '/dashboard/analysis/:pageNo([1-9]\\d*)?',
            name: 'Analysis',
            component: () => import('@/views/dashboard/Analysis'),
            hidden: true,
            meta: { title: '分析页', keepAlive: false, permission: [ 'dashboard' ] }
          },
          {
            path: '/dashboard/workplace',
            name: 'Workplace',
            component: () => import('@/views/dashboard/Workplace'),
            meta: { title: '工作台', keepAlive: true, permission: [ 'dashboard' ] }
          }
        ]
      },
       {
        path: '/customer',
        name: 'customer',
        component: RouteView,
        redirect: '/list/table-list',
        meta: { title: '客户管理', icon: 'user', permission: [ 'customer' ] },
        children: [
          {
            path: '/customer/list/:pageNo([1-9]\\d*)?',
            name: 'TableListWrapper',
            hideChildrenInMenu: true,
            component: () => import('@/views/customer/CustomerList'),
            meta: { title: '客户列表', keepAlive: true, permission: [ 'customer' ] }
          }
        ]
      },
       {
        path: '/organization',
        name: 'organization',
        component: RouteView,
        redirect: '/list/table-list',
        meta: { title: '机构管理', icon: 'user', permission: [ 'org' ] },
        children: [
          {
            path: '/organization/list/:pageNo([1-9]\\d*)?',
            name: 'TableListWrapper',
            hideChildrenInMenu: true,
            component: () => import('@/views/user/UserList'),
            meta: { title: '机构列表', keepAlive: true, permission: [ 'org' ] }
          },
          {
                path: '/organization/user/permission-list',
                name: 'UserPermissionList',
                component: () => import('@/views/other/UserList'),
                meta: { title: '权限管理', keepAlive: true }
         }
        ]
      },
      {
        path: '/device',
        name: 'device',
        component: RouteView,
        redirect: '/list/table-list',
        meta: { title: '设备管理', icon: 'table', permission: [ 'device' ] },
        children: [
          {
            path: '/device/list/:pageNo([1-9]\\d*)?',
            name: 'device_list',
            hideChildrenInMenu: true, // 强制显示 MenuItem 而不是 SubMenu
            component: () => import('@/views/device/DeviceList'),
            meta: { title: '设备列表', keepAlive: true, permission: [ 'device' ] }
          },
          {
            path: '/device/group/list',
            name: 'device_group_list',
            component: () => import('@/views/device/DeviceGroupList'),
            meta: { title: '设备分组', keepAlive: true, permission: [ 'device_group' ] }
          }
        ]
      },
      {
        path: '/audio',
        name: 'audio',
        component: RouteView,
        redirect: '/list/table-list',
        meta: { title: '音频管理', icon: 'audio', permission: [ 'audio' ] },
        children: [
          {
            path: '/audio/list',
            name: 'AudioList',
            hideChildrenInMenu: true,
            component: () => import('@/views/audio/AudioList'),
            meta: { title: '音频列表', keepAlive: true, permission: [ 'audio' ] }
          }
        ]
      },
      {
        path: '/system',
        name: 'systemPage',
        component: RouteView,
        meta: { title: '系统管理', icon: 'slack', permission: [ 'audio' ] },
        redirect: '/other/icon-selector',
        children: [
              {
                path: '/system/role-list',
                name: 'RoleList',
                hidden: true,
                component: () => import('@/views/other/UserList'),
                meta: { title: '角色管理', keepAlive: true }
              },
              {
                path: '/other/list/permission-list',
                name: 'PermissionList',
                hidden: true,
                component: () => import('@/views/other/PermissionList'),
                meta: { title: '权限列表', keepAlive: true }
              }
            ]
      },
      // result
      {
        path: '/result',
        name: 'result',
        component: RouteView,
        redirect: '/result/success',
        hidden: true,
        meta: { title: '结果页', icon: 'check-circle-o', permission: [ 'result' ] },
        children: [
          {
            path: '/result/success',
            name: 'ResultSuccess',
            component: () => import(/* webpackChunkName: "result" */ '@/views/result/Success'),
            meta: { title: '成功', keepAlive: false, hiddenHeaderContent: true, permission: [ 'result' ] }
          },
          {
            path: '/result/fail',
            name: 'ResultFail',
            component: () => import(/* webpackChunkName: "result" */ '@/views/result/Error'),
            meta: { title: '失败', keepAlive: false, hiddenHeaderContent: true, permission: [ 'result' ] }
          }
        ]
      },
      // Exception
      {
        path: '/exception',
        name: 'exception',
        component: RouteView,
        redirect: '/exception/403',
        hidden: true,
        meta: { title: '异常页', icon: 'warning', permission: [ 'exception' ] },
        children: [
          {
            path: '/exception/403',
            name: 'Exception403',
            component: () => import(/* webpackChunkName: "fail" */ '@/views/exception/403'),
            meta: { title: '403', permission: [ 'exception' ] }
          },
          {
            path: '/exception/404',
            name: 'Exception404',
            component: () => import(/* webpackChunkName: "fail" */ '@/views/exception/404'),
            meta: { title: '404', permission: [ 'exception' ] }
          },
          {
            path: '/exception/500',
            name: 'Exception500',
            component: () => import(/* webpackChunkName: "fail" */ '@/views/exception/500'),
            meta: { title: '500', permission: [ 'exception' ] }
          }
        ]
      },
      // account
      {
        path: '/account/settings',
        name: 'settings',
        component: () => import('@/views/account/settings/Index'),
        meta: { title: '个人中心', icon: 'user', hideHeader: true },
        redirect: '/account/settings/base',
        hideChildrenInMenu: true,
        children: [
              {
                path: '/account/settings/base',
                name: 'BaseSettings',
                component: () => import('@/views/account/settings/BaseSetting'),
                meta: { title: '基本信息', hidden: true }
              },
              {
                path: '/account/settings/security',
                name: 'SecuritySettings',
                component: () => import('@/views/account/settings/Security'),
                meta: { title: '安全设置', hidden: true, keepAlive: true }
              },
              {
                path: '/account/settings/password',
                name: 'PasswordSettings',
                component: () => import('@/views/account/settings/PasswordSecurity'),
                meta: { title: '密码设置', hidden: true, keepAlive: true }
              },
              {
                path: '/account/settings/custom',
                name: 'CustomSettings',
                component: () => import('@/views/account/settings/Custom'),
                meta: { title: '个性化设置', hidden: true, keepAlive: true }
              },
              {
                path: '/account/settings/binding',
                name: 'BindingSettings',
                component: () => import('@/views/account/settings/Binding'),
                meta: { title: '账户绑定', hidden: true, keepAlive: true }
              },
              {
                path: '/account/settings/notification',
                name: 'NotificationSettings',
                component: () => import('@/views/account/settings/Notification'),
                meta: { title: '新消息通知', hidden: true, keepAlive: true }
              }
              ]
      }
    ]
  },
  {
    path: '*', redirect: '/404', hidden: true
  }
]

/**
 * 基础路由
 * @type { *[] }
 */
export const constantRouterMap = [
  {
    path: '/user',
    component: UserLayout,
    redirect: '/user/login',
    hidden: true,
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import(/* webpackChunkName: "user" */ '@/views/user/Login')
      },
      {
        path: 'register',
        name: 'register',
        component: () => import(/* webpackChunkName: "user" */ '@/views/user/Register')
      },
      {
        path: 'register-result',
        name: 'registerResult',
        component: () => import(/* webpackChunkName: "user" */ '@/views/user/RegisterResult')
      },
      {
        path: 'recover',
        name: 'recover',
        component: undefined
      }
    ]
  },

  {
    path: '/404',
    component: () => import(/* webpackChunkName: "fail" */ '@/views/exception/404')
  }

]
