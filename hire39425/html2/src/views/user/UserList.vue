<template>
  <page-header-wrapper>
    <a-card :bordered="false">
      <div class="table-page-search-wrapper">
        <a-form layout="inline">
          <a-row :gutter="48">
             <a-col :md="8" :sm="24">
              <a-form-item label="用户名">
                <a-select v-model="queryParam.username" placeholder="全部" default-value="">
                  <a-select-option value="">全部</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>

            <a-col :md="!advanced && 8 || 24" :sm="24">
              <span class="table-page-search-submitButtons" :style="advanced && { float: 'right', overflow: 'hidden' } || {} ">
                <a-button type="primary" @click="$refs.table.refresh(true)">查询</a-button>
                <a-button style="margin-left: 8px" @click="() => this.queryParam = {}">重置</a-button>
              </span>
            </a-col>
          </a-row>
        </a-form>
      </div>

      <div class="table-operator">
        <a-button type="primary" icon="plus" @click="handleAdd">新建</a-button>
      </div>

      <s-table
        ref="table"
        size="default"
        rowKey="key"
        :columns="columns"
        :data="loadData"
        :alert="true"
        :rowSelection="rowSelection"
        showPagination="auto"
      >
        <span slot="serial" slot-scope="text, record, index">
          {{ index + 1 }}
        </span>

        <span slot="role_uid" slot-scope="text">
          <ellipsis :length="10" tooltip>{{ text | roleFilter }}</ellipsis>
        </span>
        <span slot="is_active" slot-scope="text">
          <ellipsis :length="4" tooltip>{{ text | accountStatusFilter }}</ellipsis>
        </span>

        <span slot="action" slot-scope="text, record">
          <template>
            <a @click="handleEdit(record)">修改</a>
            <a-divider type="vertical" />

            <a-popconfirm title="是否确认删除？一旦删除不可恢复" @confirm="delete_user(record.id)">
               <a style="color:red">删除</a>
            </a-popconfirm>
          </template>
        </span>
      </s-table>

      <create-form
        ref="createModal"
        :visible="visible"
        :loading="confirmLoading"
        :model="mdl"
        @cancel="handleCancel"
        @ok="handleOk"
      />
    </a-card>
  </page-header-wrapper>
</template>

<script>
import moment from 'moment'
import { STable, Ellipsis } from '@/components'
import { getRoleList } from '@/api/manage'
import { getUserList, deleteUser, createUser, editUser } from '@/api/user'

import CreateForm from './modules/UserCreateForm'

const columns = [
  {
    title: '#',
    scopedSlots: { customRender: 'serial' }
  },
  {
    title: 'ID',
    dataIndex: 'id'
  },
  {
    title: '用户名',
    dataIndex: 'username'
  },
   {
    title: '角色',
    dataIndex: 'role_uid',
    scopedSlots: { customRender: 'role_uid' }
  },
  {
    title: '联系方式',
    dataIndex: 'telephone'
  },
  {
    title: '创建时间',
    dataIndex: 'date_joined'
  },
  {
    title: '上次登录',
    dataIndex: 'last_login'
  },
  {
    title: '状态',
    dataIndex: 'is_active',
    scopedSlots: { customRender: 'is_active' }
  },
  {
    title: '操作',
    dataIndex: 'action',
    width: '150px',
    scopedSlots: { customRender: 'action' }
  }
]

export default {
  name: 'UserList',
  components: {
    STable,
    Ellipsis,
    CreateForm
  },
  data () {
    this.columns = columns
    return {
      // create model
      visible: false,
      confirmLoading: false,
      mdl: null,
      // 高级搜索 展开/关闭
      advanced: false,
      // 查询参数
      queryParam: {},
      // 加载数据方法 必须为 Promise 对象
      loadData: parameter => {
        const requestParameters = Object.assign({}, parameter, this.queryParam)
        return getUserList(requestParameters)
          .then(res => {
            return res
          })
      },
      selectedRowKeys: [],
      selectedRows: []
    }
  },
  filters: {

  },
  created () {
    getRoleList({ t: new Date() })
  },
  computed: {
    rowSelection () {
      return {
        selectedRowKeys: this.selectedRowKeys,
        onChange: this.onSelectChange
      }
    }
  },
  methods: {
    handleAdd () {
      this.mdl = null
      this.visible = true
    },
    handleEdit (record) {
      this.visible = true
      this.mdl = { ...record }
    },
    handleOk () {
      const form = this.$refs.createModal.form
      this.confirmLoading = true
      form.validateFields((errors, values) => {
        if (!errors) {
          console.log('values', values)
            // 修改 e.g.
            new Promise((resolve, reject) => {
                if (values.id > 0) {
                    editUser(values).then(res => {
                          // 重置表单数据
                          if (res.code === 200) {
                              this.$message.info(res.message)
                              form.resetFields()
                              this.visible = false
                              this.confirmLoading = false
                              // 刷新表格
                              this.$refs.table.refresh()
                          }
                    }).catch(error => {
                        this.confirmLoading = false
                        reject(error)
                    })
               } else {
                     createUser(values).then(res => {
                          // 重置表单数据
                          if (res.code === 200) {
                              this.$message.info(res.message)
                              form.resetFields()
                              this.visible = false
                              this.confirmLoading = false
                              // 刷新表格
                              this.$refs.table.refresh()
                          } else {
                               this.confirmLoading = false
                            this.$message.error(res.message)
                        }
                }).catch(error => {
                    this.confirmLoading = false
                     this.$message.error('请求失败')
                     reject(error)
                })
                }
            }).then()
        } else {
          this.confirmLoading = false
        }
      })
    },
    handleCancel () {
      this.visible = false
      const form = this.$refs.createModal.form
      form.resetFields() // 清理表单数据（可不做）
    },
    delete_user (key) {
        console.log(this.data)
        // const newData = this.data.filter(item => item.device_id !== key)
        // this.data = newData
        this.loading = true
        new Promise((resolve, reject) => {
            deleteUser(key).then(res => {
                  if (res.code === 200) {
                      this.$message.info(res.message)
                      // 刷新表格
                      this.$refs.table.refresh()
                  }
            }).catch(error => {
                this.loading = false
                reject(error)
            })
        }).then()
    },
    onSelectChange (selectedRowKeys, selectedRows) {
      this.selectedRowKeys = selectedRowKeys
      this.selectedRows = selectedRows
    },
    toggleAdvanced () {
      this.advanced = !this.advanced
    },
    resetSearchForm () {
      this.queryParam = {
        date: moment(new Date())
      }
    }
  }
}
</script>
