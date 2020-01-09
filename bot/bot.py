import telegram
import random
import os
import matplotlib.pyplot as plt
import pickle as pk
import networkx as nx
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import PicklePersistence


def help(bot, update, user_data):
    f = open('help.md', 'r')
    bot.send_message(chat_id=update.message.chat_id, text=f.read(),
                     parse_mode=telegram.ParseMode.MARKDOWN)


def end(bot, update, user_data):
    root = user_data['quiz'].name
    file = open("%s_results.pickle" % root, "wb")
    pk.dump(user_data['results'], file)
    file.close()
    print("entra")
    bot.send_message(chat_id=update.message.chat_id, text="%s> Gràcies pel seu temps!" % root)


def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hola sóc en" +
                     " Joan Muntaner un bot de enquestes.")


def author(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Autor: " +
                     "Niebo Zhang\nCorreu: niebo.zhang@est.fib.upc.edu")


def write_question(bot, update, user_data):
    question = user_data['state']
    if question == 'END':
        end(bot, update, user_data)
    else:
        write = user_data['quiz'].name + '> ' + \
            user_data['quiz'].node[question]['pregunta'] + '\n'
        answer = [(a, b) for (a, b) in user_data['quiz'].edges(question)
                  if 'item' in user_data["quiz"][a][b]]
        options = user_data['quiz'].node[answer[0][1]]['options']
        for o in options:
            write = write + o + '\n'
        bot.send_message(chat_id=update.message.chat_id, text=write)


def quiz(bot, update, args, user_data):
    if len(args) < 1:
        bot.send_message(chat_id=update.message.chat_id, text="Introdueix " +
                         "una enquesta!")
    else:
        try:
            file = open("%s.pickle" % args[0], 'rb')
            enquesta_graph = pk.load(file)
            file.close()
        except Exception as e:
            bot.send_message(chat_id=update.message.chat_id, text="L'enquesta " +
                             "no existeix!")
            return
        user_data["quiz"] = enquesta_graph
        if os.path.exists("%s_results.pickle" % args[0]):
            file = open("%s_results.pickle" % args[0], 'rb')
            user_data["results"] = pk.load(file)
            file.close()
        else:
            user_data["results"] = {}
            question = nx.get_node_attributes(enquesta_graph, "pregunta")
            items = nx.get_edge_attributes(enquesta_graph, "item")
            answer = nx.get_node_attributes(enquesta_graph, "options")
            for q in question:
                for (q2, t) in items:
                    if(q == q2):
                        options = answer[t]
                        for o in options:
                            user_data["results"][(q, o.split(":")[0])] = 0
        root = enquesta_graph.name
        bot.send_message(chat_id=update.message.chat_id, text="Enquesta" +
                         " %s:" % root)
        question = list(enquesta_graph.edges(root))[0][1]
        user_data['state'] = question
        write_question(bot, update, user_data)


def question(bot, update, user_data):
    if 'state' in user_data:
        if user_data['state'] != 'END':
            state = user_data['state']
            G = user_data['quiz']
            answer = update.message.text
            if (state, answer) not in user_data['results']:
                bot.send_message(chat_id=update.message.chat_id,
                                 text="La resposta no està dins de les opcions!")
                return
            else:
                user_data['results'][(state, answer)] += 1
                user_data['alternativa'] = False
                for e in G[state]:
                    if 'alternativa' in G[state][e]:
                        if(G[state][e]['alternativa'] == answer):
                            user_data['alternativa'] = True
                            user_data['state'] = e
                    elif 'item' not in G[state][e]:
                        nextAux = e
                if(user_data['alternativa']):
                    if 'parent_state' not in user_data:
                        user_data['parent_state'] = nextAux
                else:
                    try:
                        user_data['state'] = nextAux
                    except NameError:
                        user_data['state'] = user_data['parent_state']
                write_question(bot, update, user_data)


def pie(bot, update, args, user_data):
    try:
        if user_data['state'] == 'END':
            try:
                name = user_data['quiz'].name
                file = open("%s_results.pickle" % name, 'rb')
                results = pk.load(file)
                file.close()
            except Exception as e:
                bot.send_message(chat_id=update.message.chat_id,
                                 text="El pie no està disponible.")
                return
            idQ = args[0]
            options = []
            option_count = []
            for (question, option) in user_data['results']:
                if question == idQ:
                    options.append(option)
                    option_count.append(user_data['results'][(question,
                                                             option)])
            if(len(options) == 0):
                bot.send_message(chat_id=update.message.chat_id,
                                 text="%s no existeix en l'enquesta." % idQ)
                return
            plt.clf()
            explode = (0.1,) * len(options)
            fitxer = "%d.png" % random.randint(1000000, 9999999)
            plt.pie(option_count, labels=options, explode=explode, shadow=True,
                    autopct='%1.1f%%')
            plt.savefig(fitxer, bbox_inches='tight')
            bot.send_photo(chat_id=update.message.chat_id,
                           photo=open(fitxer, 'rb'))
            os.remove(fitxer)
        else:
            bot.send_message(chat_id=update.message.chat_id, text="Enquesta " +
                             "en processament, acaba primer l'enquesta, " +
                             "altrament introdueix \end per finalitzar-la" +
                             "(Atenció: els resultats no es guardaran).")
    except Exception as e:
        bot.send_message(chat_id=update.message.chat_id, text="Tria una " +
                         "enquesta disponible.")


def bar(bot, update, args, user_data):
    try:
        if user_data['state'] == 'END':
            try:
                name = user_data['quiz'].name
                file = open("%s_results.pickle" % name, 'rb')
                results = pk.load(file)
                file.close()
            except Exception as e:
                bot.send_message(chat_id=update.message.chat_id, text="El " +
                                 "bar no està disponible.")
                return
            idQ = args[0]
            options = []
            option_count = []
            for (question, option) in user_data['results']:
                if question == idQ:
                    options.append(option)
                    option_count.append(user_data['results'][(question,
                                                             option)])
            if(len(options) == 0):
                bot.send_message(chat_id=update.message.chat_id,
                                 text="%s no existeix en l'enquesta." % idQ)
                return
            plt.clf()
            fitxer = "%d.png" % random.randint(1000000, 9999999)
            plt.bar(options, option_count)
            plt.savefig(fitxer, bbox_inches='tight')
            bot.send_photo(chat_id=update.message.chat_id,
                           photo=open(fitxer, 'rb'))
            os.remove(fitxer)
        else:
                bot.send_message(chat_id=update.message.chat_id,
                                 text="Enquesta en processament, " +
                                 "acaba primer l'enquesta, altrament " +
                                 "introdueix \end per finalitzar-la" +
                                 "(Atenció: els resultats no es guardaran).")
    except Exception as e:
        bot.send_message(chat_id=update.message.chat_id, text="Tria " +
                         "una enquesta disponible")


def report(bot, update, user_data):
    try:
        name = user_data['quiz'].name
        file = open("%s_results.pickle" % name, 'rb')
        results = pk.load(file)
        file.close()
        resultats = 'pregunta valor respostes\n'
        for (pregunta, opcio) in results:
            resultats = resultats + pregunta + ' ' + opcio + ' ' + \
                 str(results[(pregunta, opcio)]) + '\n'
        bot.send_message(chat_id=update.message.chat_id, text=resultats)
    except Exception as e:
        bot.send_message(chat_id=update.message.chat_id, text="Report" +
                         "no disponible.")


def end_quiz(bot, update, user_data):
    try:
        if user_data['state'] != 'END':
            user_data['state'] = 'END'
        bot.send_message(chat_id=update.message.chat_id, text="S'ha " +
                         "finalitzat l'enquesta sense guardar els valors.")
    except Exception as e:
        return


persist = PicklePersistence(filename='user_data.pickle')
TOKEN = open('token.txt').read().strip()
updater = Updater(token=TOKEN)
dispatcher = updater.dispatcher
dispatcher.persistence = persist
dispatcher.user_data = persist.get_user_data()

dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('author', author))
dispatcher.add_handler(CommandHandler('report', report, pass_user_data=True))
dispatcher.add_handler(CommandHandler('quiz', quiz, pass_args=True,
                                      pass_user_data=True))
dispatcher.add_handler(MessageHandler(Filters.text, question,
                                      pass_user_data=True))
dispatcher.add_handler(CommandHandler('pie', pie, pass_args=True,
                                      pass_user_data=True))
dispatcher.add_handler(CommandHandler('bar', bar, pass_args=True,
                                      pass_user_data=True))
dispatcher.add_handler(CommandHandler('end', end_quiz, pass_user_data=True))
dispatcher.add_handler(CommandHandler('help', help, pass_user_data=True))

updater.start_polling()
