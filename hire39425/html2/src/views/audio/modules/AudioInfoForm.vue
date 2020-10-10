<template>
  <a-modal
    title="编辑音频信息"
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
        <a-form-item label="音频名称">
          <a-input v-decorator="['name', {rules:[{required: false, message: '默认为空,可以指定以便检索'}]}]"/>
        </a-form-item>
        <a-form-item label="文件路径">
          <a-input v-decorator="['file_path', {rules:[{required: false, message: '请输入file_path'}]}]" disabled/>
        </a-form-item>
        <a-form-item label="文件大小">
          <a-input v-decorator="['file_size']" disabled/>
        </a-form-item>
          <a-form-item label="时长">
          <a-input v-decorator="['duration']" disabled/>
        </a-form-item>
      </a-form>
    </a-spin>
  </a-modal>
</template>

<script>
import pick from 'lodash.pick'

// 表单字段
const fields = ['id', 'name', 'file_path', 'file_size', 'duration']

export default {
  name: 'AudioEditForm',
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
