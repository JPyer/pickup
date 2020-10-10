<template>
  <page-header-wrapper>
    <a-card :bordered="false">
      <div class="table-page-search-wrapper">
        <a-form layout="inline">
          <a-row :gutter="48">
             <a-col :md="8" :sm="24">
              <a-form-item label="音频名称">
                <a-input v-model="queryParam.name" placeholder=""/>
              </a-form-item>
             </a-col>
             <a-col :md="8" :sm="24">
              <a-form-item label="设备">
                <a-select v-model="queryParam.device_id" placeholder="全部" default-value="" @change="deviceChange">
                  <a-select-option value="" >全部</a-select-option>
                  <a-select-option v-for="option in deviceOptions" :key="option.id" :value="option.id">
                    {{option.device_name}}
                  </a-select-option>

                </a-select>
              </a-form-item>
            </a-col>
            <template>
              <a-col :md="8" :sm="24">
                <a-form-item label="上传日期">
                  <a-date-picker v-model="queryParam.date" style="width: 100%" placeholder="请输入上传日期"/>
                </a-form-item>
              </a-col>

            </template>
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
      </div>

      <s-table
        ref="table"
        size="default"
        rowKey="id"
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
            <a-button
                    @click="playAudio(record)"
                    :disabled="record.status === 0 "
                    ref='record_btn'
                    size="small"
                    type="primary"
                   >
                   <a-icon type="play-circle"  />
                回播
            </a-button>
            <a-divider type="vertical" />
            <a @click="handleEdit(record)">修改</a>
             <a-divider type="vertical" />
            <a-popconfirm title="是否要删除该音频记录（音频文件请自行移除）？" @confirm="delete_audio(record.id)">
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

        <audio-play-form
            ref="playAudioModal"
        :visible="play_visible"
        :loading="play_confirmLoading"
        :audioSrc="audioSrc"
        :audioTitle="audioTitle"
        :model="mdl"
        :audioAuthor="audioAuthor">

        </audio-play-form>
    </a-card>
  </page-header-wrapper>
</template>

<script>
import moment from 'moment'
import { STable, Ellipsis } from '@/components'
import audioApi from '@/api/audio'
import CreateForm from './modules/AudioInfoForm'
import AudioPlayForm from './modules/AudioPlayForm'
import { getDeviceOption } from '@/api/device'
import { getUrlKey } from '@/utils/util'
import defaultSettings from '@/config/defaultSettings'
import storage from 'store'
import { ACCESS_TOKEN } from '@/store/mutation-types'
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
    title: '音频名称',
    dataIndex: 'name'
  },
  {
    title: '文件路径',
    dataIndex: 'file_path'
  },
  {
    title: '时长',
    dataIndex: 'duration'
  },
  {
    title: '大小(M)',
    dataIndex: 'file_size'
  },
  {
    title: '所属设备',
    dataIndex: 'device_name'
  },
    {
    title: '创建时间',
    dataIndex: 'gmt_create'
  },
  {
    title: '操作',
    dataIndex: 'action',
    width: '200px',
    scopedSlots: { customRender: 'action' }
  }
]

export default {
  name: 'AudioList',
  components: {
    STable,
    Ellipsis,
    CreateForm,
    AudioPlayForm
  },
  data () {
    this.columns = columns
    return {
      // create model
      visible: false,
      confirmLoading: false,
      play_visible: false,
      play_confirmLoading: false,
      audioSrc: null,
      audioTitle: null,
      audioAuthor: null,
      mdl: null,
      // 高级搜索 展开/关闭
      advanced: false,
      // 查询参数
      queryParam: {},
      deviceOptions: [],
      // 加载数据方法 必须为 Promise 对象
      loadData: parameter => {
        const requestParameters = Object.assign({}, parameter, this.queryParam)
        return audioApi.getAudioList(requestParameters)
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
    getDeviceOption()
         .then(res => {
             this.deviceOptions = res.data
        }
    )
    const deviceId = getUrlKey('device_id')
    // console.log(this.queryParam.device_id)
    // if (!this.queryParam.device_id) {
    //     if (deviceId) {
    //         this.queryParam.device_id = parseInt(deviceId)
    //     }
    // }
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
                    audioApi.editAudio(values).then(res => {
                          // 重置表单数据
                          if (res.code === 200) {
                              this.$message.info(res.message)
                              form.resetFields()
                              this.visible = false
                              this.confirmLoading = false
                              // 刷新表格
                              this.$refs.table.refresh()
                          } else {
                              this.$message.error(`系统错误：${res.message}`)
                          }
                    }).catch(error => {
                        this.confirmLoading = false
                        this.$message.error(`请求失败`)
                        reject(error)
                    })
               } else {

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
    deviceChange (val) {
      // console.log(val)
      //  this.queryParam.device_id = parseInt(val)
      // this.queryParam.device_id = val
      // if (this.$route.query.device_id) {
      //     this.$route.query = null
      // }
    },
    playAudio (record) {
        // TODO
        // const url = 'http://localhost:8000/api/audio/file'
        // const pcmBase64 = getWebPcm2WavBase64(url)
        // const wavdata = getWebPcm2WavBase64(url)

        this.play_visible = true
        this.play_confirmLoading = false
        this.audioSrc = defaultSettings.baseUrl + audioApi.audioApi.play + '?id=' + record.id + '&token=' + storage.get(ACCESS_TOKEN)
        this.audioTitle = record.file_path
        this.audioAuthor = record.device_name
        this.mdl = record
    },
    delete_audio (key) {
        this.loading = true
        new Promise((resolve, reject) => {
            audioApi.deleteAudio(key).then(res => {
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
