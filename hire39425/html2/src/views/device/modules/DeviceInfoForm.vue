<template>
  <a-modal
    :title="model && model.id > 0 ? '编辑设备' : '添加设备' "
    :width="640"
    :visible="visible"
    :confirmLoading="loading"
    @ok="() => { $emit('ok') }"
    @cancel="() => { $emit('cancel') }"
  >
    <a-spin :spinning="loading">
      <a-form :form="form" v-bind="formLayout">
        <!-- 检查是否有 id 并且大于0，大于0是修改。其他是新增，新增不显示主键ID -->
        <a-form-item v-show="model && model.id > 0" label="设备ID">
          <a-input v-decorator="['id', { initialValue: 0 }]" disabled />
        </a-form-item>
        <a-form-item label="设备名称">
          <a-input v-decorator="['device_name', {rules:[{required: false, message: '请输入设备名称'}]}]"  />
        </a-form-item>
        <a-form-item label="设备ip">
          <a-input v-decorator="['ip_addr',  {rules:[{required: true, message: '请输入设备IP地址：如192.168.X.X'}]}]"  :disabled="model.status === 1 || model.status === 2"/>
        </a-form-item>
        <a-form-item label="网卡物理地址"  v-show="model && model.id > 0">
            <a-input v-decorator="['mac_addr', {rules:[{required: false, message: '请输入网卡物理地址'}]}]" disabled/>
        </a-form-item>
        <a-form-item label="子网掩码"  v-show="model && model.id > 0">
           <a-input v-decorator="['subnet', {rules:[{required: false, message: '请输入子网掩码'}]}]" />
        </a-form-item>
        <a-form-item label="dns服务器1" v-show="model && model.id > 0">
           <a-input v-decorator="['dns_server1', {rules:[{required: false, message: '请输入dns服务器'}]}]" />
        </a-form-item>
        <a-form-item label="dns服务器2"  v-show="model && model.id > 0">
           <a-input v-decorator="['dns_server2', {rules:[{required: false, message: '请输入dns服务器'}]}]" />
        </a-form-item>
        <a-form-item label="所属分组">
            <a-select v-decorator="['device_group_id', {rules:[{required: false, message: '请输入所在组'}]}]">
                <a-select-option  v-for="option in options" :key="option.id" :value="option.id" :selected="model.device_group_id === option.id">
                    {{ option.name }}
                </a-select-option>
            </a-select>
        </a-form-item>
        <a-form-item label="备注">
          <a-input v-decorator="['remark', {rules: [{required: false, min: 1, message: '请输入至少五个字符的规则描述！'}]}]" />
        </a-form-item>
         <a-form-item label="状态" v-show="model && model.id > 0">
            {{model.status | statusFilter}}
        </a-form-item>
        <a-form-item label="写入硬件" v-show="model && visible">
            <a-checkbox v-decorator="['writeInDevice',{rules: [], initialValue: 0}]" :disabled="model.status === 0 || model.status === 3"></a-checkbox>
        </a-form-item>
      </a-form>
    </a-spin>
  </a-modal>
</template>

<script>
import pick from 'lodash.pick'
// 表单字段
const fields = ['id', 'device_name', 'device_group_id', 'mac_addr', 'ip_addr', 'subnet', 'gateway', 'dns_server1', 'dns_server2', 'security_key', 'remark', 'writeInDevice']

export default {
  name: 'DeviceInfoForm',
  props: {
    visible: {
      type: Boolean,
      required: true
    },
    loading: {
      type: Boolean,
      default: () => false
    },
    model: {
      type: Object,
      default: () => null
    },
    options: {
      type: Array,
      default: () => null
    }
  },
  data () {
    this.formLayout = {
      labelCol: {
        xs: { span: 24 },
        sm: { span: 7 }
      },
      wrapperCol: {
        xs: { span: 24 },
        sm: { span: 13 }
      }
    }
    return {
      form: this.$form.createForm(this)
    }
  },
  filters: {
  },
  created () {
    console.log('custom modal created')

    // 防止表单未注册
    fields.forEach(v => this.form.getFieldDecorator(v))

    // 当 model 发生改变时，为表单设置值
    this.$watch('model', () => {
      this.model && this.form.setFieldsValue(pick(this.model, fields))
    })
  }
}
</script>
