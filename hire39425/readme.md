### 开发笔记
前端：
- https://preview.pro.ant.design/
- github https://github.com/ant-design/ant-design-pro   
- github https://github.com/vueComponent/ant-design-vue-pro/blob/master/README.zh-CN.md
- 使用文档：http://pro.ant.design/docs/getting-started-cn

github:https://github.com/iczer/vue-antd-admin

#### 1.model同步

python38 manage.py startapp $name
python38 manage.py makemigrations $name
python38 manage.py migrate device --database=$db

auth,session
#### 2.跨域访问
# csrf_exempt 测试阶段使用
#### 3.多个数据库联用时数据导入导出
python38 manage.py dumpdata app1 --database=db1 > app1_fixture.json
python manage.py dumpdata auth > auth_fixture.json
python manage.py loaddata app1_fixture.json --database=db1
python manage.py loaddata app2_fixture.json --database=db2
#### 4. 修改api server
templates/src/services/api.js
#### 5.修改前端表单权限
~~v-auth:role 表示通过 role.operation 进行校验，v-auth:permission 表示通过 permission.operation 进行校验。~~

获取用户信息：GetInfo (html/src/store/modules/user.js)
修改系统标题：html/src/config/defaultSettings.js
缓存用户信息：html/src/store/modules/user.js
#### 6.前端登录逻辑
- html/src/store/modules/user.js

#### 7.音频播放
google浏览器现在已不允许音视频自动播放
#### 8.eslint 常用规范
"no-console": "error", 　　　　　　　　　　　　　　　　 // 禁止console
"no-alert": "error", 　　　　　　　　　　　　　　　　　 // 禁止alert,conirm等
"no-debugger": "error", 　　　　　　　　　　　　　　　 // 禁止debugger
"semi": ["error", "never"],　　　　　　　　　　　　   // 禁止分号
"no-tabs": "error", 　　　　　　　　　　　　　　　　　　// 禁止使用tab
"no-unreachable": "error", 　　　　　　　　　　　　　　// 当有不能执行到的代码时
"eol-last": "error", 　　　　　　　　　　　　　　　　　　// 文件末尾强制换行
"no-new": "error",　　　　　　　　　　　　　　　　　　　 // 禁止在使用new构造一个实例后不赋值
"quotes": ["error", "backtick"], 　　　　　　　　　　 // 引号类型 `` "" ''
"no-unused-vars": ["error", { "vars": "all", "args": "after-used" }], 　　// 不能有声明后未被使用的变量
"no-trailing-spaces": "error", 　　　　　　　　　　　　// 一行结束后面不要有空格
"space-before-function-paren": ["error", "never"], // 函数定义时括号前面要不要有空格
"no-undef": "error", 　　　　　　　　　　　　　　　　　　// 不能有未定义的变量,定义之前必须有var或者let
"curly": ["error", "all"], 　　　　　　　　　　　　　　 // 必须使用 if(){} 中的{}
'arrow-parens': "error", 　　　　　　　　　　　　　　　　// 箭头函数的参数要有()包裹
'generator-star-spacing': "error", 　　　　　　　　　　// allow async-await
"space-before-function-paren": ["error", "never"],  // 禁止函数名前有空格，如function Test (aaa,bbb)
"space-in-parens": ["error", "never"], 　　　　　　　　// 禁止圆括号有空格，如Test( 2, 3 )
"space-infix-ops": "error", 　　　　　　　　　　　　　　//在操作符旁边必须有空格， 如 a + b而不是a+b
"space-before-blocks": ["error", "always"], 　　　　　// 语句块之前必须有空格 如 ) {}
"spaced-comment":["error", "always"], 　　　　　　　　// 注释前必须有空格
"arrow-body-style": ["error", "always"], 　　　　　　// 要求箭头函数必须有大括号 如 a => {}
"arrow-parens": ["error", "always"], 　　　　　　　　//要求箭头函数的参数必有用括弧包住，如(a) =>{}
"arrow-spacing": ["error", { "before": true, "after": true }], // 定义箭头函数的箭头前后都必须有空格
"no-const-assign": "error",  　　　　　　　　　　　　  // 禁止修改const变量
"template-curly-spacing": ["error", "never"], 　　// 禁止末班字符串中的{}中的变量出现空格，如以下错误`${ a }`
"no-multi-spaces": "error", 　　　　　　　　　　　　// 禁止多个空格，只有一个空格的地方必须只有一个
"no-whitespace-before-property": "error", 　　　　// 禁止属性前有空格，如obj. a
"keyword-spacing":["error",{"before": true, "after": true}]　　 //关键字前后必须有空格 如 } else {
#### 9.频谱图/声波图绘制
https://www.cnblogs.com/Wayou/p/html5_audio_api_visualizer.html
#### 10.首页html
html/public/index.html