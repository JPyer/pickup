<template>
  <a-modal
    title="播放音频"
    :width="850"
    :visible="visible"
    :options="options"
    :loading="loading"
    @cancel="handlePlayCancel"
    @ok="handlePlayCancel"
  >
      <audio
         ref="audioModel"
         id="audio"
          controls
          :paused="!visible"
          nodownload="nodownload"
          crossorigin="anonymous"
          @timeupdate="onLoadedmetadata"
            preload="auto"
          autoplay="autoplay">
          <source   type="audio/wav" />
      </audio>
<!--       <aplayer ref="audioModel" controls id="audio"  crossorigin='anonymous' :music="music"></aplayer>-->
      <div>
      <canvas id="canvas1" width="800" height="150"></canvas>
      <canvas id="canvas2" width="800" height="150"></canvas>
      </div>
  </a-modal>
</template>
<script>
import aplayer from 'vue-aplayer'
import config from '@/config/defaultSettings'
import audioApi from '@/api/audio'
import { ACCESS_TOKEN } from '@/store/mutation-types'
import storage from 'store'
import { addWavHeader } from '../stream2pcm'
export default {
  name: 'AudioPlayForm',
  components: {
      aplayer,
      config
  },
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
    },
    audioSrc: {
      type: String,
      default: () => null
    },
    audioTitle: {
      type: String,
      default: () => null
    },
    audioAuthor: {
      type: String,
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
      arraybuffer: null,
      MEDIA_ELEMENT_NODE: new WeakMap(),
      atx: null,
      music: {
       title: this.audioTitle,
       artist: this.audioAuthor,
       src: this.audioSrc,
       autoplay: true
      },
      autoplay: true
    }
  },
  created () {
    console.log('custom play modal created')
    this.audio = document.querySelector('#audio')
    this.ctx = null
    this.canvas1 = null
    this.canvas2 = document.getElementById('canvas2')
  },
  methods: {
      play () {
        this.draw('audio_file')
      },
      analyzerInitialize () {
         let source = null
         if (!this.atx) {
            this.atx = new AudioContext()
           } else {
               this.resume().then(() => {
                 console.log('Playback resumed successfully')
               })
         }

         var analyser = this.atx.createAnalyser()
         var audio = document.querySelector('#audio')

         if (this.MEDIA_ELEMENT_NODE.has(audio)) {
           source = this.MEDIA_ELEMENT_NODE.get(audio)
        } else {
          source = this.atx.createMediaElementSource(audio)
          this.MEDIA_ELEMENT_NODE.set(audio, audio.innerHTML)
        }
        // 将source与分析器链接
         source.connect(analyser)
         // 将分析器与destination链接，这样才能形成到达扬声器的通路
         analyser.connect(this.atx.destination)
         return source
      },
      getAudio () {
         new Promise((resolve, reject) => {
            const data = { 'id': this.model.id, 'tag': 'audio' }
            audioApi.playAudio(data).then(res => {
                if (res.code === 200) {
                    const url = URL.createObjectURL(res) // 通过这个API让语音数据转为成一个url地址
                    // let audio = new Audio();// 在VUE中使用audio标签
                    const audio = document.querySelector('#audio')
                    audio.src = url // 设置audio的src为上面生成的url
                    this.draw()
                    // let playPromiser = audio.play();// 进行播放
                    // 在谷歌内核中,audio.play()会返回一个promise的值，在IE内核中就不会返回任何的值
                    // 所以如果要分浏览器，可以判断playPromiser的值来进行操作
                    audio.onended = () => {
                        // onended可以检测语音是否播完
                    }
                }
            })
        }).then()
     },
      draw (srcType) {
        var that = this
        // 创建上下文
        var atx = this.atx
        var source = null
        const MEDIA_ELEMENT_NODE = this.MEDIA_ELEMENT_NODE
        // 使用Ajax获取音频文件
        var request = new XMLHttpRequest()
        request.open('GET', this.audioSrc, true)
        request.setRequestHeader('Authentication', 'Token ' + storage.get(ACCESS_TOKEN))
        request.responseType = 'arraybuffer' // 配置数据的返回类型

        // 加载完成
        request.onload = function () {
            that.arraybuffer = request.response
            if (request.status !== 200) {
                that.$message.error('访问资源失败：权限不足或资源暂不支持')
                return
            }
            // TODO
            const audio = document.querySelector('#audio')
            //  pcm转wav需要下面三行,不需要转则注释掉，audio 标签中加上src="audioSrc"
            const newArrayBuffer = addWavHeader(that.arraybuffer, 16000, 24, 1)
            audio.src = window.URL.createObjectURL(new Blob([newArrayBuffer], { type: 'audio/wav' }))
            that.arraybuffer = newArrayBuffer.buffer
            //
            if (!that.atx) {
              that.atx = new AudioContext()
           } else {
               that.atx.resume().then(() => {
                 console.log('Playback resumed successfully')
               })
            }
            atx = that.atx
            atx.decodeAudioData(that.arraybuffer, function (buffer) {
                // 创建分析器
                var analyser = atx.createAnalyser()

                // audio.src = this.audioSrc
                // audio.crossorigin = 'anonymous'
                // audio.nodownload = 'nodownload'

                if (srcType === 'buffer') {
                     // source = atx.createBufferSource()
                     if (MEDIA_ELEMENT_NODE.has(audio)) {
                        source = MEDIA_ELEMENT_NODE.get(audio)
                    } else {
                      source = atx.createMediaElementSource(audio)
                      MEDIA_ELEMENT_NODE.set(audio, source)
                    }
                } else {
                     // source = atx.createMediaElementSource(audioTest)
                     if (MEDIA_ELEMENT_NODE.has(audio)) {
                        source = MEDIA_ELEMENT_NODE.get(audio)
                    } else {
                      source = atx.createMediaElementSource(audio)
                      MEDIA_ELEMENT_NODE.set(audio, source)
                    }
                }
                // 将source与分析器链接
                source.connect(analyser)
                // 将分析器与destination链接，这样才能形成到达扬声器的通路
                analyser.connect(atx.destination)
                // 将解码后的buffer数据复制给source
                source.buffer = buffer
                // 播放
                if (srcType === 'buffer') {
                     source.start(0)
                } else {
                    audio.play()
                }
                // 开始绘制频谱图
                const canvas = document.getElementById('canvas1')
                const cwidth = canvas.width
                const cheight = canvas.height - 2
                const meterWidth = 1 // 能量条的宽度
                // const gap = 2 // 能量条的间距
                const meterNum = 800 / (1 + 0) // 计算当前画布上能画多少条
                var ctx = canvas.getContext('2d')
                // 冒头的高度
                // 冒头的颜色
                // 将上一面各个冒头的位置保存到这个数组
                var capHeight = 2
                // var capStyle = '#fff'
                var capStyle = '#001529'
                var capYPositionArray = []
                // 定义一个渐变样式用于画图
                var gradient = ctx.createLinearGradient(0, 0, 0, 300)
                gradient.addColorStop(1, '#0f0')
                gradient.addColorStop(0.5, '#ff0')
                gradient.addColorStop(0, '#4aeb46')
                // 绘制频谱图
                function drawSpectrum () {
                    var array = new Uint8Array(analyser.frequencyBinCount)
                    analyser.getByteFrequencyData(array)
                    // 计算从analyser中的采样步长
                    // var step = Math.round(array.length / meterNum)
                    // 清理画布
                    ctx.clearRect(0, 0, cwidth, cheight)

                    for (var i = 0; i < meterNum; i++) {
                        var value = array[i] // y轴的值
                        // 绘制缓慢降落的冒头
                        if (capYPositionArray.length < Math.round(meterNum)) {
                            // 初始化保存冒头位置的数组，将第一个画面位置保存
                            capYPositionArray.push(value)
                        }
                        ctx.fillStyle = capStyle
                        // 1.开始绘制冒头
                        if (value < capYPositionArray[i]) {
                            // 使用前一次数据
                            ctx.fillRect(i * 2, cheight - (--capYPositionArray[i]), meterWidth, capHeight)
                        } else {
                            // 否则，直接使用当前数据并记录
                            ctx.fillRect(i * 2, cheight - value, meterWidth, capHeight)
                            capYPositionArray[i] = value
                        }
                        // 2.开始绘制频谱条
                        ctx.fillStyle = gradient
                        /* 频谱条的宽度+条间距 */
                        ctx.fillRect(i * 2, cheight - value + capHeight,
                            meterWidth, cheight)
                    }
                    requestAnimationFrame(drawSpectrum)
                }
                requestAnimationFrame(drawSpectrum)

                // 开始绘制波形图

                const canvas2 = document.getElementById('canvas2')
                const cwidth2 = canvas2.width
                const cheight2 = canvas2.height - 2
                const meterWidth2 = 10 // 能量条的宽度
                // const gap = 2 // 能量条的间距
                const meterNum2 = 800 / (10 + 2) // 计算当前画布上能画多少条
                var ctx2 = canvas2.getContext('2d')
                const WIDTH = cwidth
                const HEIGHT = cheight
                const canvasCtx2 = ctx2
                // analyser.fftSize = 2048
                var bufferLength = analyser.fftSize
                var dataArray = new Uint8Array(bufferLength)
                canvasCtx2.clearRect(0, 0, cwidth2, cheight2)

                const draw2 = function () {
                    const drawVisual = requestAnimationFrame(draw2)
                    analyser.getByteTimeDomainData(dataArray)

                    // canvasCtx2.fillStyle = config.primaryColor
                    canvasCtx2.fillStyle = '#001529'
                    canvasCtx2.fillRect(0, 0, cwidth2, cheight2)
                    canvasCtx2.lineWidth = 2
                    canvasCtx2.strokeStyle = '#4aeb46'
                    canvasCtx2.beginPath()

                    var sliceWidth = cwidth2 * 1.0 / bufferLength
                    var x = 0

                    for (var i = 0; i < bufferLength; i++) {
                        var v = dataArray[i] / 128.0
                        var y = v * cheight2 / 2
                        if (i === 0) {
                            canvasCtx2.moveTo(x, y)
                        } else {
                            canvasCtx2.lineTo(x, y)
                        }
                        x += sliceWidth
                    }
                    canvasCtx2.lineTo(canvas.width, canvas.height / 2)
                    canvasCtx2.stroke()
                }
                draw2()
            }, function (e) {
                that.$message.error('波形图、频谱图加载失败')
            })
        }
        request.onerror = function () {
            that.$message.error('访问资源失败：权限不足或资源不存在')
        }
        request.send()
      },
      draw2 (srcType) {
        var that = this
        // 创建上下文
        var atx = that.atx
        var source = null
        const MEDIA_ELEMENT_NODE = that.MEDIA_ELEMENT_NODE
        // 使用Ajax获取音频文件
        var request = new XMLHttpRequest()
        request.open('GET', this.audioSrc, true)
        request.setRequestHeader('Authentication', 'Token ' + storage.get(ACCESS_TOKEN))
        request.responseType = 'arraybuffer' // 配置数据的返回类型

        // 加载完成
        request.onload = function () {
            that.arraybuffer = request.response
            if (request.status !== 200) {
                that.$message.error('访问资源失败：权限不足或资源暂不支持')
                return
            }
            // TODO
            const audio = document.querySelector('#audio')
            //  pcm转wav需要下面三行,不需要转则注释掉，audio 标签中加上src="audioSrc"
            const newArrayBuffer = addWavHeader(that.arraybuffer, 16000, 24, 1)
            audio.src = window.URL.createObjectURL(new Blob([newArrayBuffer], { type: 'audio/wav' }))
            that.arraybuffer = newArrayBuffer.buffer
            //
            source = that.analyzerInitialize()

            atx.decodeAudioData(that.arraybuffer, function (buffer) {
                // 创建分析器
                var analyser = atx.createAnalyser()

                // audio.src = this.audioSrc
                // audio.crossorigin = 'anonymous'
                // audio.nodownload = 'nodownload'

                // 将解码后的buffer数据复制给source
                source.buffer = buffer

                // 播放
                if (srcType === 'buffer') {
                     source.start(0)
                } else {
                    audio.play()
                }
                // 开始绘制频谱图
                requestAnimationFrame(that.drawSpectrum(analyser))

                // 开始绘制波形图
                const canvas2 = that.canvas2
                const cwidth2 = canvas2.width
                const cheight2 = canvas2.height - 2
                const meterWidth2 = 10 // 能量条的宽度
                // const gap = 2 // 能量条的间距
                const meterNum2 = 800 / (10 + 2) // 计算当前画布上能画多少条
                var ctx2 = canvas2.getContext('2d')
                const WIDTH = canvas2.width
                const HEIGHT = canvas2.height
                const canvasCtx2 = ctx2
                // analyser.fftSize = 2048
                var bufferLength = analyser.fftSize
                var dataArray = new Uint8Array(bufferLength)
                canvasCtx2.clearRect(0, 0, cwidth2, cheight2)

                const draw2 = function () {
                    const drawVisual = requestAnimationFrame(draw2)
                    analyser.getByteTimeDomainData(dataArray)

                    // canvasCtx2.fillStyle = config.primaryColor
                    canvasCtx2.fillStyle = '#001529'
                    canvasCtx2.fillRect(0, 0, cwidth2, cheight2)
                    canvasCtx2.lineWidth = 2
                    canvasCtx2.strokeStyle = '#4aeb46'
                    canvasCtx2.beginPath()

                    var sliceWidth = cwidth2 * 1.0 / bufferLength
                    var x = 0

                    for (var i = 0; i < bufferLength; i++) {
                        var v = dataArray[i] / 128.0
                        var y = v * cheight2 / 2
                        if (i === 0) {
                            canvasCtx2.moveTo(x, y)
                        } else {
                            canvasCtx2.lineTo(x, y)
                        }
                        x += sliceWidth
                    }
                    canvasCtx2.lineTo(canvas2.width, canvas2.height / 2)
                    canvasCtx2.stroke()
                }
                draw2()
            }, function (e) {
                that.$message.error('波形图、频谱图加载失败')
            })
        }
        request.onerror = function () {
            that.$message.error('访问资源失败：权限不足或资源不存在')
        }
        request.send()
      },
      onTimeupdate (res) {
          // console.log(res)
          // this.$refs.audioModal.currentTime = res.target.currentTime
          // this.sliderTime = parseInt(
          //   (this.audio.currentTime / this.audio.maxTime) * 100
          //  )
      },

      handlePlayCancel () {
        this.visible = false
        this.audioSrc = null
        this.arraybuffer = []
      },
      onLoadedmetadata (e) {
      },
      drawSpectrum (analyser) {
          const canvas = document.getElementById('canvas1')
          var ctx = canvas.getContext('2d')
          const cwidth = canvas.width
          const cheight = canvas.height - 2
          const meterNum = 800 / (1 + 0) // 计算当前画布上能画多少条
          const meterWidth = 1 // 能量条的宽度
          var capHeight = 2
          // var capStyle = '#fff'
          var capStyle = '#001529'
          var capYPositionArray = []
          var gradient = ctx.createLinearGradient(0, 0, 0, 300)
          gradient.addColorStop(1, '#0f0')
          gradient.addColorStop(0.5, '#ff0')
          gradient.addColorStop(0, '#4aeb46')
          var array = new Uint8Array(analyser.frequencyBinCount)
          analyser.getByteFrequencyData(array)
          // 计算从analyser中的采样步长
          // var step = Math.round(array.length / meterNum)
          // 清理画布
          ctx.clearRect(0, 0, cwidth, cheight)

          for (var i = 0; i < meterNum; i++) {
              var value = array[i] // y轴的值
              // 绘制缓慢降落的冒头
              if (capYPositionArray.length < Math.round(meterNum)) {
                  // 初始化保存冒头位置的数组，将第一个画面位置保存
                  capYPositionArray.push(value)
              }
              ctx.fillStyle = capStyle
              // 1.开始绘制冒头
              if (value < capYPositionArray[i]) {
                  // 使用前一次数据
                  ctx.fillRect(i * 2, cheight - (--capYPositionArray[i]), meterWidth, capHeight)
              } else {
                  // 否则，直接使用当前数据并记录
                  ctx.fillRect(i * 2, cheight - value, meterWidth, capHeight)
                  capYPositionArray[i] = value
              }
              // 2.开始绘制频谱条
              ctx.fillStyle = gradient
              /* 频谱条的宽度+条间距 */
              ctx.fillRect(i * 2, cheight - value + capHeight,
                  meterWidth, cheight)
          }
          requestAnimationFrame(this.drawSpectrum(analyser))
      }
  },
  watch: {
      'visible' (val, oldVal) {
          // const audio = this.$refs.audioModel
          const audio = document.querySelector('audio')
          if (!val) {
              audio.pause()
              // audio.currentTime = 0
          } else {
              window.AudioContext = (window.AudioContext || window.webkitAudioContext || window.mozAudioContext)
              window.requestAnimationFrame = window.requestAnimationFrame || window.webkitRequestAnimationFrame
              try {
                const atx = new AudioContext()
                  } catch (e) {
               this.$message.error('您的浏览器不支持AudioContext,无法显示频谱图')
               return false
              }
              this.music.src = this.audioSrc
              this.music.artist = this.audioAuthor
              this.music.title = this.audioTitle
              // this.getAudio()
              // this.draw('buffer')
              this.draw('audio_file')
          }
      }
  }
}
</script>
<style>
    #fileWrapper {
        transition: all 0.5s ease
    }
    #fileWrapper:hover {
        opacity: 1!important
    }
    #visualizer_wrapper {
        text-align: center
    }
</style>
