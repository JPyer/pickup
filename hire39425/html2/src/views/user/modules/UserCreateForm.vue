<template>
  <a-modal
    :title="model && model.id >0 ? '编辑' : '添加'"
    :width="640"
    :visible="visible"
    :options="options"
    :confirmLoading="loading"
    @ok="() => { $emit('ok') }"
    @cancel="() => { $emit('cancel') }"
  >
    <a-spin :spinning="loading">
      <a-form :form="form" v-bind="formLayout">
        <!-- 检查是否有 id 并且大于0，大于0是修改。其他是新增，新增不显示主键ID -->
        <a-form-item v-show="model && model.id > 0" label="ID">
          <a-input v-decorator="['id', { initialValue: 0 }]" disabled />
        </a-form-item>
        <a-form-item label="用户名">
          <a-input v-decorator="['username', {rules:[{required: true, message: '请输入用户名'}]}]" />
        </a-form-item>
        <a-form-item label="姓名">
          <a-input v-decorator="['realname', {rules:[{required: true, message: '请输入姓名'}]}]" />
        </a-form-item>
          <a-form-item label="联系方式">
          <a-input v-decorator="['telephone', {rules:[{required: false, message: '请输入联系方式'}]}]" />
        </a-form-item>
        <a-form-item label="密码" v-if="!model">
          <a-input v-decorator="['password', {rules:[{required: true, min: 6, message: '请输入密码(至少6位)'}]}]" />
        </a-form-item>
         <a-form-item label="角色">
          <a-select v-decorator="['role_uid', {rules:[{required: true, message: '请输入角色'}]}]" :disabled="model && model.id > 0">
            <a-select-option  v-for="option in role_options" :key="option.value" :value="option.value" v-if="option.value !== current_role">
                {{ option.text }}
            </a-select-option>
          </a-select>
        </a-form-item>
         <a-form-item label="启用">
            <a-checkbox v-decorator="['is_active',{rules: [], initialValue: true}]" ></a-checkbox>
        </a-form-item>
      </a-form>
    </a-spin>
  </a-modal>
</template>

<script>
import pick from 'lodash.pick'

// 表单字段
const fields = ['id', 'username', 'realname', 'telephone', 'password', 'role_uid', 'is_active']

export default {
  name: 'UserCreateForm',
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
      role_options: [
        { 'value': 'org_admin', 'text': '机构管理员' },
        { 'value': 'org_user', 'text': '机构子用户' }
      ],
      form: this.$form.createForm(this),
      current_role: this.$store.getters.roles['creatorId']
    }
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
