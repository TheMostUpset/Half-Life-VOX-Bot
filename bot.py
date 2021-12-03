import pathlib, wave, os
curPath = str(pathlib.Path(__file__).parent.resolve()) + "/"
voxPath = curPath + "vox/" # path to the vox folder

fileList = os.listdir(voxPath)

MAX_FILE_LENGTH = 665600 # about one minute

ERR_EMPTY = 100
ERR_TOO_LONG = 101

def getSoundList(): # returns sound list
    list = fileList.copy()
    list.sort()
    for i, s in enumerate(list):
        list[i] = s.removesuffix(".wav")
    return list

def formatList(tbl):
    return ' '.join(tbl)

def getVOXfile(filename):
    return open(curPath + filename, "rb")

def createVOX(words, filename):
    filename = str(filename)
    words = words.lower()
    if "," in words: words = words.replace(",", " _comma")
    if "." in words: words = words.replace(".", " _period")
    words = words.split()
    
    output = bytearray()

    for word in words:
        wavFile = word + ".wav"
        if wavFile in fileList:
            file = wave.open(voxPath + wavFile, "rb")
            output += file.readframes(file.getnframes())
            file.close()
        else:
            print(wavFile + " was not found!")

    outputLength = len(output)
    if outputLength <= 0:
        return ERR_EMPTY, 0
    if outputLength > MAX_FILE_LENGTH:
        return ERR_TOO_LONG, 0

    framerate = 11025
    duration = outputLength / float(framerate)
    
    newfile = wave.open(curPath + filename + ".wav", "wb")
    newfile.setnchannels(1)
    newfile.setsampwidth(1)
    newfile.setframerate(framerate)
    newfile.writeframesraw(output)
    newfile.close()
    print("Created wav file " + filename + " with duration of " + str(duration) + " seconds")
    
    return filename + ".wav", duration

# telegram stuff goes below

TOKEN = "YOUR_TOKEN" # your telegram bot token

from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
# from telegram import InlineQueryResultVoice
# from telegram.ext import InlineQueryHandler

updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher

import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def botSendMessage(update, context, msg):
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

def start(update, context):
    botSendMessage(update, context, "Hello. Black Mesa Announcement System welcomes you to the chat. Remember: there is /list command.\nWarning: this may not work on iPhones.")
dispatcher.add_handler(CommandHandler('start', start))

def wordsList(update, context):
    botSendMessage(update, context, "Here's list of VOX sounds:")
    botSendMessage(update, context, formatList(getSoundList()[2:205]))
    botSendMessage(update, context, formatList(getSoundList()[205:410]))
    botSendMessage(update, context, formatList(getSoundList()[410:616]))
dispatcher.add_handler(CommandHandler('list', wordsList))

def echo(update, context):
    if update is None:
        return
    if update.message is None or update.message.text is None:
        botSendMessage(update, context, "An error occurred, please try again")
        return
    chatID = update.effective_chat.id
    voxFile, voxDur = createVOX(update.message.text, chatID)
    if voxFile is ERR_EMPTY:
        botSendMessage(update, context, "Unable to create sound file")
    elif voxFile is ERR_TOO_LONG:        
        botSendMessage(update, context, "Too long sentence")
    else:
        context.bot.send_voice(chat_id=chatID, voice=getVOXfile(voxFile), duration=voxDur)
        # context.bot.send_document(chat_id=chatID, document=getVOXfile(curPath + str(chatID) + ".wav")) # also send the file as document
        # TODO: delete voxFile after it was successfully sent
dispatcher.add_handler(MessageHandler(Filters.text & (~Filters.command), echo))

# unfinished inline functionality, that code was used for tests

# def inline_vox(update, context):
    # query = update.inline_query.query
    # if not query:
        # return
    # thisID = update.inline_query.id
    # results = list()
    # voxFile, voxDur = createVOX(query, thisID)
    # results.append(
        # InlineQueryResultVoice(
            # id=query.upper(),
            # title='Create VOX',
            # voice_url=getVOXfile(voxFile),
            # voice_duration=int(voxDur)
        # )
    # )
    # context.bot.answer_inline_query(thisID, results)
# dispatcher.add_handler(InlineQueryHandler(inline_vox))

updater.start_polling()