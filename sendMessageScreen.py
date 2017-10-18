from utils import *
import os
from threading import Thread,Timer
import time
import messageListScreen
from PIL import Image
import requests
from io import BytesIO
import imageToAnsi
import sys
import principalScreen

inputToSend = Buffer()

def printLoop(client,buffer,session):
    try:
        while not client.isStopThread():
            reprintScreen(client, buffer, inputToSend)
            time.sleep(0.5)
    except KeyboardInterrupt:
        client.stopThread()
        messageListScreen.openScreen(client, session)

def receive(client,buffer):
    threadName = client.getThreadName()
    while not client.isStopThread():

        #buffer.addToBuffer('test\n')
        #reprintScreen(client,buffer,inputToSend)
        while (client.isThereMessage()):
            #print('\n[' + threadName + ']: ' + client.getMessage())
            buffer.addToBuffer('[' + threadName + ']: ' + client.getMessage() + '\n')
            reprintScreen(client, buffer, inputToSend)
        #time.sleep(0.2)

def send(client,session,thread,buffer):
    try:
        while not client.isStopThread():
            # print('[' + client.getUser().name + ']: ', end='', flush=True)
            inputToSend.clearBuffer()
            reprintScreen(client, buffer, inputToSend)
            while True:
                c = getchar()
                if ord(c) == 13 or ord(c) == 10:
                    break
                if ord(c) == 3:
                    client.stopThread()
                    messageListScreen.openScreen(client, session)

                inputToSend.addChar(c)
                reprintScreen(client, buffer, inputToSend)
                # toSendMessage += repr(c)
            # toSendMessage = input('[' + client.getUser().name + ']: ')
            buffer.addToBuffer('[' + client.getUser().name + ']: ' + inputToSend.getBuffer() + '\n')
            if inputToSend.getBuffer() == '/exit':
                client.stopThread()
                messageListScreen.openScreen(client, session)
                break
            client.sendMessage(inputToSend.getBuffer(), thread_id=thread.uid, thread_type=thread.type)
    except KeyboardInterrupt:
        client.stopThread()
        messageListScreen.openScreen(client, session)


def reprintScreen(client,buffer,inputBuffer):
    console_clear()
    print(buffer.getBuffer(), end='', flush=True)
    print('[' + client.getUser().name + ']: ', end='', flush=True)
    print(inputToSend.getBuffer(), end='', flush=True)


def printImage(image):
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            p = image.getpixel((x, y))
            h = "%2x%2x%2x" % (p[0], p[1], p[2])
            short, rgb = imageToAnsi.rgb2short(h)
            sys.stdout.write("\033[48;5;%sm " % short)
        sys.stdout.write("\033[0m\n")
    sys.stdout.write("\n")


def openScreen(client,session,thread):
    buffer = Buffer()

    doPrintImage = False
    if thread is not None:
        messages = client.fetchThreadMessages(thread_id=thread.uid, limit=10)
        console_clear()
        buffer.addToBuffer('---- Type /exit to get back to messages list menu ----\n')
        print('---- Type /exit to get back to messages list menu ----')
        try:
            for msg in reversed(messages):
                toPrintMsg = '['+client.fetchThreadInfo(msg.author)[msg.author].name+']: '+toUTF8(msg.text)
                print(toPrintMsg)
                buffer.addToBuffer(toPrintMsg+'\n')
                try:
                    if msg.attachments:
                        if doPrintImage:
                            response = requests.get(msg.attachments[0]['preview']['uri'])
                            img = Image.open(BytesIO(response.content))
                            baseheight = 22
                            basewidth = 20
                            img = img.resize((basewidth, baseheight), Image.ANTIALIAS)
                            printImage(img)
                        else:
                            print('{attachment}: ',msg.attachments[0]['preview']['uri'])
                            buffer.addToBuffer('{attachment}: '+msg.attachments[0]['preview']['uri']+'\n')
                    if msg.extensible_attachment is not None:
                        if doPrintImage:
                            uriPreview = msg.extensible_attachment['story_attachment']['media']['image']['uri']
                            response = requests.get(uriPreview)
                            img = Image.open(BytesIO(response.content))
                            baseheight = 22
                            basewidth = 20
                            img = img.resize((basewidth, baseheight), Image.ANTIALIAS)
                            printImage(img)
                        else:
                            uriVideo = msg.extensible_attachment['story_attachment']['media']['playable_url']
                            print('{attachment}: ', uriVideo)
                            buffer.addToBuffer('{attachment}: '+ uriVideo+'\n')
                except:
                    pass

            client.startThread(thread.uid)
            receiveThread = Thread(target=receive, args=(client,buffer,))
            receiveThread.deamon = True
            receiveThread.start()
            sendThread = Thread(target=send, args=(client,session,thread,buffer,))
            sendThread.deamon = True
            sendThread.start()
            #printThread = Thread(target=printLoop, args=(client,buffer,session,))
            #printThread.deamon = True
            #printThread.start()
            client.listen()

        except KeyboardInterrupt:
            client.stopThread()
            messageListScreen.openScreen(client,session)

    else:
        users = {}
        for u in client.fetchAllUsers():
            users[u.uid] = u.name
        users[client.uid] = client.fetchThreadInfo(client.uid)[client.uid].name

        console_clear()
        buffer.addToBuffer('---- Type /exit to get back to the main menu ----\n')
        print('---- Type /exit to get back to the main menu ----')
        print('search for a user: ',end='',flush=True)
        buffer.addToBuffer('search for a user: ')
        inputToSend.clearBuffer()
        reprintScreen(client, buffer, inputToSend)
        while True:
            c = getchar()
            if ord(c) == 13 or ord(c) == 10:
                break
            if ord(c) == 3:
                principalScreen.openScreen(client, session)
            inputToSend.addChar(c)
            reprintScreen(client, buffer, inputToSend)
        buffer.addToBuffer('[' + client.getUser().name + ']: ' + inputToSend.getBuffer() + '\n')
        if inputToSend.getBuffer() == '/exit':
            principalScreen.openScreen(client, session)
        else:
            print('todo')
