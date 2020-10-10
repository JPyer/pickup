<template>

<a-row :gutter="16">
       <a-form :form="form" layout="vertical"  ref="formModifyPassword" >
        <a-form-item label="旧密码">
          <a-input-password  v-decorator="['old_password', {rules:[{required: true, message: '请输入旧密码', validateTrigger: 'blur'}]}]" />
        </a-form-item>
        <a-form-item label="新密码">
          <a-input v-decorator="['password', {rules:[{required: true, min: 6, message: '请输入新密码,最少6位'}]}]" />
        </a-form-item>
        <a-form-item label="确认新密码">
          <a-input v-decorator="['re_password', {rules:[{required: true, min:6, message: '请确认新密码,最少6位'}]}]" />
        </a-form-item>
      </a-form>
       <a-form-item>
            <a-button type="primary" html-type="submit" @click="handleSubmit">提交</a-button>
      </a-form-item>
</a-row>
</template>

<script>
import pick from 'lodash.pick'
import { modifyPassword } from '@/api/user'
import storage from 'store'
import { ACCESS_TOKEN } from '@/store/mutation-types'

const fields = ['old_password', 'password', 're_password']
export default {
 name: 'ModifyPasswordForm',
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
      model: {}
    }
  },
  created () {
    // 防止表单未注册
    fields.forEach(v => this.form.getFieldDecorator(v))

    // 当 model 发生改变时，为表单设置值
    this.$watch('model', () => {
      this.model && this.form.setFieldsValue(pick(this.model, fields))
    })
  },
  methods: {
     handleSubmit () {
          const form = this.$refs.formModifyPassword.form
          form.validateFields((errors, values) => {
              if (!errors) {
                  new Promise((resolve, reject) => {
                      modifyPassword(values).then(res => {
                          if (res.code === 200) {
                              this.$message.info(res.message)
                              // form.resetFields()
                              storage.remove(ACCESS_TOKEN)
                              return this.$store.dispatch('Logout').then(() => {
                                this.$router.push({ name: 'login' })
                              })
                          } else {
                              this.$message.error(res.message)
                          }
                      }).catch(error => {
                          this.loading = false
                          reject(error)
                      })
                  }).then()
              } else {
              }
          })
     }
  }
}
</script>

<style scoped>

</style>
