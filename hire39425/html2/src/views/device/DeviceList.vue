<template>
  <page-header-wrapper>
    <a-card :bordered="false">
      <div class="table-page-search-wrapper">
        <a-form layout="inline">
          <a-row :gutter="48">
            <a-col :md="5" :sm="16">
              <a-form-item label="设备ID">
                <a-input-number v-model="queryParam.id" placeholder=""/>
              </a-form-item>
            </a-col>
            <a-col :md="8" :sm="16">
              <a-form-item label="设备名称">
                <a-input v-model="queryParam.device_name" placeholder=""/>
              </a-form-item>
            </a-col>
            <a-col :md="5" :sm="7">
              <a-form-item label="使用状态">
                <a-select v-model="queryParam.status" placeholder="全部" default-value="">
                  <a-select-option value="">全部</a-select-option>
                  <a-select-option value="0">关闭</a-select-option>
                  <a-select-option value="1">运行中</a-select-option>
                  <a-select-option value="2">录音中</a-select-option>
                  <a-select-option value="3">异常</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :md="6" :sm="16">
              <a-form-item label="分组">
                <a-select v-model="queryParam.group_id" placeholder="全部" default-value="">
                  <a-select-option value="" >全部</a-select-option>
                  <a-select-option v-for="option in groupOptions" :key="option.id" :value="option.id">
                    {{option.name}}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <template v-if="advanced">
              <a-col :md="8" :sm="24">
                <a-form-item label="更新日期">
                  <a-date-picker v-model="queryParam.date" style="width: 100%" placeholder="请输入更新日期"/>
                </a-form-item>
              </a-col>
            </template>
            <a-col :md="!advanced && 8 || 24" :sm="24">
              <span class="table-page-search-submitButtons" :style="advanced && { float: 'right', overflow: 'hidden' } || {} ">
                <a-button type="primary" @click="$refs.table.refresh(true)">查询</a-button>
                <a-button style="margin-left: 8px" @click="() => this.queryParam = {}">重置</a-button>
                <a @click="toggleAdvanced" style="margin-left: 8px">
                  {{ advanced ? '收起' : '展开' }}
                  <a-icon :type="advanced ? 'up' : 'down'"/>
                </a>
              </span>
            </a-col>
          </a-row>
        </a-form>
      </div>
      <div class="table-operator">
        <a-button type="primary" icon="plus" @click="handleAdd">新建</a-button>
        <a-button type="info" icon="search" @click="handleDiscovery" :loading="discovery_loading">
            网络查找
        </a-button>
        <a-dropdown>
          <a-menu slot="overlay">
            <a-menu-item key="1" @click="batchOpenAudio"><a-icon type="audio"  />开启录音</a-menu-item>
            <a-menu-item key="2" @click="batchCloseAudio"><a-icon type="stop" />停止录音</a-menu-item>
          </a-menu>
          <a-button style="margin-left: 8px">
            批量操作 <a-icon type="down" />
          </a-button>
        </a-dropdown>
      </div>

      <s-table
        ref="table"
        size="default"
        rowKey="id"
        :columns="columns"
        :dataSource="data"
        :data="loadData"
        :alert="true"
        :rowSelection="rowSelection"
        showPagination="auto"
      >
        <span slot="serial" slot-scope="text, record, index">
          {{ index + 1 }}
        </span>
        <span slot="status" slot-scope="text">
          <a-badge :status="text | statusTypeFilter" :text="text | statusFilter" />
        </span>
        <span slot="description" slot-scope="text">
          <ellipsis :length="4" tooltip>{{ text }}</ellipsis>
        </span>

        <span slot="action" slot-scope="text, record">
          <template>
             <div slot="actions">
               <a-popconfirm
                   :title="record.status === 2 ? '确认关闭录音？' : '确认开始录音？'"
                   :disabled="record.status === 0"
                    @confirm="handleAudioRecord($event,record.id)">
                   <a-button
                        :loading="record.loading"
                       :disabled="record.status === 0 "
                       ref='record_btn'
                       size="small"
                       :type="record.status === 2 ? 'danger' : 'primary'"
                       >
                       <a-icon :type="record.status === 2 ? 'stop' : 'audio' "  />
                   </a-button>
                </a-popconfirm>
               <a-divider type="vertical" />

               <a-dropdown>
                <a-menu slot="overlay">
                    <a-menu-item width="200px">
                     <a @click="handleEdit(record)">  <a-icon type="setting" />设备配置</a>
                    <a @click="handleAudioSet(record.id)"> <a-icon type="audio" />音频参数</a>
                    <a @click="handleAudioChannelEdit(record.id)"> <a-icon type="notification" />音频通道</a>
                    <a-popconfirm title="警告！是否要删除该设备(运行中请先关闭)？" @confirm="delete_device(record.id)">
                          <a style="color:red"> <a-icon type="delete" />删除设备</a>
                    </a-popconfirm>
                    </a-menu-item>
                </a-menu>
                <a>更多<a-icon type="down"/></a>
                </a-dropdown>
             </div>
          </template>
        </span>
      </s-table>

      <device-info-form
        ref="createModal"
        :visible="visible"
        :loading="confirmLoading"
        :model="mdl"
        :options="groupOptions"
        @cancel="handleCancel"
        @ok="handleOk"
      />
      <discovery-device-advanced-table
       ref="discoveryAdvancedDeviceModal"
       :visible="discovery_form_visible"
        :loading="discovery_loading"
       :data="discovery_device_list"
        @cancel="handleDiscoveryCancel"
      />
       <device-audio-channel-edit-form
        ref="deviceAudioChannelModal"
        :visible="channel_visible"
        :loading="channelConfirmLoading"
        :model="channel_mdl"
        @cancel="handleChannelCancel"
        @ok="handleChannelOk"
       />
        <device-audio-set-form
        ref="deviceAudioSetModal"
        :visible="audio_set_visible"
        :loading="audioSettingConfirmLoading"
        :model="audio_set_mdl"
        @cancel="handleAudioSettingCancel"
        @ok="handleAudioSettingOk"
       />

    </a-card>
  </page-header-wrapper>
</template>

<script>
import moment from 'moment'
import { STable, Ellipsis } from '@/components'
import {
    createDevice,
    editDevice,
    getDeviceList,
    getDeviceGroupOption,
    deleteDevice,
    getDeviceAudioChannelInfo,
    updateDeviceAudioChannelInfo,
    getDeviceAudioSetting,
    updateDeviceAudioSetting
} from '@/api/device'
import { openAudio, closeAudio } from '@/api/audio'
import DeviceInfoForm from './modules/DeviceInfoForm'
import DiscoveryDeviceTable from './modules/DiscoveryDeviceTable'
import DiscoveryDeviceAdvancedTable from './modules/DiscoveryDeviceAdvancedForm'
import DeviceAudioChannelEditForm from './modules/DeviceAudioChannelEditForm'
import DeviceAudioSetForm from './modules/DeviceAudioSetForm'

const columns = [
  {
    title: '#',
    scopedSlots: { customRender: 'serial' }
  },
  {
    title: 'ID',
    dataIndex: 'id',
    scopedSlots: { customRender: 'id' }
  },
  {
    title: '名称',
    dataIndex: 'device_name'
  },
  {
    title: 'mac',
    dataIndex: 'mac_addr'
  },

  {
    title: 'ip',
    dataIndex: 'ip_addr',
    sorter: true
  },
  {
    title: '音频',
    dataIndex: 'audio_count',
    sorter: true,
    needTotal: true,
    scopedSlots: { customRender: 'audio_count' }
  },
  {
    title: '状态',
    dataIndex: 'status',
    scopedSlots: { customRender: 'status' },
    width: '10%'
  },
  {
    title: '创建时间',
    dataIndex: 'gmt_create',
    sorter: true
  },
  {
    title: 'loading',
    dataIndex: 'loading',
    value: false,
    visible: false
  },
  {
    title: '更新时间',
    dataIndex: 'gmt_modify',
    sorter: true,
    visible: false
  },
  {
    title: '操作',
    dataIndex: 'action',
    width: '160px',
    scopedSlots: { customRender: 'action' }
  }
]

export default {
  name: 'DeviceList',
  components: {
    STable,
    Ellipsis,
    DeviceInfoForm,
    DiscoveryDeviceTable,
    DiscoveryDeviceAdvancedTable,
    DeviceAudioChannelEditForm,
    DeviceAudioSetForm
  },
  data () {
    this.columns = columns
    return {
      data: [],
      visible: false,
      edit_visible: false,
      discovery_form_visible: false,
      channel_visible: false,
      audio_set_visible: false,
      discovery_loading: false,
      channelConfirmLoading: false,
      audioSettingConfirmLoading: false,
      discovery_device_list: [],
      confirmLoading: false,
      mdl: null,
      channel_mdl: null,
      audio_set_mdl: null,
      record: null,
      // 高级搜索 展开/关闭
      advanced: false,
      // 查询参数
      queryParam: {},
      groupOptions: [],
      // 加载数据方法 必须为 Promise 对象
      loadData: parameter => {
        const requestParameters = Object.assign({}, parameter, this.queryParam)
        console.log('get device , request parameters:', requestParameters)

        return getDeviceList(requestParameters)
          .then(res => {
            this.data = res.data
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
    getDeviceGroupOption()
         .then(res => {
             this.groupOptions = res.data
        })
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
      this.mdl = {}
      this.visible = true
    },
    handleDiscovery () {
      this.discovery_form_visible = true
    },
    handleEdit (record) {
      this.visible = true
      this.mdl = { ...record }
      this.options = this.groupOptions
    },
    handleAudioChannelEdit (key) {
      this.channel_visible = true
       const info = { 'device_id': key }
       new Promise((resolve, reject) => {
            getDeviceAudioChannelInfo(info).then(res => {
                  if (res.code === 200) {
                     this.channel_mdl = res.result
                  }
            }).catch(error => {
                this.loading = false
                reject(error)
            })
        }).then()
    },
    batchOpenAudio () {
        console.log(this.selectedRows)
        const deviceIds = []
        for (let i = 0; i < this.selectedRows.length; i++) {
            const row = this.selectedRows[i]
            if (row.status !== 0) {
                deviceIds.push(row.id)
            }
        }
        const info = { 'device_ids': deviceIds }
        this.loading = true
        new Promise((resolve, reject) => {
            openAudio(info).then(res => {
                  if (res.code === 200) {
                      this.$message.info(res.message)
                      this.$refs.table.refresh()
                  } else {
                      this.loading = false
                      this.$message.error(res.message)
                  }
            }).catch(error => {
                reject(error)
                 this.$message.error('请求失败')
                this.loading = false
            })
        }).then(
        )
    },
    batchCloseAudio () {
        const deviceIds = []
        for (let i = 0; i < this.selectedRows.length; i++) {
            const row = this.selectedRows[i]
            if (row.status !== 0) {
                deviceIds.push(row.id)
            }
        }
         this.loading = true
        const info = { 'device_ids': deviceIds }
        new Promise((resolve, reject) => {
            closeAudio(info).then(res => {
                  if (res.code === 200) {
                      this.$message.info(res.message)
                      this.$refs.table.refresh()
                  } else {
                      this.loading = false
                      this.$message.error(res.message)
                  }
            }).catch(error => {
                reject(error)
                 this.loading = false
                 this.$message.error('请求失败')
            })
        }).then(

        )
    },
    handleAudioSet (key) {
      this.audio_set_visible = true
       const info = { 'device_id': key }
       new Promise((resolve, reject) => {
            getDeviceAudioSetting(info).then(res => {
                  if (res.code === 200) {
                     this.audio_set_mdl = res.result
                  }
            }).catch(error => {
                this.loading = false
                reject(error)
            })
        }).then()
    },
    delete_device (key) {
        console.log(this.data)
        // const newData = this.data.filter(item => item.device_id !== key)
        // this.data = newData
        this.loading = true
        new Promise((resolve, reject) => {
            deleteDevice(key).then(res => {
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
    handleOk () {
      const form = this.$refs.createModal.form
      this.confirmLoading = true
       form.validateFields((errors, values) => {
        if (!errors) {
          console.log('values', values)
            // 修改 e.g.
            new Promise((resolve, reject) => {
                if (values.id > 0) {
                    editDevice(values).then(res => {
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
                     createDevice(values).then(res => {
                          // 重置表单数据
                          if (res.code === 200) {
                              this.$message.info(res.message)
                              form.resetFields()
                              this.visible = false
                              this.confirmLoading = false
                              // 刷新表格
                              this.$refs.table.refresh()
                          } else {
                            this.$message.error(res.message)
                             this.confirmLoading = false
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
    handleChannelOk () {
      const form = this.$refs.deviceAudioChannelModal.form
      this.channelConfirmLoading = true
      form.validateFields((errors, values) => {
        if (!errors) {
          console.log('values', values)
          if (values.id > 0) {
            // 修改 e.g.
            new Promise((resolve, reject) => {
                updateDeviceAudioChannelInfo(values).then(res => {
                      // 重置表单数据
                      if (res.code === 200) {
                          this.$message.info(res.message)
                          form.resetFields()
                          this.channel_visible = false
                          this.channelConfirmLoading = false
                          // 刷新表格
                          this.$refs.table.refresh()
                      } else {
                          this.$message.error(res.message)
                      }
                }).catch(error => {
                    this.channelConfirmLoading = false
                    reject(error)
                })
            }).then()
          } else {
          }
        } else {
          this.channelConfirmLoading = false
        }
      })
    },

    handleAudioSettingOk () {
      const form = this.$refs.deviceAudioSetModal.form
      this.audioSettingConfirmLoading = true
      form.validateFields((errors, values) => {
        if (!errors) {
          console.log('values', values)
          if (values.id > 0) {
            // 修改 e.g.
            new Promise((resolve, reject) => {
                updateDeviceAudioSetting(values).then(res => {
                      // 重置表单数据
                      if (res.code === 200) {
                          this.$message.info(res.message)
                          form.resetFields()
                          this.channel_visible = false
                          this.audioSettingConfirmLoading = false
                          // 刷新表格
                          this.$refs.table.refresh()
                      } else {
                          this.$message.error(res.message)
                      }
                }).catch(error => {
                    this.audioSettingConfirmLoading = false
                    reject(error)
                })
            }).then()
          } else {
          }
        } else {
          this.audioSettingConfirmLoading = false
        }
      })
    },
    handleCancel () {
      this.visible = false
      const form = this.$refs.createModal.form
      form.resetFields()
    },
    handleEditCancel () {
      this.edit_visible = false
      const form = this.$refs.editModal.form
      form.resetFields() // 清理表单数据（可不做）
    },
    handleDiscoveryCancel () {
      this.discovery_form_visible = false
      this.discovery_loading = false
      this.discovery_device_list = []
    },
    handleChannelCancel () {
      this.channel_visible = false
    },
    handleAudioSettingCancel () {
      this.audio_set_visible = false
    },
    handleAudioRecord (event, key) {
      const target = this.data.find(item => item.id === key)

      target._originalData = { ...target }
      target.loading = true
      // target.status = 2
       const info = { 'device_id': key }
       new Promise((resolve, reject) => {
           if (target.status === 1) {
                openAudio(info).then(res => {
                      if (res.code === 200) {
                          target.status = 2
                          target.loading = false
                          this.$message.info(res.message)
                      } else {
                          target.loading = false
                          this.$message.error(res.message)
                      }
                }).catch(error => {
                    reject(error)
                    target.loading = false
                     this.$message.error('请求失败')
                })
           } else {
                closeAudio(info).then(res => {
                 if (res.code === 200) {
                      target.status = 1
                     target.loading = false
                     this.$message.info(res.message)
                 } else {
                     target.loading = false
                     this.$message.error(res.message)
                }
                }).catch(error => {
                    reject(error)
                    target.loading = false
                    this.$message.error('请求失败')
                })
           }
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
