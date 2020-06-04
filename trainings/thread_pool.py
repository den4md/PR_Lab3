from threading import Thread, Lock


class ThreadPool:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return cls.instance

    thread_limit = 4
    thread_list = [Thread() for i in range(thread_limit)]
    for t in thread_list:
        t.start()
    lock = Lock()

    def give_task(self, target, args=()):
        with self.lock:
            while not self.approve_task(args, target):
                pass

    def approve_task(self, args, target):
        for t in self.thread_list:
            if not t.is_alive():
                self.thread_list.remove(t)
                t = Thread(target=target, args=args)
                self.thread_list.append(t)
                t.start()
                return True
        return False

    def join(self):
        with self.lock:
            for t in self.thread_list:
                t.join()
