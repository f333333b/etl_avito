#fishing.py автобот для ловли рака в русской рыбалке
import keyboard
import mouse
import pyautogui
import pygetwindow
import time
import random


def window_active():
    # Функция проверяет активность окна и запоминает текущее окно, затем переключается на рыбалку
    global flagWindow, window1, windowLast, windowGame, flagChangeWindow
    global posPotionX, posPotionY
    if not flagChangeWindow:
        return None
    try:
        if not windowGame.isActive:
            flagWindow = True
            window1 = pyautogui.getActiveWindowTitle()
            windowLast = pygetwindow.getWindowsWithTitle(window1)[0]
            windowGame.activate()
            time.sleep(0.1)
    except Exception as e:
        print('ERROR: ',e)
        x,y = mouse.get_position()
        mouse.move(posPotionX, posPotionY)
        mouse.click()
        mouse.move(x,y)
        error_debug()
        time.sleep(0.5)
        


def window_last():
    # Функция переключается на последнее активное окно
    global flagWindow, window1, windowLast, windowGame, flagChangeWindow
    if not flagChangeWindow:
        return None
    try:
        if flagWindow == True:
            flagWindow = False
            windowLast.activate()
            time.sleep(0.1)
    except Exception as e:
        print('ERROR: ',e)
        error_debug()
        time.sleep(0.5)


def window_drag_full(full = True):
    # Функция для перемещения окна игры по оси Х, если его не видино полностью
    global dragFull
    
    # Если окно выходит за пределы экрана
    if dragFull > 0:
        global posMapX,posPotionX,posPotionY,posBaseButtonX
        global posHelloButtonX, posMenuButtonX,posTripButtonX
        global posIsBaseX,posIsEatX
        posMouseLastX, posMouseLastY = mouse.get_position()
        time.sleep(1)
        
        # Если full == True вытаскиваем окно, для полной видимости и меняем координаты позиций кнопок
        if full:
            mouse.drag(posPotionX,posPotionY,posPotionX-dragFull,posPotionY,True,0.01)
            posPotionX -= dragFull
            posMapX -= dragFull
            posMenuButtonX -= dragFull
            posHelloButtonX -= dragFull
            posBaseButtonX -= dragFull
            posTripButtonX -= dragFull
            posIsBaseX[0] -= dragFull
            posIsBaseX[1] -= dragFull
            posIsEatX -= dragFull
            
        # Если full == False возвращаем окно на прежнюю позицию и меняем координаты позиций кнопок
        else:
            mouse.drag(posPotionX,posPotionY,posPotionX+dragFull,posPotionY,True,0.01)
            posPotionX += dragFull
            posMapX += dragFull
            posMenuButtonX += dragFull
            posHelloButtonX += dragFull
            posBaseButtonX += dragFull
            posTripButtonX += dragFull
            posIsBaseX[0] += dragFull
            posIsBaseX[1] += dragFull
            posIsEatX += dragFull
            
        mouse.move(posMouseLastX, posMouseLastY)
        time.sleep(2)



def error_debug():
    # Функция отладки ошибок
    global countError, posPotionX, posPotionY, flagChangeWindow
    countError += 1
    
    # Отключение авто смены окон
    # и единоразовая активация окна игры мышью
    if countError >= 10:
        time.sleep(0.5)
        posMouseLastX, posMouseLastY = mouse.get_position()
        countError = 0
        flagChangeWindow = False
        print('Смена окон: ОТКЛЮЧЕНА')
        mouse.move(posPotionX, posPotionY)
        mouse.click()
        time.sleep(0.5)
        mouse.move(posMouseLastX, posMouseLastY)
    else:
        return None
    

def game_locate_initialization():
    # Функия инициализации переменных относительно локации и типа рыбалки
    time.sleep(0.45)
    
    global windowGame,fishingLocate,fishingType,fishingShotNum,posLocateMapX,posLocateMapY,posAimX,posAimY
    global colorAim,nameAim,flagAutoPosition,color,posX,posY,posFloatBiteX,posFloatBiteY,X1,Y1,quantR

    # Определение окна игры в переменную
    # 0 - вылов рака на деме, 1 - вылов головастика, Днепр-Киев
    try:
        #window1 = pygetwindow.getWindowsWithTitle('Select game mode')[0]
        if fishingLocate == 0:
            windowGame = pygetwindow.getWindowsWithTitle('Дема: Лягушачья заводь')[0]
        
        if fishingLocate == 1:
            windowGame = pygetwindow.getWindowsWithTitle('Днепр-Киев: Тишина')[0]
        
    except Exception as e:
        print('ERROR: ',e)
        time.sleep(1)


    # Определение координат заброса, цвета пикселя
    # И получение координат локации на карте


    if fishingLocate == 0:
        
        #Кнопка локации на карте: Дема: Лягушачья заводь
        posLocateMapX,posLocateMapY = 1130,311
        
        # Координаты и цвет пикселя для подтверждения пойманного рака в открытом садке(клешня) и переменная имени
        posAimX, posAimY = 1083,394
        colorAim = (94,86,65)
        nameAim = 'рак'

    elif fishingLocate == 1:
        #Кнопка локации на карте: Днепр-Киев: Тишина
        posLocateMapX,posLocateMapY = 978,348
        
        # Координаты и цвет пикселя для подтверждения пойманного головастика в открытом садке(хвост) и переменная имени
        posAimX, posAimY = 1119,340
        colorAim = (109,154,135)
        nameAim = 'головастик'
    
    if flagAutoPosition:
        
        # координаты заброса для Дема: Лягушачья заводь 
        if fishingLocate == 0:
            
            # координаты заброса 0,33_11 на рака, точка заброса красн.
            if fishingShotNum == 0:
                pos_shot(X1+260, Y1-203)
                
            # координаты заброса 0,40_4 на рака, точка заброса красн.
            if fishingShotNum == 1:
                pos_shot(X1+54, Y1-216)
            
        # координаты заброса для Днепр-Киев: Тишина          
        if fishingLocate == 1:
            
            # координаты заброса поплавка 3.00 на головастика
            if fishingShotNum == 0:
                pos_shot(X1+476, Y1-263)
                    
    else:
            
        # Заброс в ручном режиме 
        print('Нажмите правой кнопкой мыши поочередно на 3 точки заброса')
        for i in range(quantR):
            
            # Координаты для индекса точки заброса
            posX[i],posY[i] = pos_cursor(str(i+1))
            
            # Координаты для поплавка, точка поклевки
            if fishingType == 1:
                posFloatBiteX[i],posFloatBiteY[i] = posX[i],posY[i]-1

    if fishingType == 1:
        # Красный
        color[0] = (181, 8, 8)
        # Белый
        color[1] = (255,255,255)
    elif fishingType == 2:
        # Красный
        color[0] = (233,0,0)
        
    time.sleep(0.45)



def game_menu_launch(changeServer = False):
    # Запуск игры из меню до перехода на локу
    global posMenuX1,posMenuY1,posHelloButtonX, posHelloButtonY
    global timeServerReload,countServerReload,serverNumber
    global posMenuServerX1,posMenuServerY1,posMenuServerX2,posMenuServerY2,posMenuServerX3,posMenuServerY3
    sl = 3
    time.sleep(sl)
    posMouseLastX, posMouseLastY = mouse.get_position()
    
    # Проверка 3 пикселей заставки меню по цвету
    if pyautogui.pixelMatchesColor(665, 600,(13, 88, 94)) and pyautogui.pixelMatchesColor(700, 400,(195, 109, 148)) and pyautogui.pixelMatchesColor(740, 630,(255, 203, 1)):
        
        # При перезаходе в игру 3 раза подряд менее чем за 120 сек = выход
        if countServerReload >= 3:
            if (time.time-timeServerReload)<=120:
                print('Частый перезаход на сервер.Выход')
                exit()
            countServerReload = 0
            timeServerReload = time.time()
        countServerReload += 1
            
        # Кнопка "Начать игру"
        mouse.move(posMenuX1, posMenuY1)
        mouse.click()
        time.sleep(sl*3)
        
        # Выбор сервера
        if changeServer:
            if serverNumber >= 3:
                serverNumber = 1
            else:
                serverNumber += 1
        if serverNumber == 1:
            mouse.move(posMenuServerX1,posMenuServerY1)
        elif serverNumber == 2:
            mouse.move(posMenuServerX2,posMenuServerY2)
        else:
            mouse.move(posMenuServerX3,posMenuServerY3)
        mouse.double_click()
        time.sleep(sl)
        
        # Кнопка авторизации, лог и пасс
        mouse.move(944, 564)
        mouse.click()
        time.sleep(sl*5)
        
        # Кнопка приветствие
        mouse.move(posHelloButtonX, posHelloButtonY)
        mouse.click()
        time.sleep(sl)
                    
    else:
        print('Не вышло обнаружить меню. Выход')
        exit()
    mouse.move(posMouseLastX, posMouseLastY)
    
    
def game_menu_exit():
    # Выход в меню игры
    global posMenuButtonX, posMenuButtonY
    sl = 3
    time.sleep(sl)
    posMouseLastX, posMouseLastY = mouse.get_position()
    
    # Кнопка "Меню"
    mouse.move(posMenuButtonX, posMenuButtonY)
    mouse.click()
    time.sleep(sl)
    
    # Кнопка "В главное меню"
    mouse.move(960, 550)
    mouse.click()
    time.sleep(sl)
    
    # Кнопка подтверждения "Выход"
    mouse.move(960, 580)
    mouse.click()
    time.sleep(sl*5)
    mouse.move(posMouseLastX, posMouseLastY)


def game_reload(changeServer = False):
    # Функция перезапуска игры, с возможностью смены сервера
    time.sleep(3)
    window_active()
    posMouseLastX, posMouseLastY = mouse.get_position()
    rod_withdraw_all()
    window_drag_full(True)
    game_menu_exit()
    game_menu_launch(changeServer)
    game_to_locate()
    window_drag_full(False)
    rod_rope_all()
    mouse.move(posMouseLastX, posMouseLastY)
    window_last()   

  
def game_server_break():
    # Функция "обрыва связи с сервером", с перезаходом на тот же
    global countServerBreak
    posMouseLastX, posMouseLastY = mouse.get_position()
    
    # проверка цвета по координатам в 3 местах, для подтв. окна ошибки
    if pyautogui.pixelMatchesColor(939, 531, (57, 143, 219)):
        if pyautogui.pixelMatchesColor(972, 534, (182, 255, 255)):
            if pyautogui.pixelMatchesColor(1007,533,(255, 182, 102)):
                
                # нажатие кнопки "ОК" в окне ошибки
                mouse.move(1020,590)
                mouse.click()
                time.sleep(30)
                
                
                # перезаход в игру
                countServerBreak += 1
                game_menu_launch()
                window_drag_full(True)
                game_to_locate()
                window_drag_full(False)
                rod_rope_all()
                mouse.move(posMouseLastX, posMouseLastY)
    else:
        return None
        

def game_to_locate():
    # Переход на локацию
    global posMapX,posMapY,posLocateMapX,posLocateMapY
    time.sleep(1)
    posMouseLastX, posMouseLastY = mouse.get_position()
    
    # Кнопка карты
    mouse.move(posMapX,posMapY)
    mouse.click()
    time.sleep(3)
        
    # Кнопка локации
    mouse.move(posLocateMapX,posLocateMapY)
    mouse.click()
    mouse.move(posMouseLastX, posMouseLastY)
    time.sleep(9)
    

def locate_position(NumMap):
    # получение координат локации на карте
    if NumMap == 0:
        #Кнопка локации на карте: Дема: Лягушачья заводь
        return 1130,311
    elif NumMap == 1:
        #Кнопка локации на карте: Днепр-Киев: Тишина
        return 978,348
    else:
        print(NumMap," карта не существует в функции")
        return 0,0

def game_trip_end_check():
    # Функция проверяет наличие таблички окончание путевки
    global fishingTrip
    if fishingTrip > 0:
        global flagTripEnd
        if not flagTripEnd:
            global posTripEndX,posTripEndY,colorTripEnd
            for i in range(3):
                if not pyautogui.pixelMatchesColor(posTripEndX[i],posTripEndY[i],colorTripEnd[i]):
                    return None
            # Если находимся на доступной базе, продлеваем  пребывание на 1 день, нажатием
            if fishingTrip == 1:
                time.sleep(0.2)
                posMouseLastX, posMouseLastY = mouse.get_position()
                window_active()
                time.sleep(0.2)
                # Клик на кнопку продления
                mouse.move(posTripEndX[0],posTripEndY[0])
                mouse.click()
                time.sleep(0.2)
                mouse.move(posMouseLastX, posMouseLastY)
                window_last()
            # Если поездка по путевке, то активируется флаг и запускается таймер конца поездки
            elif fishingTrip == 2:
                global timeTripEnd
                window_active()
                time.sleep(1)
                window_last()
                flagTripEnd = True
                timeTripEnd = time.time()


def game_trip_end():
    # Функция повторной поездки по путевке, активируется при активной табличке окончания путевки. Через 75 сек сбрасываются удочки и ожидается возврат на базу
    global flagTripEnd
    if flagTripEnd:
        global timeTripEnd
        if (time.time()-timeTripEnd)>= 75:
            global posIsBaseX,posIsBaseY,colorIsBase,fishingLocate
            posMouseLastX, posMouseLastY = mouse.get_position()
            window_active()
            rod_stop_all()
            window_last()
            while True:
                # Проверка местонахождения на базе 2мя пикселями.
                if pyautogui.pixelMatchesColor(posIsBaseX[0],posIsBaseY[0],colorIsBase[0]):
                    if pyautogui.pixelMatchesColor(posIsBaseX[1],posIsBaseY[1],colorIsBase[1]):
                        window_active()
                        game_trip_locate_inventory(fishingLocate)
                        eat()
                        rod_rope_all()
                        flagTripEnd = False
                        window_last()
                        mouse.move(posMouseLastX, posMouseLastY)
                        break
                else:
                    time.sleep(1)


def game_trip_initialization(NumLoc = 0,NumShot = 0, NumType = 1):
    # Функция повторной инициализации, в случае смены локации
    global fishingLocate,fishingShotNum,fishingType,flagAutoPosition,flagChangeBait
    if (fishingLocate != NumLoc) or (fishingShotNum != NumShot) or (fishingType != NumType):
        if fishingLocate != NumLoc:
            flagChangeBait = True
            fishingLocate = NumLoc
        fishingShotNum = NumShot
        fishingType = NumType
        flagAutoPosition = True
        game_locate_initialization()
    else:
        return None


def game_trip_locate(NumLoc):
    global posBaseButtonX,posBaseButtonY,posTripButtonX, posTripButtonY
    global posIsBaseX,posIsBaseY,colorIsBase
    # Функция осуществления поездки с базы, ечерез кнопку "Путешествие",NumLoc -  выбранная база
    time.sleep(1)
    posMouseLastX, posMouseLastY = mouse.get_position()
    
    # Проверка местонахождения на базе 2мя пикселями. И клик на кнопку "На базе" если это не так
    if not pyautogui.pixelMatchesColor(posIsBaseX[0],posIsBaseY[0],colorIsBase[0]):
        if not pyautogui.pixelMatchesColor(posIsBaseX[1],posIsBaseY[1],colorIsBase[1]):
            window_drag_full(True)
            mouse.move(posBaseButtonX, posBaseButtonY)
            mouse.click()
            window_drag_full(False)
            
    # Кнопка "Путешествие"(находясь на базе)
    mouse.move(posTripButtonX, posTripButtonY)
    mouse.click()
    time.sleep(2)
    
    if NumLoc < 4:
        # Определение нужной карты (Дема)
        if NumLoc == 0:
            mouse.drag(710,320,710,409,True, 0.1)
        # Определение нужной карты (Днепр-киев)
        elif NumLoc == 1:
            mouse.drag(710,320,710,420,True, 0.1)
        # Определение нужной карты (Озеро)
        elif NumLoc == 2:
            mouse.drag(710,320,710,533,True, 0.1)
        # Определение нужной карты (Борнео)
        elif NumLoc == 3:
            mouse.drag(710,320,710,365,True, 0.1)
        # Позиция: верх списка карт
        mouse.move(560,270)
    else:
    # Определение нужной карты (Сейшилы)
        if NumLoc == 4:
            mouse.drag(710,320,710,538,True, 0.1)
        # Позиция: низ списка карт
        mouse.move(560,620)
        
    # Выбор карты
    mouse.click()
    
    # Кнопка "Поехать" 1
    time.sleep(0.5)
    mouse.move(780,770)                
    mouse.click()
    time.sleep(2)
    
    # Кнопка "Поехать" 2
    time.sleep(0.5)
    mouse.move(810,500)                
    mouse.click()
    time.sleep(5)
    
    # Кнопка локации (с предварительным получением координат кнопки новой локации)
    NewLocateMapX,NewLocateMapY = locate_position(NumLoc)
    mouse.move(NewLocateMapX,NewLocateMapY)
    mouse.click()
    mouse.move(posMouseLastX, posMouseLastY)
    time.sleep(9)
    game_trip_initialization(NumLoc,defaultShotNum,defaultFishingType)
    
  
def game_trip_locate_inventory(NumLoc):
    # Функция осуществления поездки по путевке из инвентаря,NumLoc -  выбранная локация для использования всех путевок этой локации
    global posThingsButtonX, posThingsButtonY,defaultLocate,defaultShotNum,defaultFishingType,fishingTrip,defaultFishingTrip
    time.sleep(2)
    posMouseLastX, posMouseLastY = mouse.get_position()
    
    # Кнопка "Разные вещи"(рюкзак)
    mouse.move(posThingsButtonX, posThingsButtonY)
    mouse.click()
    time.sleep(2)
    
    # Ползунок в меню рюкзака
    mouse.drag(845,258,845,842,True,0.2)
    time.sleep(0.5)

    # Выбор верхнего предмета в меню рюкзака
    mouse.move(600,252)
    mouse.click()
    time.sleep(0.5)

    # Выбор последующих предметов в меню рюкзака
    for i in range(30):
        keyboard.send('down')
        time.sleep(0.5)
        # Определение эхолота в конце списка и переезд на локацию по умолчанию
        if pyautogui.pixelMatchesColor(1253,619,(138,132,132)):
            if pyautogui.pixelMatchesColor(1299,761,(96,88,101)):
                keyboard.send('space')
                game_trip_locate(defaultLocate)
                fishingTrip = defaultFishingTrip
                return
        # Определение путевки
        if pyautogui.pixelMatchesColor(1274,634,(186,173,139)):
            if pyautogui.pixelMatchesColor(1228,679,(159,168,173)):
                
                # Определение нужной путевки (Днепр-Киев)
                if NumLoc == 1:    
                    if pyautogui.pixelMatchesColor(937,664,(54,137,192)):
                        if pyautogui.pixelMatchesColor(1007,666,(210,137,50)):
                            print('Днепр-Киев')
                            break
                                    
                # Определение нужной путевки (Борнео)
                elif NumLoc == 3: 
                    if pyautogui.pixelMatchesColor(935,668,(174,97,0)):
                        if pyautogui.pixelMatchesColor(974,665,(174,97,0)):
                            print('Борнео')
                            break                            
                    
                # Определение нужной путевки (Сейшилы)
                elif NumLoc == 4:
                    if pyautogui.pixelMatchesColor(936,670,(0,54,126)):
                        if pyautogui.pixelMatchesColor(1078,668,(54,0,89)):
                            print('Сейшилы')
                            break
                
    # Кнопка использовать  в меню рюкзака
    time.sleep(0.5)
    mouse.move(1277,838)                
    mouse.click()
    time.sleep(5)

    # Кнопка локации (с предварительным получением координат кнопки новой локации)
    NewLocateMapX,NewLocateMapY = locate_position(NumLoc)
    mouse.move(NewLocateMapX,NewLocateMapY)
    mouse.click()
    mouse.move(posMouseLastX, posMouseLastY)
    time.sleep(9)
    game_trip_initialization(NumLoc,defaultShotNum,defaultFishingType)
    
    

def position_start():
    # Функция определяет координаты кнопки "Прикорм"
    print('Нажмите слева сверху от кнопки "Прикорм" правой кнопкой мыши')
    mouse.wait(button='right')
    X1,Y1 = mouse.get_position()
    picsSize = 10
    X1 += 45
    Y1 += 10
    for x in range(X1,X1+picsSize):
        for y in range(Y1,Y1+picsSize):
            if pyautogui.pixelMatchesColor(x, y, (129, 59, 1)):
                if pyautogui.pixelMatchesColor(x, y+4, (156, 73, 4)):
                    if pyautogui.pixelMatchesColor(x, y+10, (67, 67, 67)):
                        print('Координаты кнопки "Прикорм" были найдены')
                        print(x,', ', y)
                        return x, y
    print("Координаты кнопки 'Прикорм' не были найдены")
    return None


def pos_cursor(rodNum):
    # Определение координат заброса удочки rodNum после правого клика мыши
    time.sleep(0.2)
    rod_number(rodNum)
    print('Выберите место для ',rodNum,' нажатия')
    mouse.wait(button='right')
    x1,y1 = mouse.get_position()
    y1 -= 1
    time.sleep(0.45)
    return x1,y1



def pos_shot(positionX,positionY):
    # Функция назначения всех координат 3 удочек, по переданной точке индикации 1 удочки
    global quantR,posX,posY,posFloatBiteX,posFloatBiteY
    
    # Координаты для индекса точки заброса 1 удочки
    posX[0],posY[0] = positionX, positionY
    
    # Координаты для индекса точки заброса 2,3 удочки
    for i in range(1,quantR):
        posX[i],posY[i] = posX[i-1]+2,posY[i-1]
        
    # Координаты для индекса точки определения обычного поплавка всех удочек
    for i in range(quantR):
        posFloatBiteX[i],posFloatBiteY[i] = posX[i],posY[i]-1



def button_press(button1):
    timeStartPress = time.time()
    while True:
        keyboard.send(button1)
        time.sleep(0.02)
        if (time.time()-timeStartPress)>=0.45:
            break


def cage_check():
    # Функция проверки садка, закрывается если он не открыт
    time.sleep(0.4)
    global countAimFish,countAimFishDay,countWasteFishDay,countAllFishDay
    global posAimX,posAimY,colorAim,nameAim,posCageX,posCageY,colorCage,timeDay,keyStop,fishingPull
    firstTime = True
    # делает наживку если это рак и закрывает окно садка
    # отпускает рыбу если это другая рыба и закрывает окно садка
    if fishingPull == 1:
        if pyautogui.pixelMatchesColor(posCageX,posCageY,colorCage):
            while True:
                if pyautogui.pixelMatchesColor(posCageX,posCageY,colorCage):
                    if pyautogui.pixelMatchesColor(posAimX,posAimY,colorAim):
                        keyboard.send('shift+b')
                        time.sleep(0.4+random.uniform(0,0.05))
                        if firstTime:
                            countAimFish += 1
                            countAimFishDay += 1
                            print('выловлен ',nameAim)
                            print('Сегодня поймано целевой рыбы: ', countAimFishDay)
                            print('прошло часов дня: ', (time.time()-timeDay)//90)
                            firstTime = False
                    else:
                        keyboard.send('shift+e')
                        time.sleep(0.4+random.uniform(0,0.05))
                        if firstTime:
                            countWasteFishDay += 1
                            print('выловлено что-то другое')
                            firstTime = False
                else:
                    break
        else:
            print('ничего не выловлено')
            keyboard.send(keyStop)
            time.sleep(0.45+random.uniform(0,0.05))
        countAllFishDay += 1
    # закрывает окно садка или сбрасывает рыбу если не успел вытянуть и закрывает окно садка
    elif fishingPull == 2:
        if pyautogui.pixelMatchesColor(posCageX,posCageY,colorCage):
            while True:
                if pyautogui.pixelMatchesColor(posCageX,posCageY,colorCage):
                    keyboard.send(keyStop)
                    time.sleep(0.4+random.uniform(0,0.05))
                    if firstTime:
                        countAimFish += 1
                        countAimFishDay += 1
                        print('выловлена рыба')
                        print('Сегодня поймано целевой рыбы: ', countAimFishDay)
                        print('прошло часов дня: ', (time.time()-timeDay)//90)
                        firstTime = False
                else:
                    break
        else:
            print('ничего не выловлено')
            keyboard.send(keyStop)
            time.sleep(0.45+random.uniform(0,0.05))
        countAllFishDay += 1
        


def daily_event():
    # Функция ежедневная
    global countAimFishDay,timeDay,countDay,countWasteFishDay,countAllFishDay
    global countError, countServerBreak, countServerReload
    
    # Запись в файл за день: кол-во целевой рыбы/кол-во прилова/вся рыба
    file1 = open('count_fish.txt','a')
    file1.write(str(countAimFishDay)+'/'+str(countWasteFishDay)+'/'+str(countAllFishDay)+'\n')
    file1.close()
    print('за день: кол-во целевой рыбы\кол-во прилова\вся рыба')
    print(str(countAimFishDay)+'/'+str(countWasteFishDay)+'/'+str(countAllFishDay))
    
    # Запись в файл за день: кол-во ошибок/кол-во перезапусков/количество обрывов связи
    file2 = open('count_error.txt','a')
    file2.write(str(countError)+'/'+str(countServerReload)+'/'+str(countServerBreak)+'\n')
    file2.close()
    
    countAimFishDay = 0
    countWasteFishDay = 0
    countAllFishDay = 0
    timeDay  = time.time()
    countDay += 1


def eat():
    # Функция еды 2 раза
    global posIsEatX,posIsEatY,colorIsEat,fishingType
    if not pyautogui.pixelMatchesColor(posIsEatX,posIsEatY,colorIsEat):
        return None
    global posFoodX,posFoodY,posEatX, posEatY
    posMouseLastX, posMouseLastY = mouse.get_position()
    window_active()
    if fishingType != 1:
        # остановка удочек, если не поплавок
        rod_stop_all()
    mouse.move(posFoodX, posFoodY)
    mouse.click()
    time.sleep(1)
    for i in range(2):
        mouse.move(posEatX, posEatY)
        mouse.click()
        time.sleep(1)
    mouse.move(posMouseLastX, posMouseLastY)
    keyboard.send(keyStop)
    time.sleep(0.45+random.uniform(0,0.05))
    rod_reset_all()
    window_last()



def rod_number(rodNum):
    # Нажатие клавиши с номером удочки, rodNum - номер удочки
    global flagRodNumber, quantR
    selectNum = (int(rodNum))-1
    
    #print(str(selectNum))
    if flagRodNumber[selectNum]:
        return None
    for i in range(quantR):
        if i == selectNum:
            flagRodNumber[i] = True
            
            #print(str(flagRodNumber[i]))
            continue
        flagRodNumber[i] = False
        
        #print(str(flagRodNumber[i]))
    keyboard.send(rodNum)
    time.sleep(0.1+random.uniform(0,0.5))


def rod_number_debug(rodNum):
    # Функция исправления выбранной удочки, если по факту в игре выбрана другая
    global lastRodNum, timeRodNum
    selectNum = (int(rodNum))-1
    
    # если в прошлый вход в функцию была выбранна та же удочка и и прошло меньше секунды
    if lastRodNum == selectNum:
        global timeFishingCheck, flagRodNumber, quantR
        if (time.time()-timeRodNum) <= (1+timeFishingCheck):
            # повторный выбор удочки нажатием и выявление прежней выбранной удочки
            for i in range(quantR):
                if flagRodNumber[i]:
                    print('!Ошибка выбранной удочки ',str(i+1),', переключена на ',rodNum,' удoчку')
                if i == selectNum:
                    flagRodNumber[i] = True
                    continue
                flagRodNumber[i] = False
            keyboard.send(rodNum)
            time.sleep(0.1+random.uniform(0,0.5))
    # запоминание последнего входа в функцию и выбранной удочки
    lastRodNum = selectNum
    timeRodNum = time.time()


def rod_setting_float():
    # Функция выставления глубины поплавка
    global fishingType,flagAutoPosition
    if fishingType == 1 and flagAutoPosition:
        global fishingShotNum,fishingLocate
        
        # Места заброса для Дема: Лягушачья заводь
        if fishingLocate == 0:
            
            # Глубина 0,33
            if fishingShotNum == 0:
                rod_setting_float_reset(0)
            
            # Глубина 0,4
            if fishingShotNum == 1:
                rod_setting_float_reset(1)
        
        # Места заброса для Днепр-Киев        
        if fishingLocate == 1:
            
            # Глубина 1,5
            if fishingShotNum == 0:
                rod_setting_float_reset(2)

    else:
        return None
        
        
def rod_setting_float_reset(depthNum):
    # Функция проверки соответствия глубины поплавка, согласно переданным координатам и выставления нужной глубины при несоответствии
    global posSetFloatX,posSetFloatY,posSetBarX1,posSetBarY1,posSetBarX2,posSetBarY2,colorBar1,colorBar2
    global posSetUpX,posSetUpY,posSetDownX, posSetDownY,posSetOkX, posSetOkY,posDepthX,posDepthY
    
    # Открытие окна "Настройка" поплавка
    mouse.move(posSetFloatX,posSetFloatY)
    mouse.click()
    time.sleep(1)
    
    # Смена позиции мыши на кнопку"ок", чтобы ползунок был неактивным
    mouse.move(posSetOkX, posSetOkY)
    
    # Поиск положения ползунка по 2м пикселям
    for i in range(210):
        if pyautogui.pixelMatchesColor(posSetBarX2,posSetBarY2+i,colorBar2):
            if pyautogui.pixelMatchesColor(posSetBarX1,posSetBarY1+i,colorBar1):
                
                # Если позиция ползунка на нужной глубине, то выходим
                if posDepthX[depthNum] == posSetBarX1 and posDepthY[depthNum] == posSetBarY1+i:
                    break
                    
                # Иначе передвигаем найденный ползунок на нужную позицию
                else:
                    mouse.drag(posSetBarX1,posSetBarY1+i,posDepthX[depthNum],posDepthY[depthNum],True, 0.05)
                    time.sleep(0.2)
                    
                    # Корректируем точное значение глубины стрелками
                    # Глубина 0,33
                    if depthNum == 0:
                        mouse.move(posSetDownX, posSetDownY)
                        mouse.click()
                    
                    # Глубина 0,4
                    elif depthNum == 1:
                        mouse.move(posSetUpX,posSetUpY)
                        mouse.double_click()
                    
                    
                    # Глубина 1,5                    
                    elif depthNum == 2:
                        mouse.move(posSetDownX, posSetDownY)
                        mouse.double_click()
                    
                    break
    time.sleep(0.2)
        
    # Нажимаем на кнопку "ок"
    mouse.move(posSetOkX, posSetOkY)
    mouse.click()
    time.sleep(0.5)
                    

def rod_bait_change(positionX1, positionY1):
    # Функция смены наживки, находясь в меню "Снасти"
    global fishingLocate
    # клик по удочке в инвентаре
    mouse.move(positionX1, positionY1)
    mouse.click()
    time.sleep(0.2+random.uniform(0,0.1))
    
    # клик графа наживки
    mouse.move(610,800)
    mouse.click()
    time.sleep(0.2+random.uniform(0,0.1))
    
    # для червя, перемещение ползунка и клик перечень наживок низ, кнопка="вверх"
    if fishingLocate == 0:
        mouse.drag(855,705,855,830,True, 0.2)
        time.sleep(0.2+random.uniform(0,0.1))
        mouse.move(730,845)
        mouse.click()
        time.sleep(0.2+random.uniform(0,0.1))
        but = 'up'
    # для остальных,клик перечень наживок верх, кнопка="вниз"
    else:
        mouse.move(730,690)
        mouse.click()
        time.sleep(0.2+random.uniform(0,0.1))
        but = 'down'
    
    # перебор наживок и поиск соответствующей
    for i in range(50):
        time.sleep(0.5+random.uniform(0,0.1))
        
        # червь
        if fishingLocate == 0:
            if pyautogui.pixelMatchesColor(998,714,(116,53,74)):
                if pyautogui.pixelMatchesColor(977,720,(247,68,107)):
                    break
        # икра
        elif fishingLocate == 1:
            if pyautogui.pixelMatchesColor(944,759,(183,57,6)):
                if pyautogui.pixelMatchesColor(1040,792,(199,84,4)):
                    break
        # головастик
        elif fishingLocate == 3:
            if pyautogui.pixelMatchesColor(1012,837,(113,142,109)):
                if pyautogui.pixelMatchesColor(1031,702,(129,172,145)):
                    break
        # кусочки рыбы
        elif fishingLocate == 4:
            if pyautogui.pixelMatchesColor(1022,698,(211,129,115)):
                if pyautogui.pixelMatchesColor(963,794,(223,120,89)):
                    break
        # клик в перечне наживок кнопку = вниз/верх
        keyboard.send(but)
        
    # клик установить на удилище
    mouse.move(1170,660)
    mouse.click()
    time.sleep(0.5+random.uniform(0,0.1))
    
    # возврат мышки на выбранной удочки
    mouse.move(positionX1, positionY1)


def rod_rope(positionX1, positionY1, positionX2, positionY2):
    # Функция достает 1 удoчку открывая снасти, необходимы координаты удочки в снастях
    global posRopeX, posRopeY, flagChangeBait
    mouse.move(posRopeX, posRopeY)
    mouse.click()
    time.sleep(1+random.uniform(0,0.1))
    
    # Дабл клик по удочке в инвентаре и смена наживки, если необходимо
    if flagChangeBait:
        rod_bait_change(positionX1, positionY1)
    else:
        mouse.move(positionX1, positionY1)
    mouse.double_click()
    time.sleep(1+random.uniform(0,0.1))
    
    # Настройка глубины удочки, если это необходимо
    rod_setting_float()
    
    # Клик в место заброса, Y+1 так как индексация заброса отличается на 1 пикс.
    mouse.move(positionX2, positionY2+1)
    mouse.click()
    time.sleep(1+random.uniform(0,0.1))
    
    keyboard.send(keyStop)
    time.sleep(0.45+random.uniform(0,0.05))

def rod_rope_all():
    # Функция достает 3 удoчки открывая снасти
    global posRopeRodX1,posRopeRodY1,posRopeRodX2,posRopeRodY2
    global posRopeRodX3,posRopeRodY3,posX,posY,flagChangeBait
    time.sleep(0.6)
    posMouseLastX, posMouseLastY = mouse.get_position()
    rod_rope(posRopeRodX1,posRopeRodY1, posX[0],posY[0])
    rod_rope(posRopeRodX2,posRopeRodY2, posX[1],posY[1])
    rod_rope(posRopeRodX3,posRopeRodY3, posX[2],posY[2])
    if flagChangeBait:
        flagChangeBait = False
    rod_reset_all()
    mouse.move(posMouseLastX, posMouseLastY)


def rod_withdraw_all():
    # Функция убирает 3 уды
    global posRemoveRodX, posRemoveRodY
    time.sleep(0.4)
    posMouseLastX, posMouseLastY = mouse.get_position()
    rod_stop_all()
    for i in range(3):
        mouse.move(posRemoveRodX, posRemoveRodY)
        mouse.click()
        time.sleep(1)
    mouse.move(posMouseLastX, posMouseLastY)


def rod_pull(rodNum):
    # Функция подтягивания лески 
    global keyPull,posCageX,posCageY,colorCage,fishingPull
    
    # цикличное нажатие keyPull в течение 2 секунд с последующей проверкой садка, рыбы до 500 грам
    if fishingPull == 1:
        print('тянем леску ', rodNum)
        timeStartPull = time.time()
        while True:
            keyboard.press(keyPull)
            time.sleep(0.01)
            if ((time.time()-timeStartPull)>=2) or pyautogui.pixelMatchesColor(posCageX,posCageY,colorCage):
                keyboard.release(keyPull)
                cage_check()
                rod_check_other(rodNum)
                rod_reset(rodNum)
                break
    # цикличное 2е нажатие keyPull и keyRodPull в течение timePull секунд с выходом из садка, любой рыбы
    elif fishingPull == 2:
        global timePull,timeNetSpan,keyRodPull,keyNet
        global posRPstartX,posRPstartY,posRPendX,posRPendY,colorRPstart,colorRPend,flagRPend
        global posPstartX,posPstartY,posPendX,posPendY,colorPstart,colorPend,flagPend
        print('тянем леску ', rodNum)
        # время начала вытягивания и время до нажатия подсака, счетчики подтягиваний
        timeStartPull = time.time()
        timeNetUse = time.time()
        timeRP, timeP = 0,0
        while True:
            
            # если флаг конца полосы удочки активен, проверям начало полосы и отключаем
            if flagRPend:
                if pyautogui.pixelMatchesColor(posRPstartX,posRPstartY,colorRPstart):
                    flagRPend = False
            # если флаг конца полосы удочки не активен и количество подтягиваний удочки на 1500 меньше(примерно от 2.5 до 5 сек), жмем RodPull 2раза
            if (not flagRPend) and (timeRP <= (timeP+1500)):
                keyboard.send(keyRodPull)
                time.sleep(0.033+random.uniform(0,0.001))
                keyboard.press(keyRodPull)
                time.sleep(0.01)
                timeRP += 2
                # проверяем конец полосы удочки, для отмены нажатий RodPull
                if not pyautogui.pixelMatchesColor(posRPendX,posRPendY,colorRPend):
                    flagRPend = True
                    keyboard.release(keyRodPull)
            
            # если флаг конца полосы лески активен, проверям начало полосы и отключаем
            if flagPend:
                if pyautogui.pixelMatchesColor(posPstartX,posPstartY,colorPstart):
                    flagPend = False
            # если флаг конца полосы удочки не активен и количество подтягиваний удочки больше подтягиваний лески, жмем Pull 2раза
            if (not flagPend) and (timeRP > timeP):
                keyboard.send(keyPull)
                time.sleep(0.033+random.uniform(0,0.001))
                keyboard.press(keyPull)
                timeP += 2
                # проверяем конец полосы лески, для отмены нажатий Pull
                if not pyautogui.pixelMatchesColor(posPendX,posPendY,colorPend):
                    flagPend = True
                    keyboard.release(keyPull)
                    time.sleep(0.01)
                # если прошло timeNetSpan времени с последнего нажадия подсака, проверяем другие удочки и жмем keyNet
                if ((time.time()-timeNetUse)>=timeNetSpan):
                    rod_check_other(rodNum)
                    keyboard.send(keyNet)
                    timeNetUse = time.time()
                    time.sleep(0.01)
            
            # если прошло timePull времени сначала вытягивания или обнаружен садок то обнуляем флаги и выходим
            if ((time.time()-timeStartPull)>=timePull) or pyautogui.pixelMatchesColor(posCageX,posCageY,colorCage):
                if (not flagRPend):
                    keyboard.release(keyRodPull)
                if (not flagPend):
                    keyboard.release(keyPull)
                flagRPend, flagPend = False, False
                cage_check()
                rod_check_other(rodNum)
                rod_reset(rodNum)
                break
    time.sleep(0.1)


def rod_check_other(rodNum):
    # Функция проверяет другие удочки и при поклевке переключается на них
    global color,posX,posY,posFloatBiteX,posFloatBiteY,flagRodCheck
    global quantR
    
    if fishingType == 1:
        for i in range(quantR):
            selectNumText = str(i+1)
            if (selectNumText == rodNum) or flagRodCheck[i]:
                continue
            elif not pyautogui.pixelMatchesColor(posFloatBiteX[i],posFloatBiteY[i],color[1]):
                rod_number_debug(selectNumText)
                rod_reset(selectNumText)
                if not pyautogui.pixelMatchesColor(posFloatBiteX[i],posFloatBiteY[i],color[1]):
                    if pyautogui.pixelMatchesColor(posX[i],posY[i],color[0]):
                        rod_stop(selectNumText)
                        flagRodCheck[i] = True
                        rod_number(rodNum)
    
    elif fishingType == 2:
        for i in range(quantR):
            selectNumText = str(i+1)
            if (selectNumText == rodNum) or flagRodCheck[i]:
                continue
            if not pyautogui.pixelMatchesColor(posX[i],posY[i],color[0]):
                rod_number(selectNumText)
                time.sleep(0.2+random.uniform(0,0.05))
                flagRodCheck[i] = True
                rod_number(rodNum)
            


def rod_stop(rodNum):
    # Функция остановки удочки, методом подсекания, rodNum-номер удочки
    global keyStop
    rod_number(rodNum)
    keyboard.send(keyStop)
    time.sleep(0.45+random.uniform(0,0.05))


def rod_stop_all():
    # Функция остановки 3 удочer, методом подсекания
    global key1,key2,key3
    rod_stop(key1)
    rod_stop(key2)
    rod_stop(key3)


def rod_reset(rodNum):
    # Функция возобновения ловли рыбы удочкой, методом ее переброса, rodNum-номер удочки
    global keyReset
    rod_number(rodNum)
    keyboard.send(keyReset)
    time.sleep(0.65+random.uniform(0,0.1))


def rod_reset_all():
    # Функция возобновения ловли рыбы 3 удочками, методом их переброса
    global key1,key2,key3
    rod_reset(key1)
    rod_reset(key2)
    rod_reset(key3)


def fishing_bottom(positX, positY, rodNum):
    # Процесс проверки и ловли на удочку№ rodNum на "донку"
    # с забросом в коорд. positX,positY
    global color
    if not pyautogui.pixelMatchesColor(positX,positY,color[0]):
        window_active()
        rod_reset(rodNum)
        rod_check_other(rodNum)
        if not pyautogui.pixelMatchesColor(positX,positY,color[0]):
            rod_pull(rodNum)
        window_last()
    return False

def fishing_float():
    # Процесс проверки и ловли на "поплавок"
    global posFloatBiteX,posFloatBiteY,color,quantR
    global posX,posY,flagRodCheck
    for i in range(quantR):
        rodNumText = str(i+1)
        if flagRodCheck[i]:
            window_active()
            rod_number_debug(rodNumText)
            rod_reset(rodNumText)
            if not pyautogui.pixelMatchesColor(posX[i],posY[i],color[0]):
                rod_pull(rodNumText)
            flagRodCheck[i] = False
            window_last()
            continue
        elif not pyautogui.pixelMatchesColor(posFloatBiteX[i],posFloatBiteY[i],color[1]):
            window_active()
            rod_number_debug(rodNumText)
            rod_reset(rodNumText)
            if not pyautogui.pixelMatchesColor(posFloatBiteX[i],posFloatBiteY[i],color[1]):
                if pyautogui.pixelMatchesColor(posX[i],posY[i],color[0]):
                    rod_stop(rodNumText)
                    rod_pull(rodNumText)
                    flagRodCheck[i] = False
            window_last()

# Инициализация перенных


# Флаги  и переменные для настройки программы !!!

# Номер текущего сервера (следующий при переключении будет +1)
serverNumber = 3

# Тип рыбалки, 1 - поплавок, 2 - донка
fishingType = 1

# Номер заброса (позиция для заброса удочек)
fishingShotNum = 0

# Метод пребывания на карте. 0 - бесплатное, 1 - ежедневная оплата, 2 - по путевке
fishingTrip = 2

# Тип подтягивания лески: 1 = вылов целевой рыбы до 500 грам, из которой сразу делается наживка, 2 = вылов любой рыбы, с последующей продажей зачетной и отпусканием остальной
fishingPull = 1

# Локация рыбалки, 0 - Дёма, вылов рака, 1 - Днепр-киев, головастик
fishingLocate = 1

# Флаг для смены активного окна, если откл. окно игры должно быть активным или будут ошибки
flagChangeWindow = False

# Флаг для переключения авто(True) и ручного(False) определения координат заброса
flagAutoPosition = True



# Циклично пытаемся найти координаты кнопки "Прикормка"
while True:
    Posit = position_start()
    if Posit != None:
        X1, Y1 = Posit
        break
    else:
        print('Попробуйте еще раз\n')

# Переменные "по умолчанию" для перехода на локацию при условии выполнения остальных заданий программы

# Локация рыбалки "по умолчанию", 0 - Дёма, вылов рака, 1 - Днепр-киев, головастик
defaultLocate = 0
# Номер заброса "по умолчанию" (позиция для заброса удочек)
defaultShotNum = 0
# Тип рыбалки, 1 - поплавок, 2 - донка "по умолчанию" 
defaultFishingType = 1
# Метод пребывания на карте. 0 - бесплатное, 1 - ежедневная оплата, 2 - по путевке "по умолчанию"
defaultFishingTrip = 0


# Флаги и счетчики. Не настраиваемые. Для внутренних подсчетов

windowLast = None
window1 = None
flagWindow = False
flagChangeBait = False
flagTripEnd = False
timeTripEnd = time.time()
timeAll = time.time()
timeAlert = time.time()
timeDay = time.time()
# интервал между проверками удочек
timeFishingCheck = 0.2
# интервал для проверки садка при вытягивании, в сек
timeNetSpan = 3
# максимальное время для вытягивания рыбы, в сек
timePull = 100


# Флаг проверки других удочек во время поклевки
flagRodCheck = [False, False, False]

# Флаг проверки активной удочки
flagRodNumber = [False, False, False]

# Таймер и счетчик количества перезапусков и обрыва сервера
countServerReload = 0
countServerBreak = 0
timeServerReload = time.time()

countError =0
countAimFish = 0
countAimFishDay = 0
countDay = 0
# Счетчики лишней рыбы и все поклевки в день
countWasteFishDay = 0
countAllFishDay = 0

# переменные для запоминания времени и выбранной удочки после последнего входа в функцию исправления номера удочки
lastRodNum = 0
timeRodNum = time.time()

# Создание переменных для определения позиции индикации удочек
posX, posY = [0,0,0], [0,0,0]
posFloatBiteX, posFloatBiteY = [0,0,0], [0,0,0]
# Создание переменной для определения цвета точки заброса
color = [(0,0,0),(0,0,0)]

# Создание переменной для установки глубины в меню "настройка" поплавка
posDepthX, posDepthY = [0,0,0], [0,0,0]

# Создание переменных для целевой рыбы
posAimX,posAimY,colorAim,nameAim = 0,0,(0,0,0),' '


# Координаты и цвет пикселя для определения запрета на базе
posAlertX, posAlertY = X1-31, Y1-633  
colorAlert = (216,215,184)

# Координаты и цвет пикселей для подтверждения нахождения на "базе"
posIsBaseX,posIsBaseY = [X1+141,X1+153],[Y1-449,Y1-307]
colorIsBase = [(184,69,40),(228,156,10)]

# Координаты и цвет пикселя на пустой полоске еды для подтверждения 2х поданий варенной колбасы
#posIsEatX,posIsEatY = X1-32, Y1-61
posIsEatX,posIsEatY = X1-32, Y1-54
colorIsEat =  (215, 220, 198)

# Координаты и цвет пикселей для проверки окончания путевки, posTripEndX[0] также кнопка для продления путевки
posTripEndX,posTripEndY = [X1+210,X1,X1+216],[Y1-490,Y1-565,Y1-550]
colorTripEnd = [(238,218,167),(234,212,48),(239,196,118)]

# Координаты, цвет пикселей  и флаги для полосы натяжения при подтягивании RP-удочка('h'), P-леска('g'). start=+20пикс по Х от начала полоски, end-не доходя до желтого. color = цвет пустой полоски

posRPstartX,posRPstartY = X1+371, Y1-128
colorRPstart = (185, 186, 172)
posRPendX,posRPendY = X1+449, Y1-128
colorRPend = (200, 201, 187)
flagRPend = False

posPstartX,posPstartY = X1+371, Y1-112
colorPstart = (196, 197, 183)
posPendX,posPendY = X1+449, Y1-112
colorPend = (206, 207, 193)
flagPend = False


# Координаты пикселя на зельях для активации окна
posPotionX, posPotionY = X1+340, Y1-660

# Координаты котелка с едой и кнопки "Употребить"
posFoodX, posFoodY = X1+120, Y1+10
posEatX, posEatY = 1135, 597

# Координаты снастей с удочками, кнопки "Снасти"
posRopeX, posRopeY = X1+90, Y1-70

# Координаты достать удочку, кнопки "Убрать в ящик"
posRemoveRodX, posRemoveRodY = X1+380, Y1+30

# Координаты кнопки "Садок"
posCageButtonX, posCageButtonY = X1+200, Y1

# Координаты кнопки "Разные вещи"(рюкзак)
posThingsButtonX, posThingsButtonY = X1+150, Y1-90

# Координаты кнопки "На базу"
posBaseButtonX, posBaseButtonY = X1+780, Y1-420

# Координаты кнопки "Путешествие"(находясь на базе)
posTripButtonX, posTripButtonY = X1+200, Y1-248

# Координаты кнопки "Меню"
posMenuButtonX, posMenuButtonY = X1+710, Y1-660

# Координаты кнопки закрытие сообщения "Приветствие"
posHelloButtonX, posHelloButtonY = X1+675, Y1-450

# Координаты кнопки "Настройка" поплавка
posSetFloatX, posSetFloatY = X1+330, Y1+30



# Координаты удочки 1 с открытыми снастями
posRopeRodX1, posRopeRodY1 = 660, 270

# Координаты удочки 2 с открытыми снастями
posRopeRodX2, posRopeRodY2 = 660, 320

# Координаты удочки 3 с открытыми снастями
posRopeRodX3, posRopeRodY3 = 660, 340

# Координаты и цвет пикселя для подтверждения открытого садка(деревяшка сверху)
posCageX, posCageY = 1083,238
colorCage = (162,71,26)


# Координаты и цвет пикселя меню "настройки" поплавка.
# Координаты и цвет позиции полосы прокрутки меню "настройки" поплавка
posSetBarX1, posSetBarY1 = 890, 435
posSetBarX2, posSetBarY2 = 890, 431
colorBar1 = (217,218,220)
colorBar2 = (221,221,224)

# Координаты стрелок вверх(-1) и вниз(+1) меню "настройки" поплавка
posSetUpX, posSetUpY = 890, 420
posSetDownX, posSetDownY = 890,640

# Координаты кнопки "ок" в меню "настройки" поплавка
posSetOkX, posSetOkY = 1030, 640

# Координаты выставления глубины ползунка в меню "настройки" поплавка
# Глубина 0.42(при проверке 0.33 такие же)
posDepthX[0], posDepthY[0] = 890,441
# Глубина 0.32(при проверке 0.4 такие же)
posDepthX[1], posDepthY[1] = 890,443
# Глубина 1.48(при проверке 1.5 такие же)
posDepthX[2], posDepthY[2] = 890,463


# Координаты для запуска игры из меню

# Координаты кнопки "Начать игру"
posMenuX1, posMenuY1 = 1233, 452

# Координаты 1,2,3 серверов
posMenuServerX1, posMenuServerY1 = 831, 346
posMenuServerX2, posMenuServerY2 = 831, 387
posMenuServerX3, posMenuServerY3 = 831, 422

# Разница между полным окном на экране и невидимой частью окна за пределами экрана по оси Х, в количестве пикселей
dragFull = X1-952

# Координаты нажатия на карту
posMapX,posMapY = X1+780,Y1-500

# Назначение переменных под клавиши
keyStop = 'space'
keyReset = 'd'
keyNet = 'f'
keyRodPull = 'h'
keyPull = 'g'
key1 = '1'
key2 = '2'
key3 = '3'


# Количество удочек
quantR = 3



# Основной код
game_locate_initialization()
if flagAutoPosition:
    rod_withdraw_all()
    rod_rope_all()
eat()
while True:
    if fishingType == 1:
        fishing_float()
    if fishingType == 2:
        for i in range(quantR):
            flagRodCheck[i] = fishing_bottom(posX[i],posY[i],str(i+1))
    
    if (time.time()-timeDay) >= 2160:
        # Окончание дня
        daily_event()
    if (time.time()-timeAlert) >= 10:
        # Проверка запретов
        if not pyautogui.pixelMatchesColor(posAlertX,posAlertY,colorAlert):
            game_reload(True)
        # Проверка ошибки "связь с сервером"
        game_server_break()
        # Проверка голода
        eat()
        # Проверка завершения путевки
        game_trip_end_check()
        timeAlert = time.time()
    # Проверка путешествия по путевке
    game_trip_end()
    time.sleep(timeFishingCheck)
    if keyboard.is_pressed('ctrl+1'):
        # Отключение, включение смены окон
        if flagChangeWindow:
            flagChangeWindow = False
            print('Смена окон: ОТКЛЮЧЕНА')
        else:
            flagChangeWindow = True
            print('Смена окон: ВКЛЮЧЕНА')
        time.sleep(2)
    if keyboard.is_pressed('ctrl+2'):
        print('Перезапуск игры без смены сервера')
        game_reload()
    if keyboard.is_pressed('ctrl+3'):
        print('Перезапуск игры со сменой сервера')
        game_reload(True)
    if keyboard.is_pressed('ctrl+z'):
        rod_stop_all()
        print('ПАУЗА')
        keyboard.wait('ctrl+z')
        rod_reset_all()
    if keyboard.is_pressed('x'):
        rod_reset_all()
    if keyboard.is_pressed('ctrl+c'):
        rod_stop_all()
        print('exit')
        break








file1 = open('count_fish.txt','a')
file1.write('____\n')
file1.close()
print(color[0])
print('Всего поймано целевой рыбы ', countAimFish)
print('Всего поймано целевой рыбы в последний день ', countAimFishDay)
print('Всего прошло дней ', countDay)
print('Прошло часов последнего дня ', (time.time()-timeDay)//90)
if countDay == 0:
    countDay = 1
print('В среднем целевой рыбы в день', (countAimFish-countAimFishDay)/countDay)
