import pygame
import cv2
import mediapipe as mp
import os
import random
import speech_recognition as sr
import threading


#Mediapipe kurulum
mpHands = mp.solutions.hands # el tespit etme modülü
hands = mpHands.Hands() # işlemleri gerçekleştirmek için bir nesne oluştur
mpDraw = mp.solutions.drawing_utils # çizim işlemlerini gerçekleştirmek için kullanılan modül


#webcam
cam = cv2.VideoCapture(0)

#pencere konumu, yazı tipi ve fon müziği
os.environ['SDL_VIDEO_WINDOW_POS'] ="650,25"
pygame.font.init()
pygame.mixer.init(44100, -16,2,2048)
pygame.mixer.music.load('Tetris.mp3')


#Global değişkenler
s_width = 850
s_height = 750
play_width = 300  #  300 // 10 = 30 blok başına genişlik
play_height = 600  #  600 // 20 = 30 blok başına yükseklik
block_size = 30
top_left_x = (s_width - play_width) // 2 # tam bölme
top_left_y = s_height - play_height

#ızgara oluşturma
def create_grid(locked_pos={}):
    grid = [[(0,0,0) for _ in range(10)] for _ in range(20)]#000 renk

    for i in range(len(grid)): #satırlar
        for j in range(len(grid[i])): #sütunlar
            if (j, i) in locked_pos:
                c = locked_pos[(j,i)]
                grid[i][j] = c
    return grid

# şeklin dönme durmunu kontrol etme
def convert_shape_format(shape):
    positions = [] # şeklin koordinantlarını tutmak için
    format = shape.shape[shape.rotation % len(shape.shape)] #şeklin ilk halini alır

    for i, line in enumerate(format):  # her satır içeriği kontrol edilir
        row = list(line) # her satırı değişken olarak ata
        for j, column in enumerate(row): # her sütun içeriği kontrol edilir
            if column == '0':                       #döndürülme sayısına göre yeniden şekillendirilir
                positions.append((shape.x + j, shape.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4) # şeklin en sol köşesini referans alarak yeni pozisyonu oluşturulur

    return positions # return edilir

background_image=pygame.image.load(r'C:\Users\Talha\PycharmProjects\pythonProject\tetris.jpg') # arkaplan resmi
new_width = 800 # boyutlandırma
new_height = 430
new_background = pygame.transform.scale(background_image, (new_width, new_height)) # transfom
selected_shapes = None #seçilecek olan şekiller
fall_speed_real = None #şekillerin düşme hızı (zorluğa göre)
def select_difficulty():
    global selected_shapes
    global fall_speed_real
    y_offset = 100
    r = sr.Recognizer()
    run = True
    while run:
        win.blit(new_background, (0, 0))
        draw_text_middle(win, 'Lütfen Bir Zorluk Derecesi Seçin!', 37, (31, 255, 255))
        draw_text_middle(win, '(K)olay', 37, (31, 255, 255), y_offset)
        draw_text_middle(win, '(O)rta', 37, (31, 255, 255), y_offset + 50)
        draw_text_middle(win, '(Z)or', 37, (31, 255, 255), y_offset + 100)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:
                    selected_shapes= kolay_shapes
                    fall_speed_real=0.45
                    return selected_shapes
                elif event.key == pygame.K_o:
                    selected_shapes= orta_shapes
                    fall_speed_real=0.3
                    return selected_shapes
                elif event.key == pygame.K_z:
                    selected_shapes=zor_shapes
                    fall_speed_real=0.2
                    return selected_shapes


        '''with sr.Microphone() as source:
            audio = r.listen(source)

        try:
            recognized = r.recognize_google(audio, language='tr-TR')  # Türkçe dilinde sesi tanı
            if 'kolay' in recognized :
                selected_shapes = kolay_shapes
                fall_speed_real = 0.45
                return selected_shapes
            elif 'orta' in recognized:
                selected_shapes = orta_shapes
                fall_speed_real = 0.3
                return selected_shapes
            elif 'zor' in recognized:
                selected_shapes = zor_shapes
                fall_speed_real = 0.2
                return selected_shapes
            else:
                print("Anlaşılamadı, lütfen tekrar deneyin.")

        except sr.UnknownValueError:
            print("Ses anlaşılamadı.")
        except sr.RequestError:
            print("İstek tamamlanamadı, bağlantınızı kontrol edin.")'''

def select_control_method():
    control_selected = False
    y_offset = 100
    r = sr.Recognizer()
    while not control_selected:
        win.fill((0, 0, 0))
        win.blit(new_background, (0, 0))
        draw_text_middle(win, 'Lütfen Kontrol Yöntemini Seçin!', 37, (31, 255, 255))
        draw_text_middle(win, '(E)l ile kontrol', 37, (31, 255, 255), y_offset)
        draw_text_middle(win, '(S)es ile kontrol', 37, (31, 255, 255), y_offset + 50)
        draw_text_middle(win, 'Geri Dönmek için (Backspace)', 37, (31, 255, 255), y_offset + 100)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                control_selected = True  # Eğer kullanıcı çıkış yaparsa, kontrolü sonlandır
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    control_selected = True
                    return "el"  # Kullanıcı el ile kontrol seçti
                elif event.key == pygame.K_s:
                    control_selected = True
                    return "ses"  # Kullanıcı ses ile kontrol seçti

                # Ek olarak, kullanıcıya geri dönme seçeneği de sunulabilir.
                elif event.key == pygame.K_BACKSPACE:  # Örneğin, 'Backspace' tuşuyla geri dönme seçeneği
                    control_selected = True
                    return None  # Kullanıcı geri dönmek istedi

        '''with sr.Microphone() as source:
            audio = r.listen(source)

        try:
            recognized = r.recognize_google(audio, language='tr-TR')  # Türkçe dilinde sesi tanı
            if 'el' in recognized:
                control_selected = True
                return "el"

            elif 'ses' in recognized:
                control_selected = True
                return "ses"

            else:
                print("Anlaşılamadı, lütfen tekrar deneyin.")

        except sr.UnknownValueError:
            print("Ses anlaşılamadı.")
        except sr.RequestError:
            print("İstek tamamlanamadı, bağlantınızı kontrol edin.")'''

#şekillerin tüm dönebilme halleri

S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['..0..',
      '..0..',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

U = [['.0.0.',
      '.000.',
      '.....',
      '.....',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '.00..',
      '.....'],
     ['.....',
      '.000.',
      '.0.0.',
      '.....',
      '.....'],
     ['.....',
      '.00..',
      '.0...',
      '.00..',
      '.....']]

X = [['.....',
      '..0..',
      '.000.',
      '..0..',
      '.....']]

H = [['.0.0.',
      '.000.',
      '.0.0.',
      '.....',
      '.....'],
     ['.....',
      '.000.',
      '..0..',
      '.000.',
      '.....'],
     ['.0.0.',
      '.000.',
      '.0.0.',
      '.....',
      '.....'],
     ['.....',
      '.000.',
      '..0..',
      '.000.',
      '.....']]

Y = [['.00..',
      '..0..',
      '..00.',
      '.....',
      '.....'],
     ['.....',
      '...0.',
      '.000.',
      '.0...',
      '.....']]

B = [['...0.',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '.000.',
      '...0.',
      '...0.',
      '.....'],
     ['.000.',
      '.0...',
      '.0...',
      '.....',
      '.....'],
     ['.....',
      '.0...',
      '.0...',
      '.000.',
      '.....']]


#şekiller ve renkler
zor_shapes = [S, Z, I, O, J, L, T, X, U, H, Y,B]
orta_shapes = [S, Z, I, O, J, L, T, X]
kolay_shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 230, 115), (255, 51, 51), (0, 204, 255), (255, 255, 128), (0, 102, 255), (255, 140, 26),(20, 51, 255), (204, 51, 255),(170, 51, 255),(50, 51, 255),(95, 51, 255),(202, 51, 255)]



#düşen şeklin geçerli bir boşlukta olup olmadığını kontrol etme
def valid_space(shape, grid):
    bos_pos = [[(j, i) for j in range(10) if grid[i][j] == (0,0,0)] for i in range(20)] #20 satır 10 sütun matris oluştur grid[i][j] 0,0,0 boş hücreler
    bos_pos = [j for sub in bos_pos for j in sub] # boş hüvrelerin koordinantlarını bir listeye at

    formatted = convert_shape_format(shape) # şeklin pozisyonu ve konumu alır

    for pos in formatted:
        if pos not in bos_pos:
            if pos[1] > -1: #oyun alanı dışındaysa şekil false
                return False
    return True

#lose kontrol etme
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1: #eğer bloğun y koordinantı y<1 ise yani en üst satırdaysa lose
            return True

    return False

#şekillerin sınıfları
class Piece(object):
    rows = 20  # y
    columns = 10  # x

    def __init__(self, column, row, shape):
        self.x = column # parçanın x koordinantı
        self.y = row    # y koordinantı
        self.shape = shape #şekli
        self.color = shape_colors[selected_shapes.index(shape)] #listedeki indexten alır ve rengi
        self.rotation = 0 #dönme durumu varsayılan olarak 0

#rastgele şekil
def get_shape():

    return Piece(5, 0, random.choice(selected_shapes)) #rastgele şekil almak için 5-0 başlangıç konumu

def draw_text_middle(surface, text, size, color, y_offset=0):
    font = pygame.font.SysFont("britannic", size, bold=True)
    label = font.render(text, 1, color)
    surface.blit(
        label,
        (
            top_left_x + play_width / 2 - (label.get_width() / 2), # yatayda ortala
            top_left_y + play_height / 2 - label.get_height() / 2 + y_offset, # dikeyde ortala
        ),
    )

# ızgara renklendirme
def draw_grid(surface, grid):
    sx = top_left_x #ızgaranın çizileceği konumun x'i
    sy = top_left_y #ızgaranın çizileceği konumun y'si

    for i in range(len(grid)): #len grid yani satır sayısı kadar satırların altını çizer
        pygame.draw.line(surface, (128,128,128), (sx, sy + i*block_size), (sx+play_width, sy+ i*block_size)) #başlangıç ve bitiş koordinantları
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j*block_size, sy),(sx + j*block_size, sy + play_height))

#bir satırı temizleme
def clear_rows(grid, locked):

    tss = 0 #temizlenen satır sayısı
    for i in range(len(grid)-1, -1, -1): #gridin en altından başlayıp en üste doğru ilerleyen döngü
        row = grid[i] #mevcut satır
        if (0,0,0) not in row: #eğer tüm satırda siyah renkli satır yoksa
            tss += 1 #inc'i 1 artır
            ind = i #indeksi kaydet
            for j in range(len(row)):
                try:
                    del locked[(j,i)] #lose aldıysa
                except:
                    continue

    if tss > 0: # eğer temizlenen satır var ise
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]: # kilitli olan hücreler y ekseninin en altından
            x, y = key # konumları
            if y < ind: # kilitli olan hücreleri inc değeri kadar aşağı kaydır
                newKey = (x, y + tss) # yeni konum
                locked[newKey] = locked.pop(key)

    return tss # temizlenen satırı döndür puan hesaplamak için

#sonraki şekli gösteren pencere
def draw_next_shape(shape, surface):
    font = pygame.font.SysFont('britannic', 30)
    label = font.render('Sonraki Sekil', 1, (255,255,255))

    sx = top_left_x + play_width + 50 # koordinantları
    sy = top_left_y + play_height/2 - 100
    format = shape.shape[shape.rotation % len(shape.shape)] # şeklin o anki durumu

    for i, line in enumerate(format): # her satırı kontrol et
        row = list(line) # her satırı bir liste olarak al
        for j, column in enumerate(row):# her sütun için kontrol et
            if column == '0':#sütun 0'sa
                pygame.draw.rect(surface, shape.color, (sx + j*block_size, sy + i*block_size, block_size, block_size), 0) #şekli çiz

    surface.blit(label, (sx +10, sy - 40)) #metni pencerede görüntüle

#ana pencere
def draw_window(surface, grid, score=0): #oyun penceresini çiz
    surface.fill((155, 83, 123)) # yüzeyi renklendir ile doldur

    pygame.font.init()
    font = pygame.font.SysFont('britannic', 60) #başlık
    label = font.render('TETRIS', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 15)) # tetris yazısını en üste sabitle

    #mevcut skoru göster
    font = pygame.font.SysFont('britannic', 30) # skor alanı
    label = font.render('Skor: ' + str(score), 1, (255,255,255))

    sx = top_left_x + play_width + 50 # skor yazısının koordinantlar
    sy = top_left_y + play_height/2 - 100

    surface.blit(label, (sx + 20, sy + 160)) # aradaki boşluklar

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j*block_size, top_left_y + i*block_size, block_size, block_size), 0)

    pygame.draw.rect(surface, (230, 230, 230), (top_left_x, top_left_y, play_width, play_height), 7) # dış çerçeve

    draw_grid(surface, grid)# pencereyi oluştur

#temizlenen satır miktarına karşılık gelen puanlar
def add_score(rows):
    conversion = {
        0: 0,
        1: 10,
        2: 50,
        3: 100,
        4: 500
    }
    return conversion.get(rows)





voice_command = ""
voice_thread = None

#OYUNU ÇALIŞTIRAN ANA İŞLEV
def main(win,control_method):
    global fall_speed_real
    global voice_thread
    global voice_command
    locked_positions = {} #kilitli pozisyonlar-hücreler
    grid = create_grid(locked_positions) # yeni matris

    change_piece = False # şeklin değiştirilip değişmediğini kontrol eder
    run = True # oyun başla
    current_piece = get_shape()#mevcut şekli get_shapeden al
    next_piece = get_shape() # sonraki şekil
    clock = pygame.time.Clock() #zamanlayıcı
    fall_time = 0 # geçen zaman
    fall_speed = fall_speed_real #şeklin düşme hızını saklar
    level_time = 0 # şeklin düşüş hızını artırmak için kullanıcak değişken
    score = 0
    left_wait = 0 #delay
    right_wait = 0
    rotate_wait = 0
    down_wait = 0
    paused = False
    if control_method == "ses":
        voice_thread = threading.Thread(target=voice_command_handler, args=())
        voice_thread.start()

    #ANA WHİLE DÖNGÜSÜ
    while run:
        grid = create_grid(locked_positions) #oyun alanı güncellenmesi ve kilitlenmiş pozisyonları kullanarak grid oluşturmak
        fall_time += clock.get_rawtime() # değişkenleri güncelle
        level_time += clock.get_rawtime()# değişkenleri güncelle
        clock.tick()

        if control_method == "el":
            success, img = cam.read()  # web kamerasından alınan görüntü
            imgg = cv2.flip(img, 1)
            imgRGB = cv2.cvtColor(imgg, cv2.COLOR_BGR2RGB)
            results = hands.process(imgRGB)
            if results.multi_hand_landmarks:#birden fazla el var ise
                for handLms in results.multi_hand_landmarks: #döngüye gir
                    for id, lm in enumerate(handLms.landmark): #işaret noktalarını ve id'sini al
                        h, w, c = imgg.shape #yükseklik genişlik kanal
                        if id == 0:
                            x = [] #listeleri sıfırla
                            y = []
                        x.append(int((lm.x) * w)) #koordinant
                        y.append(int((1 - lm.y) * h))

                        # EL HAREKETLERİ
                        if len(y) > 20: # işaret noktaları kontrolü
                            if (x[0] > x[3] > x[4]) and not (y[8] > y[5]):# baş parmak ve işaret parmağı
                                left_wait += 1
                            if not (x[0] > x[3] > x[4]) and (y[8] > y[5]):
                                right_wait += 1
                            if (x[0] > x[3] > x[4]) and (y[8] > y[5]):
                                rotate_wait += 1

                    mpDraw.draw_landmarks(imgg, handLms, mpHands.HAND_CONNECTIONS)

            else:
                down_wait += 1

            cv2.namedWindow("WebCam")
            cv2.moveWindow("WebCam", 20, 120)
            cv2.imshow("WebCam", imgg) # ve alınan görüntünün ekranda gösterilmesi
            cv2.waitKey(1)


                # "SAĞA"
            if right_wait >= 4:
                current_piece.x += 1
                if not (valid_space(current_piece, grid)):
                    current_piece.x -= 1
                left_wait = 0
                right_wait = 0
                rotate_wait = 0
                down_wait = 0

                # "ROTATE"
            if rotate_wait >= 4:
                current_piece.rotation += 1
                if not (valid_space(current_piece, grid)):
                    current_piece.rotation -= 1
                left_wait = 0
                right_wait = 0
                rotate_wait = 0
                down_wait = 0

            # "SOLA"
            if left_wait >= 4:
                current_piece.x -= 1
                if not (valid_space(current_piece, grid)):
                    current_piece.x += 1
                left_wait = 0
                right_wait = 0
                rotate_wait = 0
                down_wait = 0

        if control_method == "ses":
            # Algılanan ses komutunu kontrol et
            if voice_command == "sağ":
                current_piece.x += 1
                if not valid_space(current_piece, grid):
                    current_piece.x -= 1
                voice_command = ""
            elif voice_command == "döndür":
                current_piece.rotation += 1
                if not valid_space(current_piece, grid):
                    current_piece.rotation -= 1
                voice_command = ""
            elif voice_command == "sol":
                current_piece.x -= 1
                if not valid_space(current_piece, grid):
                    current_piece.x += 1
                voice_command = ""


        # şekil aşağı düşer
        if fall_time / 1000 > fall_speed:
            fall_time = 0  # yeni şekil için sıfırlar
            current_piece.y += 1  # Y ekseninde hareket ettir
            if not (valid_space(current_piece,grid)) and current_piece.y > 0:  # volid space ile şeklin geçerli bir boşlukta olup olmadığını kontrol et
                    current_piece.y -= 1  # geçerli değilse
                    change_piece = True


        shape_pos = convert_shape_format(current_piece) # parçanın konumu belirle ve oyundaki her hücredeki halini döndür

        # şeklin olduğu bölümü renklendirme
        for i in range(len(shape_pos)):
            x, y = shape_pos[i] #konumunu al
            if y > -1: # geçerli konumda ise
                grid[y][x] = current_piece.color # renklendir

        if change_piece: # eğer current piece true ise
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece # next şekil ile değiştir
            next_piece = get_shape() # sonraki şekli rastgele seç
            change_piece = False # parça değiştiği için true değeri değiştir
            score += add_score(clear_rows(grid, locked_positions)) # skor ekle
            fall_speed = fall_speed_real #düşüş hızı

            # oyun pencerelerini güncelle
            draw_window(win, grid, score)
            draw_next_shape(next_piece, win)
            pygame.display.update()

        if check_lost(locked_positions): # lose kontrol
            draw_text_middle(win,"KAYBETTIN!", 80, (255, 255, 255))
            pygame.display.update()
            pygame.time.delay(1500)
            run = False



        draw_window(win, grid, score) # oyun alanını ve skoru göstermek için
        draw_next_shape(next_piece, win) # sonraki pencere
        pygame.display.update() # gerçekleştirilen değişimleri güncelleyip kullanıcıya göstermek için

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # Boşluk tuşu ile durdurma/kaldırma
                    paused = not paused  # Oyun durumunu değiştir
                    if paused:
                        # Oyun duraklatıldığında ekrana çizilecek donmuş ekran görüntüsünü oluştur
                        paused_image = win.copy()
                        draw_text_middle(paused_image, "Duraklatıldı", 80, (255, 255, 255))
                        pygame.display.update()

                    while paused:
                        # Oyun duraklatıldığında ekrana donmuş ekran görüntüsünü göster
                        win.blit(paused_image, (0, 0))
                        pygame.display.update()
                        for event in pygame.event.get():
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_SPACE:
                                    paused = False
                                    break


    main_menu(win)  # Oyuncu kaybettiğinde direkt ana menüye dönmesi için
    pygame.display.quit()#oyun ekranından çık

def voice_command_handler():
    global voice_command
    recognizer = sr.Recognizer()

    while True:
        with sr.Microphone() as source:
            print("Komut bekleniyor...")
            audio = recognizer.listen(source)
            try:
                command = recognizer.recognize_google(audio, language='tr-TR')
                print(f"Algılanan Komut: {command}")
                command = command.lower()
                voice_command = command  # Algılanan komutu sakla

            except sr.UnknownValueError:
                print("Komut Algılanamadı.")
            except sr.RequestError:
                print("Ses Hizmetine Ulaşılamıyor.")



    #ana menü
def main_menu(win): # main
    run = True
    while run:
        win.fill((0, 0, 0))
        selected_shapes = select_difficulty()

        if selected_shapes:  # Eğer zorluk seçimi yapıldıysa
            control_method = select_control_method()  # Kontrol yöntemini seç
            if control_method:  # Eğer bir kontrol yöntemi seçildiyse
                run = False  # Döngüyü sonlandır
                pygame.mixer.music.play()
                main(win, control_method)  # Oyun ekranını, seçilen kontrol yöntemi ile başlat

        pygame.display.update()  # Ekran güncellemesi yap

    pygame.display.quit()

win = pygame.display.set_mode((s_width, s_height)) # oyun penceresine geç
pygame.display.set_caption('TETRIS') # pencere başlığı
main_menu(win) # ana menü