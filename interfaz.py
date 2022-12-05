from numpy import rec
import speech_recognition as sr
import pyttsx3, keyboard, datetime, os, wikipedia,pywhatkit
import subprocess as sub
from pygame import mixer
import telebot
from tkinter import *
from PIL import Image
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser
from telethon import TelegramClient
#import database
#from chatterbot import ChatBot
#metodos para entrenar el chatbot
#from chatterbot.trainers import ListTrainer

#Interfaz grafica
main_window = Tk()
main_window.title("Kira AI")
main_window.geometry("1000x600")

#Trabajo con el gif para poder mostrarlo
kira_gif_path="asistente-robot.gif"
info_gif = Image.open(kira_gif_path)
gif_nframes = info_gif.n_frames

main_window.resizable(0,0)
main_window.configure(bg='white')
kira_gif_list = [PhotoImage(file=kira_gif_path, format=f'gif -index {i}') for i in range(gif_nframes)]
label_gif = Label(main_window)
label_gif.pack()

def animate_gif(index):
    frame = kira_gif_list[index]
    index += 1
    if index == gif_nframes:
        index = 0
    label_gif.configure(image=frame)
    main_window.after(50, animate_gif, index)  
    
animate_gif(0)      
        
canvas_comandos = Canvas(bg="white",height=200, width=195)
canvas_comandos.place(x=0,y=0)
comandos = """
            Comandos que puedes usar:
            -Repreduce..(cancion)
            -Busca..(algo)
            -Que hora es..
            -Abrí..(página web)
            -Alarma..(hora en 24hs)
            -Escribe una nota..
            -Enviar mensaje
            -Termina
"""
canvas_comandos.create_text(90, 80, text=comandos, fill="black", font='Arial 10')


# conversion de voz  a texto

microphone = sr.Microphone()
id_contact = 0


# conversion de texto a voz
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# configuracion de velocidad y volumen
engine. setProperty('rate', 145)
engine.setProperty('volume', 0.7)

# DICCIONARIO. Se pueden agregar todos los necesarios
sites = {
    'google': 'google.com',
    'youtube': 'youtube.com',
    'whatsapp': 'web.whatsapp.com'
}
# lo que dira
def talk(text):
    engine.say(text)
    engine.runAndWait()


def sendMessage(rec):
    # Info del emisor
    api_id = '13075588'
    api_hash = 'bbbe14126ccf3fb8da4f4dc1227575d5'
    #token = '5215528257:AAFfzC6WB-tghFrJomoSVOlOfgcl99k8xPE'
    phone = '+543794862238'
    client = TelegramClient('session', api_id, api_hash)
    client.connect()
    
    if not client.is_user_authorized():
        client.send_code_request(phone)
        client.sign_in(phone, '30678')

    talk('¿A quien quieres enviarlo?')
    contacto = listen("Te escucho")
    print(contacto)

    if 'martín' in contacto:
        id_contact = 79130525
    elif 'iván' in contacto:
        id_contact = 1727635591
    elif 'mariano' in contacto:
        id_contact = 1433875261

    talk('¿Cual es el mensaje?')
    mensaje = listen("Te escucho")
    print('Enviando mensaje....')
    try:
        receiver = InputPeerUser(id_contact, 0)
        client.send_message(receiver, mensaje, parse_mode='html')
        talk('Mensaje enviado')
    except Exception as e:
        print(e)
    client.disconnect()

#Funcion del bloc de notas
# Anota el texto en lineas separadas
def write(f):
    talk("¿Que quieres anotar?")
    rec_write = listen("Te escucho")
    f.write(rec_write + os.linesep)
    f.close()
    talk("Listo, puedes revisarlo")
    sub.Popen("nota.txt", shell=True)



def listen(phrase =None):
    listener = sr.Recognizer()
    with sr.Microphone() as source:
        listener.adjust_for_ambient_noise(source)
        talk(phrase)
        pc = listener.listen(source)        
    try: 
            rec = listener.recognize_google(pc, language='es-ES')
            rec = rec.lower()
    except sr.UnknownValueError:
        pass#talk("No te entendi, intenta de nuevo")
    except sr.RequestError as e:
        print("Could not request results from Speech Recognition service; {0}".format(e))
    return rec

#Funciones asociadas a las palabras clave

#Funcion para reproducir musica
def reproduce(rec):
    music = rec.replace("reproduce", '')
    print("reproduciendo" + music)
    talk("reproduciendo" + music)
    pywhatkit.playonyt(music)

#Funcion para buscar en wiki
def busca(rec):
    order = rec.replace('busca', '')
    wikipedia.set_lang("es")
    info = wikipedia.summary(order, 1)
    print("buscando: " + order)
    talk(info)

#Funcion para saber la hora
def hora(rec):
    hora = datetime.datetime.now().strftime('%I:%M %p')
    talk("Son las " + hora)

"""def alarma(rec):
    t = tr.Thread(target=clock, args=(rec,))
    t.start()"""

#Funcion para abrir otras pags
def abre(rec):
    for site in sites:
        if site in rec:
            sub.call(f'start chrome.exe {sites[site]}', shell=True)
            talk(f'Abriendo {site}')

#Funcion para crear una nota
def notas(rec):
    try:
        with open("nota.txt", 'a') as f:
            write(f)
    except FileNotFoundError as e:
        file = open("nota.txt", 'a')
        write(file)

#Funcion alarma
def clock(rec):
    num = rec.replace('alarma', '')
    num = num.strip()
    talk("alarma activada a las " + num + "horas")
    if num[0] != '0' and len(num) < 5:
        num = '0' + num    
    while True:
            if datetime.datetime.now().strftime('%H:%M') == num:
                mixer.init()
                mixer.music.load("auronplay-alarma.mp3")
                mixer.music.play()
            else:
                continue    
            if keyboard.read_key() == "s":
                mixer.music.stop()
                break

"""def conversar(rec):
    #Le estoy diciendo que no memorice todos los registros, los que se borran que se olvide, que los borre de la memoria
    chat = ChatBot("kira", database_uri=None)
    #le paso mi chatbot para entrenar
    trainer = ListTrainer(chat)
    trainer.train(database.get_question())
    talk("Vamos a conversar...!")
    while True:
        try:
            request = listen("Te escucho")
        except UnboundLocalError:
            talk("No te entendi, intenta de nuevo")
            continue 
        #obtiene la respuesta
        answer= chat.get_response(request)
        talk("Kira:" + answer)
        if 'chau kira' in request:
            break
   """ 
    
#diccionario de palabras clave
key_words = {
    'reproduce' : reproduce,
    'busca' : busca,
    'hora' : hora,
    'alarma' : clock,
    'abrí' : abre,
    'escribe una nota' : notas,
    'enviar mensaje' : sendMessage,
    #'conversar' : conversar,
}



#Funcion principal. ESTA REFACTORIZADA EXITOSAMENTE
def run_kira():
    while True:
        try:
            rec = listen("Te escucho")
        except UnboundLocalError:
            talk("No te entendi, intenta de nuevo")
            continue    
        if 'busca' in rec:
            key_words['busca'](rec)
            break
        else:
            for word in key_words:
                if word in rec:
                    key_words[word](rec)
        if 'termina' in rec:
            talk("Adios!")
            break  
        
    main_window.update()              
        

#principales botones s
button_listen = Button(main_window, text="Presione aqui para hablar", fg="black", font=('Arial', 10, 'bold'), command=run_kira)

button_listen.pack(pady=10)

main_window.mainloop()
