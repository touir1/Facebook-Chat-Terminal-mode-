from utils import *
import messageListScreen
import sendMessageScreen
import unreadMessageScreen


def openScreen(client, session):
    choice = 0
    while choice<1 or choice>3:
        console_clear()
        print('choose a number:')
        print('1- open message list')
        #print('2- open unread messages')
        print('2- send a message')
        print('3- exit')
        choice = to_int(input('\nchoice: '))

    if choice == 3:
        quit()
    elif choice ==1:
        messageListScreen.openScreen(client, session)
    #elif choice ==2:
    #    unreadMessageScreen.openScreen(client, session)
    elif choice ==2:
        sendMessageScreen.openScreen(client=client, session=session)
