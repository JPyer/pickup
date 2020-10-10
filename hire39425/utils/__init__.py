# encoding:utf-8
import os
import platform
import signal
import subprocess
import sys
import time
import datetime
import psutil
import multiprocessing


def runcmd(command):

    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, )
    try:
        outs, errs = proc.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        outs, errs = proc.communicate()
    return proc.returncode, proc.pid, outs, errs


def kill_pid(pid):
    sys = platform.system()
    rtn_code = 1
    try:
        if sys == "Linux":
            rtn_code = os.kill(pid, signal.SIGKILL)
        else:
            cmd = 'taskkill -f -pid %s' % pid
            rtn_code, _, out, _ = runcmd(cmd)

    except OSError as  e:
        print('没有如此进程!!!')
    else:
        print('已杀死pid为%s的进程,　返回值是:%s' % (pid, rtn_code))

    return rtn_code == 0


TIME = 1
CMD = "test.py"  # 你所要执行的命令


class DaemonProcess(object):
    def __init__(self, sleep_time, cmd):
        self.sleep_time = sleep_time  # 休息时间
        self.cmd = cmd  # 需要执行的命令
        self.p = None  # 子进程对象
        self.run()  # 调用run()方法

    def check(self):
        try:
            while True:
                time.sleep(self.sleep_time * 60)
                # self.pid = os.popen('ps -ef | grep {}'.format(self.cmd)).readlines()[0].split()[1] # str类型
                self.pid = self.p.pid  # 查看子进程的进程id
                self.poll = self.p.poll()  # returncode 返回码
                if self.poll:  # self.poll不为None, 表明子进程终止了
                    print("程序已终止，重启程序")
                    self.p.kill()
                    self.run()
        except KeyboardInterrupt as e:  #
            print("[{}] 监测到ctrl+c，准备退出程序".format(datetime.datetime.now()))
            self.p.kill()

    def run(self):
        print("[{}] 开始运行子进程!".format(datetime.datetime.now()))
        # 使用subprocess.Popen()创建一个子进程运行你的py文件
        dir_path = os.path.join(os.path.abspath("."), "software")
        os.chdir(dir_path)
        self.p = subprocess.Popen(self.cmd, stdin=sys.stdin, stdout=sys.stdout,
                                  stderr=sys.stderr, shell=True)


def exec_backend_process(name, func, *args):
    p = multiprocessing.Process(name=name, target=func, args=args)
    p.daemon = True
    p.start()
    return os.getppid(), os.getpid()
