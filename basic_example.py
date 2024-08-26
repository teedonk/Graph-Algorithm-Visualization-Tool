from graphviz import Digraph

dot = Digraph()

# Adding nodes
dot.node('0', '0')
dot.node('1', '1')
dot.node('2', '2')
dot.node('3', '3')
dot.node('4', '4')
dot.node('5', '5')
dot.node('6', '6')
dot.node('7', '7')

# Adding edges with weights
dot.edge('0', '1', label='1')
dot.edge('0', '2', label='1')
dot.edge('1', '3', label='2')
dot.edge('3', '4', label='3')
dot.edge('4', '5', label='2')
dot.edge('2', '3', label='2')
dot.edge('2', '6', label='4')
dot.edge('6', '7', label='3')
dot.edge('5', '7', label='2')

dot.render('graph-output', view=True)
