# -*- coding: utf-8 -*-
import glob
import hashlib
import os
import sys
import threading
import time

import requests


class Worker:
    def __init__(self, name: str, url: str, range_start, range_end, cache_dir, finish_callback):
        self.name = name
        self.url = url
        self.cache_filename = os.path.join(cache_dir, name + ".odl")
        self.range_start = range_start  # fixed
        self.range_end = range_end  # fixed
        self.range_curser = range_start  # curser dynamic
        self.finish_callback = finish_callback
        self.terminate_flag = False
        self.FINISH_TYPE = ""  # DONE\HELP\RETIRE 

    def __run(self):
        chunk_size = 1 * 1024
        header = {
            'Range': f'Bytes={self.range_curser}-{self.range_end}', 
        }
        req = requests.get(self.url, stream=True, headers=header)

        if 200 <= req.status_code <= 299:
            with open(self.cache_filename, "wb") as cache:
                for chunk in req.iter_content(chunk_size=chunk_size):
                    if self.terminate_flag:
                        break
                    cache.write(chunk)
                    self.range_curser += len(chunk)
        if not self.terminate_flag:
            self.FINISH_TYPE = "DONE"
        req.close()
        self.finish_callback(self)

    def start(self):
        threading.Thread(target=self.__run).start()

    def help(self):
        self.FINISH_TYPE = "HELP"
        self.terminate_flag = True

    def retire(self):
        self.FINISH_TYPE = "RETIRE"
        self.terminate_flag = True

    def __lt__(self, another):
        return self.range_start < another.range_start

    def get_progress(self):
        """progress for each worker"""
        _progress = {
            "curser": self.range_curser,
            "start": self.range_start,
            "end": self.range_end
        }
        return _progress


class Downloader:
    def __init__(self, url: str, filename:str, download_dir: str, blocks_num: int = 8):
        assert 0 <= blocks_num <= 32
        self.prefix_flag = False
        if len(filename.split('/')) == 1:
            self.filename = filename
            self.prefix = ''
        else:
            self.filename = filename.split('/')[-1]
            self.prefix_flag = True
            self.prefix = os.path.dirname(filename)
        self.url = url
        self.download_dir = download_dir
        

        # self.download_dir = os.path.join(download_dir, f".{os.sep}odl{os.sep}")
        self.blocks_num = blocks_num
        self.__bad_url_flag = False
        self.file_size = self.__get_size()
        if self.file_size <= 1:
            return
        if not self.__bad_url_flag:
        # make download dir
            if not os.path.exists(self.download_dir):
                os.makedirs(self.download_dir)
                
            # make cache dir
            if self.prefix_flag:
                self.cache_dir = os.path.join(self.download_dir,self.prefix,'.cache/')
            else:
                self.cache_dir = os.path.join(self.download_dir,'.cache/')
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir)
            # print(self.url, self.file_size)
            # slicing
            self.start_since = time.time()
            # worker container
            self.workers = []  
            self.LOG = self.__get_log_from_cache() 
            self.__done = threading.Event()
            self.__download_record = []
            threading.Thread(target=self.__supervise).start()
            # main
            self.__main_thread_done = threading.Event()
            # 
            readable_size = self.__get_readable_size(self.file_size)
            pathfilename = os.path.join(self.download_dir, self.prefix,self.filename)

    def __get_size(self):
        try:
            # print(self.url)
            # req = requests.head(self.url)
            # print(req.headers)
            # content_length = req.headers["Content-Length"]
            resp = requests.get(self.url,stream=True)
            content_length = resp.headers["Content-Length"]
            # print(f"-------------{content_length}--------------")
            resp.close()
            # print(req.headers)
            # print(req.headers["Content-Length"])
            return int(content_length)
        except Exception as err:
            self.__bad_url_flag = True
            self.__whistleblower(f"[Error] {err}")
            return 0

    def __get_readable_size(self, size):
        units = ["B", "KB", "MB", "GB", "TB", "PB"]
        unit_index = 0
        K = 1024.0
        while size >= K:
            size = size / K
            unit_index += 1
        return "%.1f %s" % (size, units[unit_index])

    def __get_cache_filenames(self):
        return glob.glob(f"{self.cache_dir}{self.filename}.*.odl")

    def __get_ranges_from_cache(self):
        # like ./cache/filename.1120.odl
        ranges = []
        for filename in self.__get_cache_filenames():
            size = os.path.getsize(filename)
            if size > 0:
                cache_start = int(filename.split(".")[-2])
                cache_end = cache_start + size - 1
                ranges.append((cache_start, cache_end))
        ranges.sort(key=lambda x: x[0])
        return ranges

    def __get_log_from_cache(self):
        ranges = self.__get_ranges_from_cache()  
        LOG = []
        if len(ranges) == 0:
            LOG.append((0, self.file_size - 1))
        else:
            for i, (start, end) in enumerate(ranges):
                if i == 0:
                    if start > 0:
                        LOG.append((0, start - 1))
                next_start = self.file_size if i == len(ranges) - 1 else ranges[i + 1][0]
                if end < next_start - 1:
                    LOG.append((end + 1, next_start - 1))
        return LOG

    def __increase_ranges_slice(self, ranges: list, minimum_size=1024 * 1024):
        assert len(ranges) > 0
        block_size = [end - start + 1 for start, end in ranges]
        index_of_max = block_size.index(max(block_size))
        start, end = ranges[index_of_max]
        halfsize = block_size[index_of_max] // 2
        if halfsize >= minimum_size:
            new_ranges = [x for i, x in enumerate(ranges) if i != index_of_max]
            new_ranges.append((start, start + halfsize))
            new_ranges.append((start + halfsize + 1, end))
        else:
            new_ranges = ranges
        return new_ranges

    def __ask_for_work(self, worker_num: int):
        """ask for work, return[work_range],update self.LOG"""
        assert worker_num > 0
        task = []
        LOG_num = len(self.LOG)
        # no work now, ask for new work
        if LOG_num == 0:
            self.__share_the_burdern()
            return []
        # enough work, consume
        if LOG_num >= worker_num:  
            for _ in range(worker_num):
                task.append(self.LOG.pop(0))
        # too much work
        else:
            slice_num = worker_num - LOG_num 
            task = self.LOG
            self.LOG = []
            for _ in range(slice_num):
                task = self.__increase_ranges_slice(task)
        task.sort(key=lambda x: x[0])
        return task

    def __share_the_burdern(self, minimum_size=1024 * 1024):
        """Find the heavy worker, and introduce helper"""
        max_size = 0
        max_size_name = ""
        for w in self.workers:
            p = w.get_progress()
            size = p["end"] - p["curser"] + 1
            if size > max_size:
                max_size = size
                max_size_name = w.name
        if max_size >= minimum_size:
            for w in self.workers:
                if w.name == max_size_name:
                    w.help()
                    break

    def __give_back_work(self, worker: Worker):
        """Take unfinished work"""
        progress = worker.get_progress()
        curser = progress["curser"]
        end = progress["end"]
        if curser <= end:
            self.LOG.append((curser, end))
            self.LOG.sort(key=lambda x: x[0])

    def __give_me_a_worker(self, start, end):
        worker = Worker(name=f"{self.filename}.{start}",
                          url=self.url, range_start=start, range_end=end, cache_dir=self.cache_dir,
                          finish_callback=self.__on_worker_finish,
                        )
        return worker

    def __whip(self, worker: Worker):
        """assign new job"""
        self.workers.append(worker)
        self.workers.sort()
        worker.start()

    def __on_worker_finish(self, worker: Worker):
        assert worker.FINISH_TYPE != ""
        self.workers.remove(worker)
        # need helper
        if worker.FINISH_TYPE == "HELP":
            self.__give_back_work(worker)
            self.workaholic(2)
        # job done
        elif worker.FINISH_TYPE == "DONE":
            # get one more job
            self.workaholic(1)
        elif worker.FINISH_TYPE == "RETIRE":
            self.__give_back_work(worker)
        # Job Done, Sewing!
        if self.workers == [] and self.__get_log_from_cache() == []:
            self.__sew()

    def start(self):
        # workers assembly
        for start, end in self.__ask_for_work(self.blocks_num):
            worker = self.__give_me_a_worker(start, end)
            self.__whip(worker)
        # wait till done
        self.__main_thread_done.wait()

    def stop(self):
        for w in self.workers:
            w.retire()
        while len(self.workers) != 0:
            time.sleep(0.5)
        self.LOG = self.__get_log_from_cache()

    def workaholic(self, n=1):
        """ no work no life"""
        for s, e in self.__ask_for_work(n):
            worker = self.__give_me_a_worker(s, e)
            self.__whip(worker)

    def restart(self):
        self.stop()
        # worker assembly again!
        for start, end in self.__ask_for_work(self.blocks_num):
            worker = self.__give_me_a_worker(start, end)
            self.__whip(worker)

    def __supervise(self):
        """worker and download status supervisor"""
        REFRESH_INTERVAL = 2
        # serve as a time window-length
        LAG_COUNT = 5
        WAIT_TIMES_BEFORE_RESTART = 30
        SPEED_DEGRADATION_PERCENTAGE = 0.3
        self.__download_record = []
        maxspeed = 0
        wait_times = WAIT_TIMES_BEFORE_RESTART
        while not self.__done.is_set():
            dwn_size = sum([os.path.getsize(cachefile) for cachefile in self.__get_cache_filenames()])
            self.__download_record.append({"timestamp": time.time(), "size": dwn_size})
            if len(self.__download_record) > LAG_COUNT:
                self.__download_record.pop(0)
            s = self.__download_record[-1]["size"] - self.__download_record[0]["size"]
            t = self.__download_record[-1]["timestamp"] - self.__download_record[0]["timestamp"]
            if not t == 0:
                EPSILON = 1e-5
                speed = s / t
                readable_speed = self.__get_readable_size(speed)
                # print(s,t,readable_speed)
                percentage = self.__download_record[-1]["size"] / self.file_size * 100
                status_msg = f"\r[Current File Download Info] File Progress: {percentage:.2f} % | Speed: {readable_speed}/s | Number of Workers: {len(self.workers)} | Time Elapsed: {(time.time() - self.start_since):.0f}s | ETA: {((self.file_size- dwn_size)/(speed+EPSILON)):.2f}s"
                self.__whistleblower(status_msg)
                # speed monitor
                maxspeed = max(maxspeed, speed)
                # tolerance reached
                time_over = wait_times < 0
                # not finished yet
                not_finished = not self.__done.is_set()
                
                # still running fast enough
                speed_drops_significantly = (maxspeed - speed + EPSILON) / (maxspeed + EPSILON) > SPEED_DEGRADATION_PERCENTAGE
                speed_under_threshold = speed < 1024 * 1024
                scene_1 = speed_drops_significantly and speed_under_threshold
                # running slow
                scene_2 = speed < 100 * 1024  
                if time_over and not_finished and (scene_1 or scene_2):
                    self.__whistleblower("\r[info] speed degradation, restarting...")
                    self.restart()
                    maxspeed = 0
                    wait_times = WAIT_TIMES_BEFORE_RESTART
                else:
                    wait_times -= 1
            time.sleep(REFRESH_INTERVAL)

    def __sew(self):
        self.__done.set()
        chunk_size = 10 * 1024 * 1024
        with open(f"{os.path.join(self.download_dir, self.prefix, self.filename)}", "wb") as f:
            for start, _ in self.__get_ranges_from_cache():
                cache_filename = f"{self.cache_dir}{self.filename}.{start}.odl"
                with open(cache_filename, "rb") as cache_file:
                    data = cache_file.read(chunk_size)
                    while data:
                        f.write(data)
                        f.flush()
                        data = cache_file.read(chunk_size)
        self.clear()
        self.__whistleblower("\r")
        self.__main_thread_done.set()

    def __whistleblower(self, saying: str):
        sys.stdout.write(saying)

    def md5(self):
        chunk_size = 1024 * 1024
        filename = f"{os.path.join(self.download_dir, self.prefix, self.filename)}"
        md5 = hashlib.md5()
        with open(filename, "rb") as f:
            data = f.read(chunk_size)
            while data:
                md5.update(data)
                data = f.read(chunk_size)
        return md5.hexdigest()
    
    def clear(self):
        for filename in self.__get_cache_filenames():
            os.remove(filename)