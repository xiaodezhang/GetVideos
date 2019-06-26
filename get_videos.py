# 异常存在于find函数，包括等待时间不足无法获取及弹出窗口
import requests,time,wget
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
import os
import configparser
import time
import queue
import threading

config = configparser.ConfigParser()
episode_num = {}
episode_downloaded_num = {}
videos_downloaded = []
urls_got = []

videos_not_downloaded = []
urls_not_got = []
# we shall make our program continue after a long running due to broken.
# so a config file will work to record our messages we already got.
def get_videos_init():
    config.read('get_video.ini')
    for i in range(10):
        section_name = 'section'+str(i+1)
        num = 0
        for key in config['EPISODE_NUM']:
            if section_name == key:
                num = int(config['EPISODE_NUM'][key])
                break;
        episode_num[section_name] = num

        downloaded_num = 0
        for key in config['VIDEOS_DOWNLOADED']:
            if key.startswith(section_name):
                downloaded_num += 1
        episode_downloaded_num[section_name] = downloaded_num

    for key in config['URLS_GOT']:
        urls_got.append({key:config['URLS_GOT'][key]})
    for key in config['VIDEOS_DOWNLOADED']:
        videos_downloaded.append(key)

#    print(urls_got)
#    print(episode_num,'\n',episode_downloaded_num)
#    print(episode_num,videos_downloaded,urls_got)


class DownloadVideos(threading.Thread):
    def __init__(self,q):
        threading.Thread.__init__(self)
        self._queue = q

    def run(self):
        while True:
            try:
                msg_url = self._queue.get(False)
                #wget.download(msg_url,out=)
            except queue.Empty:
                print("All videos downloaded")
                break;


def videos_downloaded_list(video_list_file):
    try:
        f = open(video_list_file)
        lines = f.readlines()
        f.close()
        if len(lines) == 0:
            return 1,1
        else:
            last_line = lines[-1]
#            print(last_line[last_line.find('S')+1],last_line[last_line.find('E')+1])
            return int(last_line[last_line.find('S')+1]),int(last_line[last_line.find('E')+1])
    except IOError:
        open(video_list_file,"w+")
        f.close()
        return 1,1

def get_video_urls():
    delay = 10
    HD_clicked = False
    url_head = "https://watchfriendsonline.net/watch/friends-"
    driver = webdriver.Chrome()
    #for video in videos_downloaded:

    for section in episode_num:
        if episode_downloaded_num[section] > episode_num[section]:
            print("dowloaded videos's number bigger than the sections number,section:%d" % section)
            continue
        if episode_downloaded_num[section] == episode_num[section]:
            continue
        just_in_episode1 = False
        if episode_num[section] == 0:
            #获取一季的集数
            if section == 'section10':
                url_episode1 = url_head+"10"+"x1/"
            else:
                url_episode1 = url_head+section[-1]+"x1/"
            driver.get(url_episode1)
            # 点击图标由js生成，需要等待
            time.sleep(8)
            video_list = driver.find_element_by_class_name("episodios")
            lis = video_list.find_elements_by_tag_name("li")
            episode_num[section] = len(lis)
            #这个值在获取第一集的时候避免切换url
            just_in_episode1 = True

        #获取一季的每一集
        for episode in range(episode_downloaded_num[section]+1,episode_num[section]+1):
            if episode != 1 or just_in_episode1 == False:
                if section == 'section10':
                    url_episode = url_head+"10x"+str(episode)
                else:
                    url_episode = url_head+section[-1]+"x"+str(episode)
                driver.get(url_episode)
                time.sleep(8)
            metaframe = driver.find_element_by_class_name("metaframe")
            driver.switch_to.frame(metaframe)
            svg = driver.find_element_by_tag_name("svg")
            svg.click()

            # TODO:所有这些等待都是不准确的行为，我们需要一点点修改
            time.sleep(15)

            video_ele = driver.find_element_by_tag_name("video")
            print(video_ele.get_attribute("src"))
            # 选择高清视频
            if HD_clicked == False:
                # 鼠标悬浮使得设置图标可见
                try:
                    ActionChains(driver).move_to_element(video_ele).perform()
                except WebDriverException:
                    # TODO:这里希望点掉弹出窗口，但是并不能成功，测试比较麻烦，我们直接
                    # 重新获取好了
                    pop_close = driver.find_element_by_id("AdskeeperC206856Popup-close-btn")
                    pop_close.click()
                ActionChains(driver).move_to_element(video_ele).perform()
                setting_ele = driver.find_element_by_class_name("jw-svg-icon-settings")
                print("move to element\n")
#                ActionChains(driver).move_to_element(video_ele).perform()
#                time.sleep(1)
                print("setting click\n")
                ActionChains(driver).move_to_element(video_ele).perform()
                setting_ele.click()
                submenu_ele = driver.find_elements_by_class_name("jw-settings-submenu")[3]
                HD_ele = submenu_ele.find_elements_by_class_name("jw-settings-content-item")[2]
#            print(HD_ele.text)
                HD_ele.click()
                HD_clicked = True

            video_url = video_ele.get_attribute("src")
            file_name = "section"+str(section)+"/S"+str(section)+"E"+str(episode)+".mp4"
            # with open(video_list_file,"a") as f:
                # print(file_name)
                # f.write(file_name+":"+video_url+"\n")
        
            print(file_name,':',video_url)
#            wget.download(video_url,out=)
    driver.close()

def get_vides_wrapper():
    video_list_file = 'video_list'
    section_downloaded,episode_downloaded = videos_downloaded_list(video_list_file)
    while(section_downloaded != 10 and episode_downloaded != 10):
        try:
            driver = webdriver.Chrome()
            # 目前每一季的集数并不清楚，需要从已获得的下载地址网址中重新获取，为了方便，我们不多做处理
            # 而是在加入视频地址列表的时候去掉重复项。
            get_video_urls(section_downloaded,episode_downloaded,video_list_file)
            driver.close()
        except:
        #    print(str(e))
#        print("section"+str(section_downloaded+1)+"episode"+str(episode_downloaded+1)+" download failed,retry...")
            driver.close()
            section_downloaded,episode_downloaded = videos_downloaded_list(video_list_file)
            continue

def get_section_episodes_num():
    print(1)

if __name__ == '__main__':
    get_videos_init()
    get_video_urls()
