import sys
import pickle as pk
import networkx as nx
import matplotlib.pyplot as plt
from antlr4 import *
from EnquestesLexer import EnquestesLexer
from EnquestesParser import EnquestesParser
from antlr4.InputStream import InputStream
from EnquestesVisitor import EnquestesVisitor

if len(sys.argv) > 1:
    input_stream = FileStream(sys.argv[1], encoding='utf-8')
else:
    input_stream = InputStream(input('? '))
lexer = EnquestesLexer(input_stream)
token_stream = CommonTokenStream(lexer)
parser = EnquestesParser(token_stream)
tree = parser.chatbot()

visitor = EnquestesVisitor()
G = visitor.visit(tree)

Gname = G.graph["name"]

nx.write_gpickle(G, "../bot/%s.pickle" % Gname)
pregunta_resposta = nx.get_edge_attributes(G, 'item')
alternatives = nx.get_edge_attributes(G, 'alternativa')
edge_colors = ['blue' if e in pregunta_resposta else 'green'
               if e in alternatives else 'black' for e in G.edges]
nx.draw_circular(G, with_labels=True, edge_color=edge_colors, node_size=550)
nx.draw_networkx_edge_labels(G, pos=nx.circular_layout(G),
                             edge_labels=pregunta_resposta, font_color='blue')
nx.draw_networkx_edge_labels(G, pos=nx.circular_layout(G),
                             edge_labels=alternatives, font_color='green')
plt.show()
