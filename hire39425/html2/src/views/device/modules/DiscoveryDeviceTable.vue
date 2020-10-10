<template>
      <a-modal
        title="已发现的设备列表"
        :width="820"
        :visible="visible"
        :loading="loading"
        @cancel="() => { $emit('cancel') }"
      >
        <div>
            <div class="table-operator">
              <a-dropdown  v-if="selectedRowKeys.length > 0">
                <a-menu slot="overlay">
                  <a-menu-item key="1"><a-icon type="plus" />添加</a-menu-item>
                  <a-menu-item key="2"><a-icon type="delete" />移除</a-menu-item>
                </a-menu>
                <a-button style="margin-left: 8px">
                  批量操作 <a-icon type="down" />
                </a-button>
              </a-dropdown>
            </div>
            <s-table
              ref="table"
              size="default"
              rowKey="product_id"
              :columns="columns"
              :data="loadData"
               :rowSelection="rowSelection"
            >
              <span slot="serial" slot-scope="text, record, index">
                {{ index + 1 }}
              </span>
              <span slot="action" slot-scope="text, record">
                <template>
                  <a @click="handleEdit(record)">编辑</a>
                  <a-divider type="vertical" />
                </template>
              </span>
            </s-table>
        </div>
    </a-modal>
</template>

<script>
import moment from 'moment'
import { STable } from '@/components'
import { getRoleList } from '@/api/manage'
import { discoveryDevice } from '@/api/device'

export default {
  name: 'DiscoveryDeviceTableList',
  props: {
    visible: {
        type: Boolean,
        required: true
    },
    loading: {
        type: Boolean,
        default: () => false
    },
    data: {
        type: Object,
        required: true
    }
  },
  components: {
    STable
  },
  data () {
    return {
      // 高级搜索 展开/关闭
      advanced: false,
      // 查询参数
      queryParam: {},
      // 表头
      columns: [
        {
          title: '#',
          scopedSlots: { customRender: 'serial' }
        },
        {
          title: '产品ID',
          dataIndex: 'product_id'
        },
        {
          title: '设备ID',
          dataIndex: 'device_id'
        },
        {
          title: '设备名称',
          dataIndex: 'device_name'
        },
        {
          title: 'ip',
          dataIndex: 'ip_addr'
        },
        {
          title: '固件版本',
          dataIndex: 'fw_version'
        },
        {
          title: 'mac地址',
          dataIndex: 'mac_addr',
          needTotal: true
        },
        {
          title: '状态',
          dataIndex: 'err_code',
          needTotal: true
        },
        {
          title: '操作',
          dataIndex: 'action',
          width: '150px',
          scopedSlots: { customRender: 'action' }
        }
      ],
      loadData: parameter => {
          if (!this.visible) {
              return
          }
        return discoveryDevice(Object.assign(parameter, this.queryParam))
          .then(res => {
            this.$message.info(res.message)
            this.loading = false
            return res
          }).catch(error => {
          this.$message.error('查找失败:' + error.message)
          this.loading = false
      })
      },
      selectedRowKeys: [],
      selectedRows: [],

      // custom table alert & rowSelection
      options: {
        alert: { show: true, clear: () => { this.selectedRowKeys = [] } },
        rowSelection: {
          selectedRowKeys: this.selectedRowKeys,
          onChange: this.onSelectChange
        }
      },
      optionAlertShow: false
    }
  },
  created () {
    getRoleList({ t: 'test_table' })
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
    handleEdit (record) {
      this.$emit('onEdit', record)
    },
    handleOk () {

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
    },
    toggle (key) {
      const target = this.data.find(item => item.key === key)
      target._originalData = { ...target }
      target.editable = !target.editable
    }
  }
}
</script>
