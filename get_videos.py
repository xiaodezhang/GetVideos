# 异常存在于find函数，包括等待时间不足无法获取及弹出窗口
import requests,time,wget
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import WebDriverException
import os

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

def get_video_urls(section_start,episode_start,video_list_file):
    delay = 10
    HD_clicked = False
    url_head = "https://watchfriendsonline.net/watch/friends-"
    for section in range(section_start,11):
        url_episode1 = url_head+str(section)+"x1/"
#        print(url_episode1)
        driver.get(url_episode1)
        # 点击图标由js生成，需要等待
        time.sleep(8)
        # 获取一季的集数
        video_list = driver.find_element_by_class_name("episodios")
        lis = video_list.find_elements_by_tag_name("li")

        for episode in range(episode_start,len(lis)+1): #获取每一集
            if episode != 1:
                url_episode = url_head+str(section)+"x"+str(episode)
                driver.get(url_episode)
                time.sleep(8)
            metaframe = driver.find_element_by_class_name("metaframe")
            driver.switch_to.frame(metaframe)
            svg = driver.find_element_by_tag_name("svg")
            svg.click()

            # TODO:所有这些等待都是不准确的行为，我们需要一点点修改
            time.sleep(10)

            video_ele = driver.find_element_by_tag_name("video")
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
                setting_ele = driver.find_element_by_class_name("jw-icon-settings")
                ActionChains(driver).move_to_element(setting_ele).perform()
                setting_ele.click()
                submenu_ele = driver.find_elements_by_class_name("jw-settings-submenu")[3]
                HD_ele = submenu_ele.find_elements_by_class_name("jw-settings-content-item")[2]
#            print(HD_ele.text)
                HD_ele.click()
                HD_clicked = True

            video_url = video_ele.get_attribute("src")
            file_name = "section"+str(section)+"/S"+str(section)+"E"+str(episode)+".mp4"
            with open(video_list_file,"a") as f:
                print(file_name)
                f.write(file_name+":"+video_url+"\n")
        
#            wget.download(video_url,out=)

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

