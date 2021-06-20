#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 alibaba-inc. All Rights Reserved
#

import Queue, sys, time, traceback, datetime
from threading import Thread

"""
新版多线程工具，新增以下功能：
    1、具备超时间，线程超时后将线程抛弃，另外在多启动一个线程来顶替；被抛弃的线程在钩子函数里面设置好kill，一旦有反应了立马杀死
    2、线程超时后，再将该线程的参数重新加入队列，然后再通过一个对象来存储这个参数被执行了几次，也就是超时重试次数，默认设置为3次；
    3、重写线程的is_Alive函数，默认的丫的判断的不准。

"""


class KThread(Thread):
    """A subclass of threading.Thread, with a kill()
    method.
    Come from:
    Kill a thread in Python:
    http://mail.python.org/pipermail/python-list/2004-May/260937.html
    """

    def __init__(self, *args, **kwargs):
        Thread.__init__(self, *args, **kwargs)
        self.killed = False

    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run  # Force the Thread to install our trace.
        Thread.start(self)

    def __run(self):
        """Hacked run function, which installs the
        trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        self.killed = True


class Worker(KThread):
    def __init__(self, job_queue, res_queue, worker_fun):
        """
        """
        super(Worker, self).__init__()
        self._job_queue = job_queue
        self.res_queue = res_queue
        self.worker_fun = worker_fun
        self.force_success_status = False
        self.start_time = datetime.datetime.now()
        self.args = None
        self.is_running = False

    def run(self):
        """
        """
        while True:
            try:
                self.args = self._job_queue.get(timeout=2)
                self.start_time = datetime.datetime.now()
                self.setName("thread-args-%s" % self.args)
                self.is_running = True
                res = self.worker_fun(self.args)
                if not self.force_success_status:
                    self.res_queue.put(res)
                    self._job_queue.task_done()

                    # print "run 队列消息完成+1,任务参数 %s ,未完成数量: %s" % (self.args, self._job_queue.unfinished_tasks)
                else:
                    # print "被杀之后又执行完了", self.args
                    self.is_running = False
                    return
            except Queue.Empty:
                self.is_running = False
                return
            except Exception as e:
                print "Thread error, function name is : %s, args: %s, error message is: %s" % (
                    self.worker_fun.__name__, self.args, e.message)
                print traceback.format_exc()
                self.is_running = False

    def isAlive(self):
        return self.is_running

    def force_success(self):
        """
        强制将这个线程的任务标记为完成，然后线程执行的结果就不要了。
        """
        self.force_success_status = True
        self._job_queue.task_done()
        self.kill()
        print "force_success 队列消息完成+1, 任务参数：%s ,未完成数量: %s" % (self.args, self._job_queue.unfinished_tasks)


class Super_Queue():

    def __init__(self, worker_num):
        """
        """
        self._job_queue = Queue.Queue()
        self.res_queue = Queue.Queue()
        self._worker_num = worker_num
        self._ret_data = []
        self.try_args = []

    def start(self, worker_fun, args, out_speed=True, timeout=None, try_num=3):
        """
        启动函数，支持超时参数，超时后还支持重试，默认重试3次；
        """
        # 记录输出时间
        out_text_time = int(time.time())
        out_text_interval = 10

        self._ret_data = []
        for arg in args:
            self._job_queue.put(arg)
        workers = [Worker(self._job_queue, self.res_queue, worker_fun) for i in range(self._worker_num)]
        for worker in workers:
            worker.setDaemon(True)
            worker.start()

        while True:
            done_number = 0
            # print "线程巡检======================="
            for n in range(workers.__len__()):
                worker = workers[n]
                now = datetime.datetime.now()
                runtime = (now - worker.start_time).seconds
                if worker.isAlive():
                    if isinstance(timeout, (int, float)):
                        if runtime > timeout:
                            print "线程执行超时杀死", worker.args
                            arg = worker.args
                            worker.force_success()
                            # 如果没超过重试次数，就加入队列重新重试
                            if self.try_args.count(arg) < try_num:
                                self._job_queue.put(arg)
                                self.try_args.append(arg)
                                # print "参数被加入队列进行重试：%s, 这是第%s次重试 " % (arg, self.try_args.count(arg))

                            worker_new = Worker(self._job_queue, self.res_queue, worker_fun)
                            worker_new.start()
                            workers[n] = worker_new
                else:
                    # print "完成了一个线程"
                    done_number += 1
            if done_number == workers.__len__():
                # print "所有线程都已经完成"
                break
            # print "多线程巡检一圈"
            time.sleep(1)

            if out_speed and int(time.time()) - out_text_time > out_text_interval:
                print "数据处理进度: [%s/%s]" % (self.res_queue.qsize(), len(args))
                out_text_time = int(time.time())

        while self.res_queue.qsize() > 0:
            self._ret_data.append(self.res_queue.get())
        return self._ret_data

    def get_try_number(self, arg, try_num):
        """
        判断该参数是否可以重试，看是否达到了重试限制
        """

        if arg not in self.try_args or self.try_args.count(arg) < try_num:
            self.try_args.append(arg)
            return True
        return False


if __name__ == '__main__':
    def exec_proc(v):
        time.sleep(2)
        return v


    sq = Super_Queue(10)
    args = []
    for i in range(100):
        a = {"n": i}
        args.append(a)

    res = sq.start(exec_proc, args, timeout=10)
    print "返回数量 %s" % len(res)
    res.sort()
    print "返回内容 %s" % res
    time.sleep(3)  # 等待三秒等系统回收下线程

    import os, signal, threading

    threads = threading.enumerate()
    if len(threads) > 0:
        print "发现有%s个线程残留, 执行强制杀死信号" % len(threads)
        for t in threads:
            print "线程名称" + t.getName()
        raw_input("回车后开始杀死进程")
        os.kill(os.getpid(), signal.SIGKILL)
