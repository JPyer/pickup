<template>
  <page-header-wrapper>
    <a-card :bordered="false">
      <div class="table-page-search-wrapper">
        <a-form layout="inline">
          <a-row :gutter="48">
             <a-col :md="8" :sm="24">
              <a-form-item label="组名">
                  <a-input  v-model="queryParam.name" placeholder="组名"/>
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

        <span slot="description" slot-scope="text">
          <ellipsis :length="4" tooltip>{{ text }}</ellipsis>
        </span>

        <span slot="action" slot-scope="text, record">
          <template>
            <a @click="handleEdit(record)">修改</a>
            <a-divider type="vertical" />

            <a-popconfirm title="是否要删除该分组？" @confirm="delete_group(record.id)">
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
import { getDeviceGroupList, deleteDeviceGroup, createDeviceGroup, editDeviceGroup } from '@/api/device'

import CreateForm from './modules/DeviceGroupCreateForm'

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
    title: '组名',
    dataIndex: 'name'
  },
  {
    title: '设备数',
    dataIndex: 'device_count',
    sorter: true,
    needTotal: true,
    customRender: (text) => text + '个'
  },
  {
    title: '操作',
    dataIndex: 'action',
    width: '150px',
    scopedSlots: { customRender: 'action' }
  }
]

export default {
  name: 'DeviceGroupList',
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
        return getDeviceGroupList(requestParameters)
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
                    editDeviceGroup(values).then(res => {
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
                     createDeviceGroup(values).then(res => {
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
    delete_group (key) {
        console.log(this.data)
        // const newData = this.data.filter(item => item.device_id !== key)
        // this.data = newData
        this.loading = true
        new Promise((resolve, reject) => {
            deleteDeviceGroup(key).then(res => {
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
