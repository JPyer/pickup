<template>
  <a-modal
    title="编辑设备"
    :width="640"
    :visible="visible"
    :options="options"
    :confirmLoading="loading"
    @ok="() => { $emit('ok') }"
    @cancel="() => { $emit('cancel') }"
  >
    <a-spin :spinning="loading">
        <a-form @submit="handleSubmit" :form="form">
    <a-form-item
      label="设备名称"
      :labelCol="labelCol"
      :wrapperCol="wrapperCol"
    >
      <a-input v-decorator="['name', {rules:[{required: true, message: '请输入设备名称'}]}]" />
    </a-form-item>
    <a-form-item
      label="设备密钥"
      :labelCol="labelCol"
      :wrapperCol="wrapperCol"
    >
        <a-input v-decorator="['security_key', {rules:[{required: false, message: '请输入设备密钥'}]}]" />
    </a-form-item>
    <a-form-item
      label="设备ip"
      :labelCol="labelCol"
      :wrapperCol="wrapperCol"
    >
      <a-input v-decorator="['ip_addr', {rules:[{required: false, message: '请输入ip地址'}]}]" />

    </a-form-item>
      <a-form-item
      label="网卡物理地址"
      :labelCol="labelCol"
      :wrapperCol="wrapperCol"
    >
      <a-input v-decorator="['mac_addr', {rules:[{required: false, message: '请输入网卡物理地址'}]}]" />
    </a-form-item>
     <a-form-item
      label="子网掩码"
      :labelCol="labelCol"
      :wrapperCol="wrapperCol"
    >
      <a-input v-decorator="['subnet', {rules:[{required: false, message: '请输入子网掩码'}]}]" />
    </a-form-item>
    <a-form-item
      label="dns服务器1"
      :labelCol="labelCol"
      :wrapperCol="wrapperCol"
    >
      <a-input v-decorator="['dns_server1', {rules:[{required: false, message: '请输入dns服务器'}]}]" />
    </a-form-item>
    <a-form-item
      label="dns服务器2"
      :labelCol="labelCol"
      :wrapperCol="wrapperCol"
    >
      <a-input v-decorator="['dns_server2', {rules:[{required: false, message: '请输入dns服务器'}]}]" />
    </a-form-item>
    <a-form-item
      label="所属分组"
      :labelCol="labelCol"
      :wrapperCol="wrapperCol"
    >
      <a-select v-decorator="['group_id', {rules:[{required: true, message: '请输入所在组'}]}]">
        <a-select-option  v-for="option in options" :key="option.id" :value="option.id" >
            {{ option.name }}
        </a-select-option>

      </a-select>
    </a-form-item>
    <a-form-item
      label="备注"
      :labelCol="labelCol"
      :wrapperCol="wrapperCol"
    >
      <a-textarea v-decorator="['remark']"></a-textarea>
    </a-form-item>
  </a-form>
    </a-spin>
  </a-modal>

</template>

<script>
import pick from 'lodash.pick'

const fields = ['name', 'group_id', 'ip_addr', 'subnet', 'gateway', 'dns_server1', 'dns_server2', 'security_key', 'remark']

export default {
  name: 'DeviceEditForm',
  props: {
    visible: {
      type: Boolean,
      required: true
    },
    loading: {
      type: Boolean,
      default: () => false
    },
    record: {
      type: Object,
      default: null
    },
    options: {
      type: Array,
      default: () => null
    }
  },
  data () {
    return {
      labelCol: {
        xs: { span: 24 },
        sm: { span: 7 }
      },
      wrapperCol: {
        xs: { span: 24 },
        sm: { span: 13 }
      },
      form: this.$form.createForm(this)
    }
  },
  // mounted () {
  //   console.log(this.record)
  //   this.record && this.form.setFieldsValue(pick(this.record, fields))
  // },
   created () {
    console.log('custom modal created')

    // 防止表单未注册
    fields.forEach(v => this.form.getFieldDecorator(v))

    // 当 model 发生改变时，为表单设置值
    this.$watch('record', () => {
      this.record && this.form.setFieldsValue(pick(this.record, fields))
    })
  },
  methods: {
    onOk () {
      console.log('监听了 modal ok 事件')
      return new Promise(resolve => {
        resolve(true)
      })
    },
    onCancel () {
      console.log('监听了 modal cancel 事件')
      return new Promise(resolve => {
        resolve(true)
      })
    },
    handleSubmit () {
      const { form: { validateFields } } = this
      this.visible = true
      validateFields((errors, values) => {
        if (!errors) {
          console.log('values', values)
        }
      })
    }
  }
}
</script>
