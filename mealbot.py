# 경덕중학교 Telegram 급식봇
# Developer : 안재범
# 
# 초기설정
# pip3 install python-telegram-bot
# pip3 install requests library
# pip3 install BeautifulSoup4 library
# pip3 install regex library
# pip3 install datetime (업데이트 위함)
#
# 실행전 봇에 아무 메시지를 보낸후 실행해야 오류 안남
# 로그기능을 원치 않는다면 로그 용량 확인및 초기화 기능과 전교회장 및 개발자에게 건의와 로그 불러오기, 로그제거 코드 제거하면 됨
#
# 봇 미리보기 https://t.me/kdmsmealbot - 텔레그램 먼저 설치하기


#텔레그램 모듈 임포트
import telegram

import os
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
import logging
import random
import urllib
import urllib3
import re
import datetime
from pytz import timezone
import time
from datetime import date, timedelta

#급식파서 임포트
from parser import *

#미세먼지 파싱을 위함
from urllib.request import urlopen
from bs4 import BeautifulSoup

meal_token = '(Your Bot token)'   #토큰을 변수에 저장합니다.

#봇 선언
bot = telegram.Bot(token = meal_token)

#커스텀 키보드 설정
custom_keyboard = [
        ["/help", "미세먼지"],
        ["어제 급식", "오늘 급식", "내일 급식"],
        ["이틀뒤 급식", "3일뒤 급식", "4일뒤 급식"],
        ]
reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)

#chat_id 아이디 설정
updates = bot.getUpdates()
chat_id = updates[-1].message.chat.id

#커스텀 키보드 설정
bot.send_message(chat_id=chat_id, text="Start 경덕중학교 급식봇, 커스텀 키보드 설정완료!",  reply_markup=reply_markup)

#시간설정
n = time.localtime().tm_wday
now = datetime.datetime.now()

#초기설정 성공 안내
print("Start 경덕중학교 급식봇")

#도움말
def help_command(bot, update) :
    update.message.reply_text("급식봇 도움말\n이 봇은 경덕중학교의 급식을 알려주는 봇입니다.\n\n<공지> 최초 개발자 : 안재범\n 소스코드(Github) : https://github.com/NewPremium/Telegram_mealbot_KDMS_2.0", reply_markup=reply_markup)
    update.message.reply_text("모든 명령어 : \n\n*도움말\n/help - 이 도움말을 표시합니다.\n\n*급식\n어제 급식 - 어제의 급식을 알려드립니다.\n오늘 급식 - 오늘의 급식을 알려드립니다.\n내일 급식 - 내일의 급식을 알려드립니다.\n이틀뒤 급식 - 이틀뒤 급식을 알려드립니다.\n3일뒤 급식 - 3일뒤 급식을 알려드립니다.\n4일뒤 급식 - 4일뒤 급식을 알려드립니다.\n\n*미세먼지\n미세 - 안동시 미세먼지 지수를 알려드립니다.\n\n*경덕중학교\n경덕중 - 경덕중학교 사이트 링크를 전송합니다.\n학생회 - 경덕중학교 학생회 페이스북 링크를 전송합니다.\n\n*포털사이트 바로가기\n구글 - 구글 링크를 전송합니다.\n네이버 - 네이버 링크를 전송합니다.\n다음 - 다음 링크를 전송합니다.\n프로톤 메일 - 프로톤메일 링크를 전송합니다.\n깃허브 - 깃허브 링크를 전송합니다.\n페이스북 - 페이스북 링크를 전송합니다.\n인스타 - 인스타그램 링크를 전송합니다.\n\n*시간, 날짜\n날짜 - 오늘의 날짜를 알려줍니다.\n시간 - 현재 시간을 알려줍니다.\n\n*chat_id\nid - 당신의 chat_id를 알려드립니다.")

#일반 메시지
def get_message(bot, update) :

    #로그 용량 확인및 초기화 (로그파일이 200GB 이상일때 초기화) - mealbot.py 파일과 같은폴더에 건의log.txt 파일을 두어야 함
    log_byte = os.path.getsize("건의log.txt")
    filesize_megabyte = log_byte / (1024.0 ** 2)
    if filesize_megabyte >= 200000:
        now = datetime.datetime.now()
        file = open("건의log.txt", 'w')
        file.write("%s년 %s월 %s일 용량초과로 로그 초기화\n"%(now.year, now.month, now.day))
        file.close()
    
    file = open("day.txt", 'r')
    dday=file.read()
    file.close()
    today = date.today()
    if not dday==today.strftime('%Y.%m.%d'):
        update.message.reply_text("서버에 급식 데이터 다운로드중. . .")

        now = datetime.datetime.now()
        n = time.localtime().tm_wday
        
        #데이터베이스 버전 업데이트
        file = open("day.txt", 'w')
        file.write(today.strftime('%Y.%m.%d'))
        file.close()

        #어제 급식 다운로드
        yester = date.today() - timedelta(1)
        if n==0:
            r=6
        else:
            r=n-1
        meal = get_diet(2, yester.strftime('%Y.%m.%d'), r)
        if meal==" ":
            meal1="급식이 없습니다."
        else:
            meal1=meal
        file = open("yester.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n어제 급식(%s) :\n\n%s" %(now.year, now.month, now.day, yester.strftime('%Y년 %m월 %d일'), meal1))
        file.close()

        #오늘 급식 다운로드
        to = date.today()
        meal = get_diet(2, to.strftime('%Y.%m.%d'), n)
        if meal==" ":
            meal1="급식이 없습니다."
        else:
            meal1=meal
        file = open("today.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n오늘 급식 :\n\n%s"%(now.year, now.month, now.day, meal1))
        file.close()

        #내일 급식 다운로드
        tomorrow = date.today() + timedelta(1)
        if n==6:
            r=0
        else:
            r=n+1
        meal = get_diet(2, tomorrow.strftime('%Y.%m.%d'), r)
        if meal==" ":
            meal1="급식이 없습니다."
        else:
            meal1=meal
        file = open("tomorrow.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n내일 급식(%s) :\n\n%s" %(now.year, now.month, now.day, tomorrow.strftime('%Y년 %m월 %d일'), meal1))
        file.close()

        #이틀뒤 급식 다운로드
        two = date.today() + timedelta(2)
        if n==5:
            r=0
        elif n==6:
            r=1
        else:
            r=n+2
        meal = get_diet(2, two.strftime('%Y.%m.%d'), r)
        if meal==" ":
            meal1="급식이 없습니다."
        else:
            meal1=meal
        file = open("2.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n이틀뒤 급식(%s) :\n\n%s"%(now.year,now.month, now.day, two.strftime('%Y년 %m월 %d일'), meal1))
        file.close()

        #3일뒤 급식 저장
        three = date.today() + timedelta(3)
        if n==4:
            r=0
        elif n==5:
            r=1
        elif n==6:
            r=2
        else:
            r=n+3
        meal = get_diet(2, three.strftime('%Y.%m.%d'), r)
        if meal==" ":
            meal1="급식이 없습니다."
        else:
            meal1=meal
        file = open("3.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n3일뒤 급식(%s) :\n\n%s"%(now.year,now.month, now.day, three.strftime('%Y년 %m월 %d일'), meal1))
        file.close()

        #4일뒤 급식 저장
        four = date.today() + timedelta(4)
        if n==3:
            r=0
        elif n==4:
            r=1
        elif n==5:
            r=2
        elif n==6:
            r=3
        else:
            r=n+4
        meal = get_diet(2, four.strftime('%Y.%m.%d'), r)
        if meal==" ":
            meal1="급식이 없습니다."
        else:
            meal1=meal
        file = open("4.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n4일뒤 급식(%s) :\n\n%s"%(now.year,now.month, now.day, four.strftime('%Y년 %m월 %d일'), meal1))
        file.close()

        update.message.reply_text("급식 데이터 다운로드 완료!")
        print ("급식 데이터가 업데이트됨 - 현재 급식 데이터베이스 버전 : %s" %today.strftime('%Y.%m.%d'))



    #어제 급식
    if update.message.text[0:2]=="어제":
        file = open("yester.txt", 'r')
        text=file.read()
        file.close()
        update.message.reply_text(text, reply_markup=reply_markup)
        
    #오늘 급식
    if update.message.text[0:2]=="오늘":
        file = open("today.txt", 'r')
        text=file.read()
        file.close()
        update.message.reply_text(text, reply_markup=reply_markup)

    #내일 급식
    if update.message.text[0:2]=="내일":
        file = open("tomorrow.txt", 'r')
        text=file.read()
        file.close()
        update.message.reply_text(text, reply_markup=reply_markup)

    #이틀뒤 급식
    if update.message.text[0:3]=="이틀뒤":
        file = open("2.txt", 'r')
        text=file.read()
        file.close()
        update.message.reply_text(text, reply_markup=reply_markup)

    #3일뒤 급식
    if update.message.text[0:3]=="3일뒤":
        file = open("3.txt", 'r')
        text=file.read()
        file.close()
        update.message.reply_text(text, reply_markup=reply_markup)

    #4일뒤 급식
    if update.message.text[0:3]=="4일뒤":
        file = open("4.txt", 'r')
        text=file.read()
        file.close()
        update.message.reply_text(text, reply_markup=reply_markup)

    #급식관련
    if update.message.text=="급식":
        update.message.reply_text("어제, 오늘, 내일, 이틀뒤 급식중에 무엇을 알려드릴까요? 아래 키보드중 하나를 눌러주세요.", reply_markup=reply_markup)

    #정보 information
    if update.message.text[0:2]=="정보":
        file = open("day.txt", 'r')
        dday=file.read()
        file.close()
        #최초개발자 수정 금지
        update.message.reply_text("<경덕중학교 급식봇 정보>\n\n급식 데이터베이스 : %s\n최초 개발자 : 안재범 (https://github.com/NewPremium)" %(dday))

    #미세먼지
    if update.message.text[0:2]=="미세":
        targetUrl = "http://aqicn.org/city/korea/gyeongbuk/andong-si/" #링크로 들어가서 자신 지역에 가장 가까운 검역소 찾은후 클릭후 링크 복붙
        html = urlopen(targetUrl).read()
        soupData = BeautifulSoup(html, 'html.parser')
        titleData = soupData.find('a', id='aqiwgttitle1')
        timeData = soupData.find('span', id='aqiwgtutime')
        aqiData = soupData.find('div', id='aqiwgtvalue')
        
        #오류없는데 정보 없음으로 나온다면 아래 if 부터 else 까지 제거바람
        if aqiData.get('title')=="Good":
            misa="좋음"
        elif aqiData.get('title')=="Moderate":
            misa="보통"
        elif aqiData.get('title')=="Unhealthy for Sensitive Groups":
            misa="민감한 사람의 건강에 해로움"
        elif aqiData.get('title')=="Very Unhealthy":
            misa="건강에 매우 해로움"
        elif aqiData.get('title')=="Hazardous":
            misa="위험"
        else:
            titleData.string="정보 없음"
            timeData.string="정보 없음"
            misa="정보 없음"
            aqiData.string="정보 없음"

        update.message.reply_text("측정 지역 : %s\n업데이트 날짜 : %s\n미세먼지 지수 : %s (%s)\nhttp://aqicn.org/ 에서 가져옴" %(titleData.string, timeData.string, misa, aqiData.string))

    #끝말잇기
    if update.message.text[0:4]=="끝말잇기":
        update.message.reply_text("네, 저부터 시작할게요.")
        update.message.reply_text("나무꾼!")

    #날짜와 시간
    if update.message.text[0:2]=="날짜":
        now = datetime.datetime.now()
        update.message.reply_text("오늘의 날짜 : \n%s년 %s월 %s일 입니다." %(now.year,now.month, now.day))

    if update.message.text[0:2]=="시간":
        now = datetime.datetime.now()
        update.message.reply_text("현재 시간 : \n%s시 %s분 %s초 입니다." %(now.hour,now.minute, now.second))

    #전교회장에게 건의
    if update.message.text[0:4]=="전교회장":
        updates=bot.getUpdates()
        chat_id = updates[-1].message.chat.id #chat_id 설정
        msgformg=update.message.text[5:]
        print("전교회장에게 건의 - %s - %s" %(chat_id, msgformg))
        file = open("건의log.txt", 'a')
        file.write("전교회장에게 건의 - %s - %s\n" %(chat_id, msgformg))
        file.close()
        bot.send_message(chat_id=(***전교회장의 chat_id - 괄호도 빼고 chat_id 입력***), text="익명으로 건의합니다! : %s" %(msgformg))
        update.message.reply_text("익명으로된 건의가 안전하게 전교회장님께 전달되었습니다. 감사합니다.\n이 작업은 취소할 수 없습니다.")

    #개발자에게 건의
    if update.message.text[0:3]=="개발자":
        updates = bot.getUpdates()
        chat_id = updates[-1].message.chat.id
        msgfordv=update.message.text[4:]
        print("개발자에게 건의 - %s - %s" %(chat_id, msgfordv))
        file = open("건의log.txt", 'a')
        file.write("개발자에게 건의 - %s - %s\n" %(chat_id, msgfordv))
        file.close()
        bot.send_message(chat_id=(***서버구축자의 chat_id, 만약 서버 구축자가 전교회장이라면 개발자에게 건의 항목은 제거바람 - 괄호도 빼고 chat_id 입력***), text="익명으로 건의합니다! : %s" %(msgfordv))
        update.message.reply_text("익명으로된 건의가 안전하게 개발자님께 전달되었습니다. 감사합니다.\n이 작업은 취소할 수 없습니다.")

    #로그 초기화
    if update.message.text[0:4]=="dlog":
        updates = bot.getUpdates()
        chat_id = updates[-1].message.chat.id #chat_id 설정
        if chat_id == (***원하는 사람의 chat_id - 전교회장같은분 - 괄호도 빼고 chat_id 입력***) or chat_id == (***원하는 사람의 chat_id - 전교회장같은분 - 괄호도 빼고 chat_id 입력***):
            now = datetime.datetime.now()
            update.message.reply_text("로그 초기화중. . .")
            file = open("건의log.txt", 'w') #로그 초기화
            file.write("%s년 %s월 %s일 - %s 로 인해 초기화됨 \n" %(now.year, now.month, now.day, chat_id))
            file.close()
            update.message.reply_text("%s년 %s월 %s일 - %s 로 인해 초기화됨 \n" %(now.year, now.month, now.day, chat_id))
        else:
            update.message.reply_text("권한이 없습니다.")
            print("%s 님은 로그에 접근 권한이 없습니다." %(chat_id))

    #로그 조회
    if update.message.text[0:3]=="log":
        updates = bot.getUpdates()
        chat_id = updates[-1].message.chat.id #chat_id 설정
        if chat_id == (***원하는 사람의 chat_id - 전교회장같은분 - 괄호도 빼고 chat_id 입력***) or chat_id == (***원하는 사람의 chat_id - 전교회장같은분 - 괄호도 빼고 chat_id 입력***):
            now = datetime.datetime.now()
            file = open("건의log.txt", 'r')
            text=file.read()
            file.close()
            update.message.reply_text("로그 내용을 불러옵니다 : \n%s" %text) #로그 내용 전송
            print("%s 님에 의해 로그가 조회됨." %(chat_id)) #터미널에 출력
        else:
            update.message.reply_text("권한이 없습니다.") #원치 않는 사람 접근시 전송
            print("%s 님은 로그에 접근 권한이 없습니다." %(chat_id))

    #포털 사이트
    if update.message.text[0:2]=="구글" or update.message.text[0:6]=="google" or update.message.text[0:6]=="Google":
        update.message.reply_text("Google\nhttps://www.google.com/")
    if update.message.text[0:3]=="네이버" or update.message.text[0:5]=="naver" or update.message.text[0:5]=="Naver":
        update.message.reply_text("Naver\nhttps://www.naver.com/")
    if update.message.text[0:3]=="깃허브" or update.message.text[0:6]=="github" or update.message.text[0:6]=="Github":
        update.message.reply_text("Github\nhttps://github.com/")
    if update.message.text[0:2]=="다음" or update.message.text[0:4]=="daum" or update.message.text[0:4]=="Daum":
        update.message.reply_text("Daum\nhttps://www.daum.net/")
    if update.message.text[0:3]=="프로톤" or update.message.text[0:6]=="proton" or update.message.text[0:6]=="Proton":
        update.message.reply_text("Proton mail\nhttps://protonmail.com/")
    if update.message.text[0:3]=="파파고" or update.message.text[0:6]=="papago" or update.message.text[0:6]=="Papago":
        update.message.reply_text("Papago\nhttps://papago.naver.com/")
    if update.message.text[0:4]=="페이스북" or update.message.text[0:8]=="facebook" or update.message.text[0:8]=="Facebook":
        update.message.reply_text("Facebook\nhttps://www.facebook.com/")
    if update.message.text[0:3]=="인스타" or update.message.text[0:6]=="insta" or update.message.text[0:6]=="Insta":
        update.message.reply_text("인스타그램\nhttps://www.instagram.com/")
    if update.message.text[0:3]=="학생회":
        update.message.reply_text("경덕중학교 학생회\nhttps://www.facebook.com/adgyeongdeok/")

    #기본 대화
    if update.message.text[0:2]=="안녕":
        update.message.reply_text("안녕하세요! 전 경덕중학교 급식봇입니다!")
    if update.message.text[0]=="넌":
        update.message.reply_text("전 경덕중학교 급식봇이라 합니다!")
    if update.message.text[0:3]=="경덕중":
        update.message.reply_text("경덕중학교 공식사이트\nhttp://school.gyo6.net/adgd/")

    #chat_id 알려주기
    if update.message.text[0:2]=="id":
        updates=bot.getUpdates()
        chat_id = updates[-1].message.chat.id
        update.message.reply_text("당신의 chat_id 는 %s 입니다." %chat_id)

    #식단 업데이트
    if update.message.text[0:4]=="업데이트":
        update.message.reply_text("서버에 급식 데이터 다운로드중. . .")

        now = datetime.datetime.now()
        n = time.localtime().tm_wday

        #데이터베이스 버전 업데이트
        file = open("day.txt", 'w')
        file.write(today.strftime('%Y.%m.%d'))
        file.close()

        #어제 급식 다운로드
        yester = date.today() - timedelta(1)
        if n==0:
            r=6
        else:
            r=n-1
        meal = get_diet(2, yester.strftime('%Y.%m.%d'), r)
        if meal==" ":
            meal1="급식이 없습니다."
        else:
            meal1=meal
        file = open("yester.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n어제 급식(%s) :\n\n%s" %(now.year, now.month, now.day, yester.strftime('%Y년 %m월 %d일'), meal1))
        file.close()

        #오늘 급식 다운로드
        to = date.today()
        meal = get_diet(2, to.strftime('%Y.%m.%d'), n)
        if meal==" ":
            meal1="급식이 없습니다."
        else:
            meal1=meal
        file = open("today.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n오늘 급식 :\n\n%s"%(now.year, now.month, now.day, meal1))
        file.close()

        #내일 급식 다운로드
        tomorrow = date.today() + timedelta(1)
        if n==6:
            r=0
        else:
            r=n+1
        meal = get_diet(2, tomorrow.strftime('%Y.%m.%d'), r)
        if meal==" ":
            meal1="급식이 없습니다."
        else:
            meal1=meal
        file = open("tomorrow.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n내일 급식(%s) :\n\n%s" %(now.year, now.month, now.day, tomorrow.strftime('%Y년 %m월 %d일'), meal1))
        file.close()

        #이틀뒤 급식 다운로드
        two = date.today() + timedelta(2)
        if n==5:
            r=0
        elif n==6:
            r=1
        else:
            r=n+2
        meal = get_diet(2, two.strftime('%Y.%m.%d'), r)
        if meal==" ":
            meal1="급식이 없습니다."
        else:
            meal1=meal
        file = open("2.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n이틀뒤 급식(%s) :\n\n%s"%(now.year,now.month, now.day, two.strftime('%Y년 %m월 %d일'), meal1))
        file.close()

        #3일뒤 급식 저장
        three = date.today() + timedelta(3)
        if n==4:
            r=0
        elif n==5:
            r=1
        elif n==6:
            r=2
        else:
            r=n+3
        meal = get_diet(2, three.strftime('%Y.%m.%d'), r)
        if meal==" ":
            meal1="급식이 없습니다."
        else:
            meal1=meal
        file = open("3.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n3일뒤 급식(%s) :\n\n%s"%(now.year,now.month, now.day, three.strftime('%Y년 %m월 %d일'), meal1))
        file.close()

        #4일뒤 급식 저장
        four = date.today() + timedelta(4)
        if n==3:
            r=0
        elif n==4:
            r=1
        elif n==5:
            r=2
        elif n==6:
            r=3
        else:
            r=n+4
        meal = get_diet(2, four.strftime('%Y.%m.%d'), r)
        if meal==" ":
            meal1="급식이 없습니다."
        else:
            meal1=meal
        file = open("4.txt", 'w')
        file.write("%s년 %s월 %s일 기준\n4일뒤 급식(%s) :\n\n%s"%(now.year,now.month, now.day, four.strftime('%Y년 %m월 %d일'), meal1))
        file.close()

        update.message.reply_text("급식 데이터 다운로드 완료!")
        print ("급식 데이터가 업데이트됨 - 현재 급식 데이터베이스 버전 : %s" %today.strftime('%Y.%m.%d'))

updater = Updater(meal_token)

message_handler = MessageHandler(Filters.text, get_message)
updater.dispatcher.add_handler(message_handler)

help_handler = CommandHandler('help', help_command)
updater.dispatcher.add_handler(help_handler)

updater.start_polling()
updater.idle()
