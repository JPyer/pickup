<template>
  <a-popover
    v-model="visible"
    trigger="click"
    placement="bottomRight"
    overlayClassName="header-notice-wrapper"
    :getPopupContainer="() => $refs.noticeRef.parentElement"
    :autoAdjustOverflow="true"
    :arrowPointAtCenter="true"
    :overlayStyle="{ width: '300px', top: '50px' }"
  >
    <template slot="content">
      <a-spin :spinning="loading">
            <a-list>
              <a-list-item :key="index" v-for="(item, index) in messages">
                <a-list-item-meta :title="item.content" :description="item.gmt_create">
                  <a-avatar style="background-color: white" slot="avatar" src="/assets/mail.png"/>
                </a-list-item-meta>
              </a-list-item>
            </a-list>
      </a-spin>
    </template>
    <span @click="fetchNotice" class="header-notice" ref="noticeRef" style="padding: 0 18px">
      <a-badge :count="msg_count">
        <a-icon style="font-size: 16px; padding: 4px" type="bell" />
      </a-badge>
    </span>
  </a-popover>
</template>

<script>
import storage from 'store'
export default {
  name: 'HeaderNotice',
  data () {
    return {
      loading: false,
      visible: false,
      messages: [],
      msg_count: storage.get('unread_msg_count') || 0
    }
  },
  created () {
        window.setInterval(() => {
      setTimeout(this.getSystemMsg(1), 0)
    }, 1000 * 60 * 5)
  },
  mounted () {
    this.getSystemMsg(1)
  },
  methods: {
    fetchNotice () {
      if (!this.visible) {
        this.loading = true
        setTimeout(() => {
          this.getSystemMsg(0)
          this.loading = false
           storage.set('unread_msg_count', 0)
           this.msg_count = 0
        }, 1000)
      } else {
        this.loading = false
      }
      this.visible = !this.visible
    },
    getSystemMsg (unread) {
        this.$http.get('/api/system/message?unread=' + unread)
        .then(res => {
          this.messages = res.data
          storage.set('unread_msg_count', this.messages.length)
          this.msg_count = this.messages.length
        })
    }
  }
}
</script>

<style lang="css">
  .header-notice-wrapper {
    top: 50px !important;
  }
</style>
<style lang="less" scoped>
  .header-notice{
    display: inline-block;
    transition: all 0.3s;

    span {
      vertical-align: initial;
    }
  }
</style>
