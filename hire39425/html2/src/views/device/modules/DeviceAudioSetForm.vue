<template>
  <a-modal
    title="音频设置"
    :width="640"
    :visible="visible"
    :confirmLoading="loading"
    @ok="() => { $emit('ok') }"
    @cancel="() => { $emit('cancel') }"
  >
    <a-spin :spinning="loading">
      <a-form :form="form" v-bind="formLayout">
        <a-form-item  label="设备ID">
            {{model.id}}
        </a-form-item>
        <a-form-item label="FFT点数">
             <a-input-number v-decorator="['fft_points', {rules:[{required: true, message: '请输入FFT点数'}]}]" />
        </a-form-item>
        <a-form-item label="输出增益">
             <a-input-number v-decorator="['output_gain', {rules:[{required: true, message: '请输入输出增益'}]}]" />
        </a-form-item>
        <a-form-item label="麦克风头指向参数">
           <a-input-number v-decorator="['mic_direction', {rules:[{required: true, message: '请输入麦克风头指向参数'}]}]" />
        </a-form-item>
         <a-form-item label="状态" >
           {{model.status | statusFilter}}
        </a-form-item>

      </a-form>
    </a-spin>
  </a-modal>
</template>

<script>
import pick from 'lodash.pick'
// 表单字段
const fields = ['id', 'fft_points', 'output_gain', 'mic_direction', 'status', 'writeInDevice']
export default {
  name: 'DeviceAudioChannelEditForm',
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
