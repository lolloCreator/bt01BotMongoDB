import logging
import os
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
)
from pymongo import MongoClient, TEXT, DESCENDING
import certifi

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

TIPO, COMUNE, SOPRALLUOGO, CAVOGUASTO = range(4)
NODO1, NODO2, SALVA, CANCELLA, COMPLETA = 8, 9, 10, 11, 12
dizionario = {"tipo":"", "comune":"", "nodo1":"", "nodo2":""}


def get_user_collection(user):
    client = MongoClient('mongodb+srv://lolloCreator:Luigi_1998@clusterbt01.y7eaf.mongodb.net/db01db', tlsCAFile=certifi.where())
    db = client.test_database

    user_collection = db["db01collection"]
    return user_collection







def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [['SOPRALLUOGO'], ['CAVO GUASTO']]

    message = 'Ciao, seleziona una attività da aggiungere.\n\n' \
              'Se non visualizzi il menù, clicca sull\'icona in basso a destra sulla barra di scrittura. \n\n' \
              'Puoi annullare questa conversazione in qualsiasi punto utilizzando il comando:\n /cancel'

    reply_markup = ReplyKeyboardMarkup(reply_keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True,
                                       input_field_placeholder='Boy or Girl?')

    update.message.reply_text(message, reply_markup= reply_markup)

    return TIPO


def gender(update: Update, context: CallbackContext) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    logger.info("Nome utente: %s e Tipo attività: %s", user.first_name, update.message.text)
    dizionario['tipo'] = update.message.text

    message = 'Okay, per l\'attività: "%s", ho bisogno di sapere il comune' % update.message.text

    reply_keyboard = [['Arienzo'], ['Capodrise'], ['Cervino'], ['Macerata Campania'], ['Maddaloni'], ['Marcianise'], ['Portico di Caserta'], ['Recale'], ['S.Felice a Cancello'], ['S.N.La Strada'], ['S.Maria a Vico'], ['Valle di Maddaloni'], ['S.Marco Evangelista']]

    reply_markup = ReplyKeyboardMarkup(reply_keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True,
                                       input_field_placeholder='Seleziona un comune')



    update.message.reply_text(message,reply_markup= reply_markup)

    return COMUNE


def photo(update: Update, context: CallbackContext) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    logger.info("Photo of %s: %s", user.first_name, update.message.text)
    dizionario['comune'] = update.message.text

    print(dizionario['tipo'])
    if dizionario['tipo'] == 'SOPRALLUOGO':
        update.message.reply_text(
            'Sopralluoghi non ancora implementati', reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    elif dizionario['tipo'] == 'CAVO GUASTO':
        update.message.reply_text(
            'Scrivi nodo 1', reply_markup=ReplyKeyboardRemove()
        )
        return NODO1


def nodo1(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("Photo of %s: %s", user.first_name, update.message.text)
    dizionario['nodo1'] = update.message.text
    update.message.reply_text(
        'Scrivi nodo 2', reply_markup=ReplyKeyboardRemove()
    )
    return NODO2


def printDic(update: Update, context: CallbackContext) -> int:
    dizionario['nodo2'] = update.message.text
    message = ""
    for chiave, valore in dizionario.items():
        message += chiave + " : " + valore + "\n"
    update.message.reply_text(
        message, reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def completa(update: Update, context: CallbackContext) -> int:
    dizionario['nodo2'] = update.message.text
    message = ""
    for chiave, valore in dizionario.items():
        message += chiave + " : " + valore + "\n"
    message += "\nQuesti dati sono corretti?"

    reply_keyboard = [['SALVA'], ['ANNULLA']]

    reply_markup = ReplyKeyboardMarkup(reply_keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True,
                                       input_field_placeholder='Boy or Girl?')

    update.message.reply_text(
        message, reply_markup=reply_markup
    )
    return COMPLETA


def salva(update: Update, context: CallbackContext) -> int:
    user_collection = get_user_collection(update.message.from_user)
    doc_id = user_collection.insert_one(dizionario)
    print(doc_id)
    if doc_id:
        update.message.reply_text(
        'Salvato', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def annulla(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Cancellato', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Operazione annullata', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def listaCaviGuasti(update:Update, context:CallbackContext) -> int:
    user_collection = get_user_collection(update.message.from_user)
    x = user_collection
    lista = ""
    for x in x.find():
        lista+= x["comune"]+":\nTra Nodo BT "+x["nodo1"]+" e Nodo BT "+x["nodo2"]+"\n\n"
    update.message.reply_text(
        lista, reply_markup=ReplyKeyboardRemove()
    )


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    TOKEN = '5111264889:AAFtCG0lLWSiHLLLiSU_jwocWU5RJxO0e3c'
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TIPO: [MessageHandler(Filters.regex('^(SOPRALLUOGO|CAVO GUASTO|Other)$'), gender)],
            COMUNE: [MessageHandler(Filters.regex(
                '^(Arienzo|Capodrise|Cervino|Macerata Campania|Maddaloni|Marcianise|Portico di Caserta|Recale|S.Felice a Cancello|S.N.La Strada|S.Maria a Vico|Valle di Maddaloni|S.Marco Evangelista)$'),
                                    photo)],
            NODO1: [MessageHandler(Filters.text, nodo1)],
            NODO2: [MessageHandler(Filters.text, completa)],
            COMPLETA: [MessageHandler(Filters.regex('^(SALVA)$'), salva),
                       MessageHandler(Filters.regex('^(ANNULLA)$'), annulla)],

        },
        fallbacks=[CommandHandler('cancel', cancel)],

    )

    dp.add_handler(conv_handler)

    dp.add_handler(CommandHandler("lista_cavi_guasti", listaCaviGuasti))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()