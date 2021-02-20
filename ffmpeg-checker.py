#!/usr/bin/env python

import errno
import json
import time
from multiprocessing import Process
import requests
import subprocess

class FFmpegChecker(object):

    def __init__(self, cmd=None):
        self.cmd = cmd
        self.process = None

    def run(self, input_data=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=None):
        try:
            self.process = subprocess.Popen(
                self.cmd, shell=True, stdout=stdout, stderr=stderr, env=env
            )
        except OSError as e:
            # if e.errno == errno.ENOENT:
            #     raise FFExecutableNotFoundError(
            #         "Command run error : '{0}' ".format(self.cmd)
            #     )
            # else:
                raise

        self.process.communicate()
        returncode = self.process.returncode
        return returncode

    def getVideoInfo(self, input_data=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=None):
        try:
            self.process = subprocess.Popen(
                self.cmd, shell=True, stdin=subprocess.PIPE, stdout=stdout, stderr=stderr, env=env
            )
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise FFExecutableNotFoundError(
                    "Command run error : '{0}' ".format(self.cmd)
                )
            else:
                raise

        out,err= self.process.communicate()
        try:
            return str(err, 'utf-8')

        except Exception as ex:
            print("getVideoInfo 出现如下异常：%s"%ex)
            return ""


class FFExecutableNotFoundError(Exception):
    """Raise when FFmpeg/FFprobe executable was not found."""

class FFRuntimeError(Exception):
    """Raise when FFmpeg/FFprobe command line execution returns a non-zero exit code.

    The resulting exception object will contain the attributes relates to command line execution:
    ``cmd``, ``exit_code``, ``stdout``, ``stderr``.
    """

    def __init__(self, cmd, exit_code, stdout, stderr):
        self.cmd = cmd
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr

        message = "`{0}` exited with status {1}\n\nSTDOUT:\n{2}\n\nSTDERR:\n{3}".format(
            self.cmd, exit_code, (stdout or b"").decode(), (stderr or b"").decode()
        )

        super(FFRuntimeError, self).__init__(message)


def getPostInfo():
    postArr = [{"postId":7705502838,"videoUrl":"https://s1.zhishi.163.com/s1/media_channel_001video_202101_8f61cfecc63e0906bec59e9cc7b51dd3.mp4?internal=false&pub=false"},
               {"postId":7706291483,"videoUrl":"https://s1.zhishi.163.com/s1/media_channel_001video_20210108211233301_k51ugahldx9cxbghwjgmrkqdvyshnw.mp4?internal=false&pub=true&bucketName=rich-media-resource"},
               {"postId":7708742492,"videoUrl":"https://s1.zhishi.163.com/s1/media_channel_001video_20210117215322378_gvmm8ilhur5yujmwfjtmgjxyetgcwr.mp4?internal=false&pub=true&bucketName=rich-media-resource"},
               {"postId":7705505834,"videoUrl":"https://s1.zhishi.163.com/s1/media_channel_001video_202101_46a07597bd1659ae442cecfdcbd1ecf2.mp4?internal=false&pub=false"},
               {"postId":7705509684,"videoUrl":"https://s1.zhishi.163.com/s1/media_channel_001video_202101_756805b174d04479223002f0b7f89338.mp4?internal=false&pub=false"},
               {"postId":7705508732,"videoUrl":"https://s1.zhishi.163.com/s1/media_channel_001video_202101_03f092d37d6edb648fafa2a8d20d92d3.mp4?internal=false&pub=false"},
               {"postId":7705506864,"videoUrl":"https://s1.zhishi.163.com/s1/media_channel_001video_202101_4c190d3cd5e0937cb040b6d7e5593d36.mp4?internal=false&pub=false"}]
    return postArr

def haveTextRuleWords(textRules, videoInfo):
    if (textRules != []):
        for item in textRules:
            if item in videoInfo:
                return True
    return False

def getDuration(videoInfo):
    try:

        duration = videoInfo.split("Duration: ")[1].split(",")[0].split(".")[0]
        hour, minute, second = duration.split(":")
        timeinsecond = float(second) + float(minute) * 60 + float(hour) * 60 * 60
        return int(timeinsecond)
    except Exception as ex:
        # print("getDuration 出现如下异常：%s" % ex)
        return 0


def ffmpegCheck(initialId,fileName,textRules):
    pageSize = 10
    id = initialId
    cmdForCheck = "ffmpeg -ss {} -t {} -v error -i \"{}\" -f null -"
    cmdForVideoInfo = "ffmpeg -i \"{}\" "


    while (1):
        try:
            postArr = getPostInfo()
            id = res['id']
            if postArr:
                for post in postArr:
                    #重置status
                    status = 0
                    #播放时间
                    playTime = 2
                    #未检测状态码为-100
                    checkResCode = -100
                    #获取视频头信息
                    VideoInfoGetter = FFmpegChecker(cmdForVideoInfo.format(post["videoUrl"]))
                    videoInfo = VideoInfoGetter.getVideoInfo()
                    if haveTextRuleWords(textRules, videoInfo):
                        status = 2
                    else:
                        duration = getDuration(videoInfo)
                        if duration <= 0:
                            status = 2
                        else:
                            startTime = duration - playTime
                            startTimeStr = str(int(startTime / 3600)) + ":" + str(int(startTime % 3600 / 60)) + ":" + str(startTime % 3600 % 60)

                            #抽样检查
                            checker = FFmpegChecker(cmdForCheck.format(startTimeStr,str(playTime),post["videoUrl"]))
                            checkResCode = checker.run()
                            if (checkResCode in [0]):
                                status = 1
                            else:
                                status = 2

                    # 暂时先写在本地
                    if status == 2:
                        print("postId:" + str(post["postId"]) + "  fail:" + str(checkResCode))
                        with open(fileName, "a") as ErrorFile:
                            ErrorFile.write("fail="+str(checkResCode) + " - " +str(post['postId']) +" - "+post["videoUrl"] + "\n")
                            ErrorFile.close()
                    elif status == 1:
                        print("postId:" + str(post["postId"]) + "  success:" + str(checkResCode))
        except Exception as ex:
            print("出现如下异常%s" %ex)
            pass

class Process_Class(Process):
    def __init__(self, initialId,fileName,textRules):
        Process.__init__(self)
        self.initialid = initialId
        self.fileName = fileName
        self.textRules = textRules

    def run(self):
        while 1:
            try:
                ffmpegCheck(self.initialid,self.fileName,self.textRules)

            except Exception as ex:
                print("出现如下异常%s" % ex)
                pass




if __name__ == "__main__":
    # textRules 为视频头信息过滤的指定字符串，规则可配置
    # textRules = ["quicktime"]
    textRules = []

    # ffmpegCheck(55000, "videosWithError.txt", textRules)



    print("主进程开始")
    p1 = Process_Class(10070,"videosWithError1.txt",textRules)
    p2 = Process_Class(70330,"videosWithError2.txt",textRules)
    p3 = Process_Class(124320,"videosWithError3.txt",textRules)
    p4 = Process_Class(188040,"videosWithError4.txt",textRules)


    p1.start()
    p2.start()
    p3.start()
    p4.start()
