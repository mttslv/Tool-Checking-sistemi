from appJar import gui
import xlrd
import csv
import json
import networkx as nx
import matplotlib.pyplot as plt


def path_to_csv(filename):
    wb = xlrd.open_workbook(filename)
    sh = wb.sheet_by_name(wb.sheet_names()[0])

    # create a new .csv file and write into it convert excel file
    csv_file = open('untitled.csv', 'w')
    wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
    for rownum in range(sh.nrows):
        wr.writerow(sh.row_values(rownum))
    csv_file.close()

    return csv_file


def getGraph(csvFile):
    with csvFile as f:
        reader = csv.reader(f)
        arrayCsv = []
        states = []
        edges = []
        initialState = 0

        # add row for row in csv file
        for row in reader:
            # formattazione csv file
            # remove empty line
            if len(row) > 0:
                if row[1] != "":
                    arrayCsv.append(row)

        # analize csv file : add state in states list
        #    and edge in edges list
        for line, nextLine in zip(arrayCsv, arrayCsv[1:] + arrayCsv[: 1]):
            if (line[0] == "State2") or (line[0] == "FinalState2"):
                for col in line:
                    if col == 'ID':
                        id = nextLine[line.index(col)]
                    if col == 'Name':
                        if nextLine[line.index(col)] == "":
                            name = "finalState"
                        else:
                            name = nextLine[line.index(col)]

                states.append((id, name))

            elif line[0] == "Transition2":
                if initialState == 0:
                    for col in line:
                        if col == 'Target':
                            initialState = nextLine[line.index(col)]
                            print("initial state" + initialState)
                else:
                    for col in line:
                        if col == 'ID':
                            id = nextLine[line.index(col)]
                        if col == 'Name':
                            name = nextLine[line.index(col)]
                        if col == 'Source':
                            fromNode = nextLine[line.index(col)]
                        if col == 'Target':
                            toNode = nextLine[line.index(col)]
                    edges.append((fromNode, name, toNode))

        # for each edge[NodeFrom.id,message,NodeTo.id] convert node.id in node.name
        for state in states:
            for edge in edges:
                supportEdge = edges[edges.index(edge)]
                # (4,M3,4)->('S1','M3','S1')
                if supportEdge[0] == state[0] and supportEdge[2] == state[0]:
                    supportEdge = [state[1], edge[1], state[1]]
                # (4,M3,5)->('S1','M1',5)
                elif supportEdge[0] == state[0]:
                    supportEdge = [state[1], edge[1], edge[2]]
                # ->('S1','M1','S2')
                elif supportEdge[2] == state[0]:
                    supportEdge = [edge[0], edge[1], state[1]]
                # update edge in edges list
                edges[edges.index(edge)] = supportEdge

        # discover startState
        for state in states:
            if initialState == state[0]:
                initialState = state[1]

    return initialState, states, edges


# search path of k length in the graph G
def dfsK(G, k, initialState):
    class Node:

        def __init__(self, str):
            self.name = str

        def neighbors(self):
            neighborsList = []
            for edge in G[1]:
                if edge[0] == self.name:
                    neighborsList.append(edge)
            return neighborsList

    # convert states in object of class Node
    nodes = []
    for state in G[0]:
        nodes.append(Node(state))

    initialStateImpl = Node(initialState)

    # the stack(pila) is a pair of value < Node , path to walk to reach it>
    # add initialState to stack
    stack = [(initialStateImpl, [])]
    paths = []

    while len(stack) > 0:
        # element at the top of the stack
        stackObj = stack.pop()

        node = stackObj[0]
        pathNode = stackObj[1]
        # if length to reach the node is lesser then the max path length
        if len(pathNode) < (2 * k - 2):

            nodeNeighbors = node.neighbors()

            # increment the stack to remember the various possible choices
            if len(nodeNeighbors) > 0:
                for neighbor in nodeNeighbors:
                    pathNode = stackObj[1][:]
                    pathNode.append(neighbor[0])
                    pathNode.append(neighbor[1])

                    stack.append((Node(neighbor[2]), pathNode))
            # if node dont have neighbors it is a final state, and add the path to paths
            else:
                pathNode.append(node.name)
                paths.append(pathNode)
        else:
            pathNode.append(node.name)
            paths.append(pathNode)

    return paths


def add_file(btn):
    filename = app.openBox(None, None, (("excel file", "*.xlsx"),))
    app.setEntry('path', filename)


def genera_percorsi(btn):
    path = app.getEntry('path')

    csv_filename = str(path_to_csv(path).name)
    try:
        csvFile = open(csv_filename, 'r')
    except():
        print("error")

    graph = getGraph(csvFile)

    G = (graph[1], graph[2])

    profondita = int(app.getEntry('profondita'))

    paths = dfsK(G, profondita, graph[0])
    print(len(paths))

    nodes = []

    for node in graph[1]:
        nodes.append(node[1])

    with open("graph.json", 'w') as outfile:
        json.dump({'edges': graph[2], 'nodes': nodes}, outfile)

    app.clearListBox('listapercorsi')
    app.updateListBox('listapercorsi', paths)

    app.changeOptionBox('passarePerNodi', [])
    app.changeOptionBox('nonPassarePerNodi', [])

    nodi = []
    for nodo in graph[1]:
        nodi.append(str(nodo[1]))

    nodi = sorted(nodi)

    # key = lambda x: tuple(int(i) for i in re.findall('\d+', x)[:2])

    app.changeOptionBox('passarePerNodi', nodi)
    app.changeOptionBox('nonPassarePerNodi', nodi)
    # app.changeOptionBox('cappioSuNodi',nodi)
    # app.changeOptionBox('noCappioSuNodi', nodi)


def filtra(btn):
    passate = 0
    allItem = len(app.getAllListItems('listapercorsi'))
    item = 0
    all=[]
    activeCheckBoxPassaPer = []
    activeCheckBoxNonPassaPer = []

    for checkBox in app.getOptionBox('passarePerNodi'):
        if app.getOptionBox('passarePerNodi')[checkBox]:
            activeCheckBoxPassaPer.append(checkBox)

    for checkBox in app.getOptionBox('nonPassarePerNodi'):
        if app.getOptionBox('nonPassarePerNodi')[checkBox]:
            activeCheckBoxNonPassaPer.append(checkBox)

    # gestione lista percorsi: passare per nodi
    for percorso in app.getAllListItems('listapercorsi'):

        find = True
        item += 1

        #print(str(item)+"/"+str(allItem))
        current_percent_complete = (item / allItem) * 100
        print (str(int(current_percent_complete))+"%  -- Passa Per")

        passaPerNodi = activeCheckBoxPassaPer[:]

        while (len(passaPerNodi) > 0) and (find):
                nodo = passaPerNodi.pop()
                find = False
                for col in percorso:
                    passate += 1
                    if col == nodo:
                        find = True
                        break

        if find:
            print("trovato: "+str(percorso))
            #app.removeListItem('listapercorsi', percorso)
            all.append(percorso)

    app.clearListBox('listapercorsi')
    app.updateListBox('listapercorsi', all)
    print ("percorsi visibili dopo PASSA PER: "+str(len(app.getAllListItems('listapercorsi'))))
    print("numero confronti: "+str(passate))

    # gestione lista percorsi: non passare per nodi
    all = []
    passate = 0
    item = 0
    allItem = len(app.getAllListItems('listapercorsi'))

    for percorso in app.getAllListItems('listapercorsi'):
        find = False
        passaPerNodi = activeCheckBoxNonPassaPer[:]
        item += 1

        current_percent_complete = (item / allItem) * 100
        print(str(int(current_percent_complete)) + "%  -- Non Passa Per")

        while (len(passaPerNodi) > 0) and (not find):
            nodo = passaPerNodi.pop()
            for col in percorso:
                passate += 1
                if col == nodo:
                    find = True
                    #app.removeListItem('listapercorsi', percorso)
                    break

        if not find:
            print("trovato: " + str(percorso))
            # app.removeListItem('listapercorsi', percorso)
            all.append(percorso)

    app.clearListBox('listapercorsi')
    app.updateListBox('listapercorsi', all)
    print ("percorsi visibili dopo NON PASSA PER: " + str(len(app.getAllListItems('listapercorsi'))))
    print("numero confronti: " + str(passate))


def filtraCappi(btn):
    # gestione lista percorsi: passare per nodi
    for percorso in app.getAllListItems('listapercorsi'):
        trovata = True

        ciclaSuNodi = []
        for item in app.getOptionBox('cappioSuNodi'):
            if app.getOptionBox('cappioSuNodi')[item]:
                ciclaSuNodi.append(item)

        for nodo in ciclaSuNodi:
            trovata=False
            for col in percorso:
                if percorso.index(col)<len(percorso)-2:
                    if (percorso[percorso.index(col)] == nodo) and (percorso[percorso.index(col)+2] == nodo):
                        trovata=True

        if not trovata:
            app.removeListItem('listapercorsi', percorso)

    # gestione lista percorsi: non ciclare su nodi
    for percorso in app.getAllListItems('listapercorsi'):
            trovata = False

            ciclaSuNodi = []
            for item in app.getOptionBox('noCappioSuNodi'):
                if app.getOptionBox('noCappioSuNodi')[item]:
                    ciclaSuNodi.append(item)

            while len(ciclaSuNodi)>0 and not trovata:
            # for nodo in ciclaSuNodi:
                #if trovata==False:
                    trovata = False
                    nodo = ciclaSuNodi.pop()
                    for col in percorso:
                        if percorso.index(col) < len(percorso) - 2:
                            if (percorso[percorso.index(col)] == nodo) and (percorso[percorso.index(col) + 2] == nodo):
                                trovata = True
                                app.removeListItem('listapercorsi', percorso)
                                break


def export_paths(btn):
    filename = app.saveBox(None, None, fileTypes=(("json file", "*.json"),))
    path = app.getEntry('path')

    # csv_filename = str(path_to_csv(path).name)
    #
    # csvFile = open(csv_filename, 'r')
    #
    # graph = getGraph(csvFile)
    # nodes = []
    #
    # for node in graph[1]:
    #     nodes.append(node[1])

    with open(filename, 'w') as outfile:
        json.dump({"paths": app.getAllListItems('listapercorsi')}, outfile)


def genera_grafo(btn):
    selected = app.getListBoxPos('listapercorsi')[:]
    if len(selected) > 0:
        s = selected.pop()
        # print(s)
        # print(app.selectListItem('listapercorsi', s))
        # print(app.selectListItemAtPos('listapercorsi', s))
        # print(app.getAllListItems('listapercorsi')[s])
        colorPath(app.getAllListItems('listapercorsi')[s])


def colorPath(path):
    plt.clf()
    G = nx.DiGraph()
    file = json.load(open('graph.json'))

    nodesRed = []
    nodesGrey = []
    allNodes = {}

    print(path)
    paths = []
    for p in path[:]:
        if not path.index(p) % 2:
            p = p.replace(" ", "")
            paths.append(p)
    print(paths)

    for node in file['nodes'][:]:
        node = node.replace(" ", "")
        allNodes[str(node)] = str(node)
        find = False
        for elem in paths:
            if elem == node:
                find = True
                break
            else:
                find = False

        if find:
            nodesRed.append(node)
        else:
            nodesGrey.append(node)

    print("allnode:"+str(len(allNodes)))
    edgesRed = []
    edgesGrey = []
    for edge in file['edges'][:]:
        edge[0] = edge[0].replace(" ", "")
        edge[2] = edge[2].replace(" ", "")
        i = 0
        find = False
        while i < len(paths) - 1:
            if edge[0] == paths[i] and edge[2] == paths[i + 1]:
                find = True
                break

            else:
                find = False

            i += 1

        if find:
            edgesRed.append((edge[0], edge[2]))
        else:
            edgesGrey.append((edge[0], edge[2]))

    G.add_edges_from(edgesRed)
    G.add_edges_from(edgesGrey)

    optionsRed = {
        'width': 2,
        'edge_color': 'red',
        'alpha': 0.8
    }
    optionsGrey = {
        'width': 0.2,
        'edge_color': 'grey',
        'alpha': 0.5
    }

    pos = nx.spring_layout(G, k=50, iterations=50)
    nx.draw_networkx_nodes(G, pos, nodelist=nodesGrey, node_color='grey', node_size=300, alpha=0.5)
    nx.draw_networkx_nodes(G, pos, nodelist=nodesRed, node_color='red', node_size=500, alpha=0.8)
    nx.draw_networkx_edges(G, pos,
                           edgelist=edgesRed,
                           **optionsRed)
    nx.draw_networkx_edges(G, pos,
                           edgelist=edgesGrey,
                           **optionsGrey)

    nx.draw_networkx_labels(G, pos, allNodes, font_size=5)

    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    plt.axis('off')
    plt.show()





app = gui("Manage Paths")
# app.setGeometry(700,600)
# app.setLocation("CENTER")

app.addLabel('pathLabel', 'select excel file: ', 0, 0)
app.addEntry('path', 0, 1)
app.setEntryDefault('path', 'path')
app.addButton('Sfolgia', add_file, 0, 2)

app.addLabel('profonditaLabel', 'profondità visita: ', 1, 0)
app.addNumericEntry('profondita', 1, 1)
app.setEntryDefault('profondita', 'lunghezza path')
app.addButton('genera percorsi', genera_percorsi, 1, 2)

app.addHorizontalSeparator(2, 0, 5, colour="grey")
app.addListBox('listapercorsi', [], 3, 0, 3, 8)
app.setListBoxSubmitFunction('listapercorsi', genera_grafo)

app.addButton('export paths', export_paths, 11, 1)
app.addVerticalSeparator(3,3,0,9,colour="grey")

app.addLabel('labelfiltri','manage filter',3,4)
app.setLabelBg('labelfiltri',"green")
app.addTickOptionBox('passarePerNodi', [], 4, 4)
app.addTickOptionBox('nonPassarePerNodi', [], 5, 4)
app.addButton('add filter', filtra, 6, 4)
app.addHorizontalSeparator(7,4, colour="grey")

# app.addLabel('labelcicli','manage cicles',8,4)
# app.setLabelBg('labelcicli',"green")
# app.addTickOptionBox('cappioSuNodi', [], 9, 4)
# app.addTickOptionBox('noCappioSuNodi', [], 10, 4)
# app.addButton('add cappi', filtraCappi, 11, 4)

app.go()
