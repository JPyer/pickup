<template>
    <a-modal
        title="已发现的设备列表"
        :width="880"
        :visible="visible"
        :loading="loading"
        @ok="handleDiscoveryDeviceOk"
        @cancel="() => { $emit('cancel') }"
        :okText="okText"
        :cancelText="cancelText"
      >
      <a-table
        :columns="columns"
        :dataSource="data"
        :pagination="false"
        :loading="loading"
      >
        <template v-for="(col, i) in table_columns" :slot="col" slot-scope="text, record">
          <a-input
            :key="col"
            v-if="record.editable"
            style="margin: -5px 0"
            :value="text"
            :placeholder="columns[i].title"
            @change="e => handleChange(e.target.value, record.key, col)"
          />
          <template v-else>{{ text}}</template>
        </template>

        <template slot="operation" slot-scope="text, record">
          <template v-if="record.editable">
            <span v-if="record.isNew">
              <a @click="saveRow(record)">添加</a>
              <a-divider type="vertical" />
              <a-popconfirm title="是否要删除此行？" @confirm="remove(record.key)">
                <a>删除</a>
              </a-popconfirm>
            </span>
            <span v-else>
              <a @click="saveRow(record)">保存</a>
              <a-divider type="vertical" />
              <a @click="cancel(record.key)">取消</a>
            </span>
          </template>
          <span v-else>
            <a @click="toggle(record.key)">编辑</a>
            <a-divider type="vertical" />
            <a-popconfirm title="是否要移除此行？" @confirm="remove(record.key)">
              <a>移除</a>
            </a-popconfirm>
          </span>
        </template>
      </a-table>
      <a-button
          :loading="memberLoading"
            style="width: 100%; margin-top: 16px; margin-bottom: 8px"
            type="dashed"
            icon="plus"
            @click="newMember"
          :disabled="memberLoading">
          {{ memberLoading && '正在查找' || '继续查找' }}
      </a-button>
   </a-modal>
</template>

<script>
import { STable } from '@/components'
import FooterToolBar from '@/components/FooterToolbar'
import { baseMixin } from '@/store/app-mixin'
import { discoveryDevice, createDevice } from '@/api/device'

export default {
  name: 'DiscoveryDeviceAdvancedForm',
  props: {
    visible: {
        type: Boolean,
        required: true
    },
    loading: {
        type: Boolean,
        default: () => false
    }
  },
  mixins: [baseMixin],
  components: {
    FooterToolBar,
    STable
  },
  data () {
    return {
      memberLoading: false,
      okText: '添加',
      cancelText: '取消',
      data: [],
      // table
      columns: [
       {
          title: '#',
          scopedSlots: { customRender: 'serial' }
        },
        {
          title: '产品ID',
          key: 'product_id',
          dataIndex: 'product_id'
        },
        {
          title: '设备ID',
          key: 'device_id',
          dataIndex: 'device_id',
          width: '15%',
          scopedSlots: { customRender: 'device_id' }
        },
        {
          title: '名称',
          key: 'device_name',
          dataIndex: 'device_name',
          width: '20%',
          scopedSlots: { customRender: 'device_name' }
        },
        {
          title: 'ip',
          key: 'ip_addr',
          dataIndex: 'ip_addr',
          width: '25%'
        },
        {
          title: '固件版本',
          key: 'fw_version',
          dataIndex: 'fw_version',
          width: '11%'
        },
        {
          title: 'mac地址',
          key: 'mac_addr',
          dataIndex: 'mac_addr'
        },
        {
          title: '操作',
          dataIndex: 'operation',
          width: '20%',
          scopedSlots: { customRender: 'operation' }
        }
      ],
      table_columns: ['key', 'product_id', 'device_id', 'fw_version', 'device_name', 'mac_addr', 'ip_addr'],
      // data: [],
      loadData: parameter => {
          console.log('loadData.parameter', parameter)
          if (!this.visible) {
              return
          }
          return self.discovery_device()
      },
      errors: []
    }
  },
   created () {

  },
  computed: {
    rowSelection () {
      return {
        selectedRowKeys: this.selectedRowKeys,
        onChange: this.onSelectChange
      }
    }
  },
  watch: {
      'visible' (val, oldVal) {
          if (val) {
              if (this.data.length === 0) {
                  this.discovery_device()
              }
          }
      }
  },
  methods: {
    handleSubmit (e) {
      e.preventDefault()
    },
    discovery_device () {
      this.memberLoading = true
      discoveryDevice()
          .then(res => {
            this.$message.info(res.message)
            this.memberLoading = false
            this.data = res.data
          }).catch(error => {
          this.$message.error('查找失败:' + error.message)
          this.memberLoading = false
      })
      return this.data
    },
    handleDiscoveryDeviceOk () {
      // 模拟网络请求、卡顿 800ms
      new Promise((resolve, reject) => {
          createDevice({ 'dataset': this.data }).then(res => {
            if (res.code === 200) {
               this.$message.info(res.message)
                this.visible = false
                this.data = []
                 this.$router.go(0)
              } else {
                this.$message.error(` 添加失败:${res.message}`)
            }
              this.loading = false
            }).catch(error => {
                this.loading = false
                reject(error)
            })
      }).then(() => {

      })
    },
    newMember () {
      this.memberLoading = true
      this.discovery_device()
    },
    remove (key) {
      const newData = this.data.filter(item => item.key !== key)
      this.data = newData
    },
    saveRow (record) {
      if (!record.device_id || !record.device_name) {
        this.loading = false
        this.$message.error('请填写完整信息。')
      } else {
        const target = this.data.find(item => item.key === record.key)
        target.editable = false
        target.isNew = false
      }
    },
    toggle (key) {
      const target = this.data.find(item => item.key === key)
      target._originalData = { ...target }
      target.editable = !target.editable
    },
    getRowByKey (key, newData) {
      const data = this.data
      return (newData || data).find(item => item.key === key)
    },
    cancel (key) {
      const target = this.data.find(item => item.key === key)
      Object.keys(target).forEach(key => { target[key] = target._originalData[key] })
      target._originalData = undefined
    },
    handleChange (value, key, column) {
      const newData = [...this.data]
      const target = newData.find(item => key === item.key)
      if (target) {
        target[column] = value
        this.data = newData
      }
    },

    // 最终全页面提交
    validate () {
      const { $refs: { repository, task }, $notification } = this
      const repositoryForm = new Promise((resolve, reject) => {
        repository.form.validateFields((err, values) => {
          if (err) {
            reject(err)
            return
          }
          resolve(values)
        })
      })
      const taskForm = new Promise((resolve, reject) => {
        task.form.validateFields((err, values) => {
          if (err) {
            reject(err)
            return
          }
          resolve(values)
        })
      })

      // clean this.errors
      this.errors = []
      Promise.all([repositoryForm, taskForm]).then(values => {
        $notification['error']({
          message: 'Received values of form:',
          description: JSON.stringify(values)
        })
      }).catch(() => {
        const errors = Object.assign({}, repository.form.getFieldsError(), task.form.getFieldsError())
        const tmp = { ...errors }
        this.errorList(tmp)
      })
    },
    errorList (errors) {
      if (!errors || errors.length === 0) {
        return
      }
      this.errors = Object.keys(errors)
        .filter(key => errors[key])
        .map(key => ({
          key: key,
          message: errors[key][0]
        }))
    },
    scrollToField (fieldKey) {
      const labelNode = document.querySelector(`label[for="${fieldKey}"]`)
      if (labelNode) {
        labelNode.scrollIntoView(true)
      }
    }
  }
}
</script>

<style lang="less" scoped>
  .card{
    margin-bottom: 24px;
  }
  .popover-wrapper {
    /deep/ .antd-pro-pages-forms-style-errorPopover .ant-popover-inner-content {
      min-width: 256px;
      max-height: 290px;
      padding: 0;
      overflow: auto;
    }
  }
  .antd-pro-pages-forms-style-errorIcon {
    user-select: none;
    margin-right: 24px;
    color: #f5222d;
    cursor: pointer;
    i {
          margin-right: 4px;
    }
  }
  .antd-pro-pages-forms-style-errorListItem {
    padding: 8px 16px;
    list-style: none;
    border-bottom: 1px solid #e8e8e8;
    cursor: pointer;
    transition: all .3s;

    &:hover {
      background: #e6f7ff;
    }
    .antd-pro-pages-forms-style-errorIcon {
      float: left;
      margin-top: 4px;
      margin-right: 12px;
      padding-bottom: 22px;
      color: #f5222d;
    }
    .antd-pro-pages-forms-style-errorField {
      margin-top: 2px;
      color: rgba(0,0,0,.45);
      font-size: 12px;
    }
  }
</style>
