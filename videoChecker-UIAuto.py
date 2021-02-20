# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re
import requests,json


class AppDynamicsJob(unittest.TestCase):
    def setUp(self):
        # AppDynamics will automatically override this web driver
        # as documented in https://docs.appdynamics.com/display/PRO44/Write+Your+First+Script
        # self.driver = webdriver.Firefox()
        chrome_driver = 'C:\Program Files\Google\Chrome\Application\chromedriver.exe'  # chromedriver的文件位置
        self.driver = webdriver.Chrome(executable_path=chrome_driver)
        self.driver.implicitly_wait(5)
        self.base_url = "https://www.lofter.com/"
        self.verificationErrors = []
        self.accept_next_alert = True

    def test_app_dynamics_job(self):
        initialNum = 50
        initialId  = 80000
        driver = self.driver
        driver.get("https://***/front/login")
        driver.find_element_by_link_text(u"邮箱").click()
        iframe = driver.find_element_by_tag_name('iframe')
        self.driver.switch_to.frame(iframe)

        driver.find_element_by_name("email").click()
        driver.find_element_by_name("email").clear()
        driver.find_element_by_name("email").send_keys("***")
        time.sleep(1)
        driver.find_element_by_name("password").click()
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys("***")
        time.sleep(0.9)
        driver.find_element_by_xpath("//span/input").click()
        time.sleep(1)
        driver.find_element_by_id("dologin").click()
        time.sleep(5)


        # driver.get("http://127.0.0.1:8080/")
        driver.get(r"https://******/videoChecker.html")
        resetNum = initialNum
        id=initialId
        while(1):
            try:
                postArr = self.getPostInfo()
                #res = self.getPostInfo()
                #postArr = res['list']
                #id = res['id']
                for post in postArr:
                    # 输入待检测视频url
                    if(resetNum <= 0):
                        resetNum = 50
                        driver.refresh()
                        # self.test_app_dynamics_job()
                    driver.find_element_by_id("video-url").click()
                    driver.find_element_by_id("video-url").clear()
                    driver.find_element_by_id("video-url").send_keys(post["videoUrl"])
                    # 输入爬取记录ID，用于结果上报。
                    driver.find_element_by_id("crawling-id").click()
                    driver.find_element_by_id("crawling-id").clear()
                    driver.find_element_by_id("crawling-id").send_keys(post["id"])
                    # 输入待检测视频文章ID，用于结果上报。
                    driver.find_element_by_id("post-id").click()
                    driver.find_element_by_id("post-id").clear()
                    driver.find_element_by_id("post-id").send_keys(post["postId"])
                    # 点击播放
                    driver.find_element_by_id("play-btn").click()
                    time.sleep(3)
                    driver.refresh()
                    resetNum = resetNum - 1
            except Exception as ex:

                print("出现如下异常%s" % ex)
                pass

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        # To know more about the difference between verify and assert,
        # visit https://www.seleniumhq.org/docs/06_test_design_considerations.jsp#validating-results
        self.assertEqual([], self.verificationErrors)

    # 获取数据
    def getPostInfo():
        postArr = [{"postId":7705502838,"videoUrl":"https://s1.zhishi.163.com/s1/media_channel_001video_202101_8f61cfecc63e0906bec59e9cc7b51dd3.mp4?internal=false&pub=false"},
                   {"postId":7706291483,"videoUrl":"https://s1.zhishi.163.com/s1/media_channel_001video_20210108211233301_k51ugahldx9cxbghwjgmrkqdvyshnw.mp4?internal=false&pub=true&bucketName=rich-media-resource"},
                   {"postId":7708742492,"videoUrl":"https://s1.zhishi.163.com/s1/media_channel_001video_20210117215322378_gvmm8ilhur5yujmwfjtmgjxyetgcwr.mp4?internal=false&pub=true&bucketName=rich-media-resource"},
                   {"postId":7705505834,"videoUrl":"https://s1.zhishi.163.com/s1/media_channel_001video_202101_46a07597bd1659ae442cecfdcbd1ecf2.mp4?internal=false&pub=false"},
                   {"postId":7705509684,"videoUrl":"https://s1.zhishi.163.com/s1/media_channel_001video_202101_756805b174d04479223002f0b7f89338.mp4?internal=false&pub=false"},
                   {"postId":7705508732,"videoUrl":"https://s1.zhishi.163.com/s1/media_channel_001video_202101_03f092d37d6edb648fafa2a8d20d92d3.mp4?internal=false&pub=false"},
                   {"postId":7705506864,"videoUrl":"https://s1.zhishi.163.com/s1/media_channel_001video_202101_4c190d3cd5e0937cb040b6d7e5593d36.mp4?internal=false&pub=false"}]
        return postArr



if __name__ == "__main__":
    while(1):
        try:
           unittest.main()

        except Exception as ex:

            print("出现如下异常%s" % ex)
            errNum = errNum + 1
            print(errNum)
            pass
