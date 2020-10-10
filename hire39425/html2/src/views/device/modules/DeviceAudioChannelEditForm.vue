<template>
  <a-modal
    title="音频通道信息编辑"
    :width="640"
    :visible="visible"
    :confirmLoading="loading"
    @ok="() => { $emit('ok') }"
    @cancel="() => { $emit('cancel') }"
  >
    <a-spin :spinning="loading">
      <a-form :form="form" v-bind="formLayout">
        <a-form-item v-show="model && model.id > 0" label="设备ID">
          <a-input v-decorator="['id', { initialValue: 0 }]" disabled />
        </a-form-item>
        <a-form-item label="输出通道数">
            <a-select v-decorator="['output_channel', {rules:[{required: false, message: '请输入输出通道数,默认为0'}]}]">
                <a-select-option  v-for="option in channelOptions" :key="option.value" :value="option.value" >
                    {{ option.name }}
                </a-select-option>
            </a-select>
        </a-form-item>
        <a-form-item label="音频采样率">
            <a-select v-decorator="['audio_sample_rate', {rules:[{required: true, message: '请输入声道数，默认为16000'}]}]">
                <a-select-option  v-for="option in sampleRateOptions" :key="option" :value="option" >
                    {{ option}}
                </a-select-option>
            </a-select>
        </a-form-item>
        <a-form-item label="采样位数">
           <a-input-number v-decorator="['audio_sample_bits', {rules:[{required: true, message: '请输入采样位数,默认为24'}]}]" />
        </a-form-item>
         <a-form-item label="重传超时阈值">
           <a-input v-decorator="['retrans_timeout', {rules:[{required: true, message: '重传超时阈值，默认为1000'}]}]" />
        </a-form-item>
      </a-form>
    </a-spin>
  </a-modal>
</template>

<script>
import pick from 'lodash.pick'
// 表单字段
const fields = ['id', 'output_channel', 'audio_sample_rate', 'audio_sample_bits', 'retrans_timeout']

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
      form: this.$form.createForm(this),
      channelOptions: [
        {
            value: 1,
            name: '单路输出'
        },
        {
            value: 8,
            name: '8路输出:7MIC+1'
        },
         {
            value: 9,
            name: '9路输出:8MIC+1'
        },
         {
            value: 17,
            name: '17路输出:16MIC+1'
        }
      ],
      encoderOptions: [
        {
            value: 1,
            name: 'PCM_S8'
        },
         {
            value: 2,
            name: 'PCM_S16LE'
        },
         {
            value: 3,
            name: 'PCM_S24LE'
        },
         {
            value: 10,
            name: 'OPUS'
        }
      ],
      channelsOptions: [
        {
            value: 1,
            name: '单声道'
        },
         {
            value: 2,
            name: '双声道'
        }
      ],

      sampleRateOptions: [ 8000, 12000, 16000 ],
      audioBitrateOption: [ 0, 16000, 32000, 48000 ]
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
