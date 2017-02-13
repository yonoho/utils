# -*- coding: utf-8 -*-
# 新
# 本模块的目的在于抽象一些扫描日志的流程模式，减少重复代码
#
# 主要包含三类对象: 
# - Scanner: 负责遍历文件，并迭代输出 “行”
# - Filter: 负责迭代过滤和格式化 “行”
# - Processor: 负责处理 Filter 返回的数据
# 
# 基本流程就是 map(Processor, Filter(Scanner(file_path, offset)))
#
# 考虑到通常扫描日志会是一个增量定时任务，还提供了一对函数:
# - set_offset_record: 用于记录文件扫描的偏移量(字节)
# - get_offset_record: 用于读取文件扫描的偏移量(字节)
import datetime
import json
import os
import re
from logging import getLogger

try:
    from future_builtins import filter
except ImportError:
    pass


logger = getLogger('scan_log')


class LogScanner(object):
    """扫描一个文件并迭代返回行，支持字节偏移量"""
    def __init__(self, file_path, offset_bytes=0):
        self.file_path = file_path
        self.offset_bytes = offset_bytes

    def __iter__(self):
        with open(self.file_path, 'r') as f:
            self.file = f
            f.seek(self.offset_bytes, 0)
            # for line in f:  # 使用 next/__next__ 时无法使用 file.tell
            #     yield line
            #     self._refresh_offset()
            while True:
                line = f.readline()
                if line:
                    yield line
                    self._refresh_offset()
                else:
                    break

    def _unread_line(self, line):
        self.file.seek(-len(line.encode()), 1)
        self._refresh_offset()

    def _refresh_offset(self):
        self.offset_bytes = self.file.tell()


class ReFilter(object):
    """调用 re.match 过滤匹配特定正则表达式的行，
    迭代返回(pattern, line, match_result)"""
    def __init__(self, scanner, patterns):
        self.scanner = scanner
        self.patterns = patterns

    def __iter__(self):
        for line in self.scanner:
            for pattern in self.patterns:
                result = re.match(pattern, line)
                if result:
                    yield (pattern, line, result)


class TimedReFilter(object):
    """比 ReFilter 多了一个检查时间的功能
    要求表达式中含有 ?P<log_time> 命名组
    """
    def __init__(self, scanner, patterns, start, end, time_format=''):
        self.re_filter = ReFilter(scanner, patterns)
        self.start = start
        self.end = end
        self.time_format = time_format

    def __iter__(self):
        for pattern, line, result in self.re_filter:
            log_time = result.groupdict().get('log_time', '')
            if self.time_format:
                try:
                    log_time = datetime.datetime.strptime(log_time, self.time_format)
                except:
                    continue
                else:
                    if self.start and log_time < self.start:  # 过早数据，丢弃
                        pass
                    elif self.end and log_time > self.end:  # 过晚数据，不读
                        self.re_filter.scanner._unread_line(line)
                        raise StopIteration
                    else:
                        yield (pattern, line, result)


class FileDict(dict):
    def __init__(self, file_path):
        self._file_path = file_path
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                try:
                    record = json.load(f)
                except:
                    pass
                else:
                    self.update(record)

    def save(self):
        with open(self._file_path, 'w') as f:
            json.dump(self, f, sort_keys=True, indent=4)
            f.write('\n')
        return self
