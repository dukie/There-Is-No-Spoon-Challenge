# The machines are gaining ground. Time to show them what we're really made of...

import itertools
from collections import defaultdict


width = int(raw_input())    # the number of cells on the X axis
height = int(raw_input())   # the number of cells on the Y axis

rawLines = list()
grid = list()
for i in xrange(height):
    line = raw_input()  # width characters, each either a number or a '.'
    rawLines.append("".join([x if x == '.' else '0' for x in line]))
    grid.append([int(x) if x != '.' else -1 for x in line])

nodesMap = defaultdict(lambda: defaultdict(lambda: list()))
nodesSet = set()

NODE_LINKS_TEMPLATE = {
    1: ((1, 0),),
    2: ((1, 1), (2, 0), (1, 0)),
    3: ((1, 1), (1, 2), (1, 0), (2, 0)),
    4: ((1, 1), (2, 2), (1, 2), (1, 0), (2, 0)),
    5: ((1, 1), (2, 2), (1, 2), (1, 0), (2, 0)),
    6: ((1, 1), (2, 2), (1, 2), (2, 0)),
    7: ((1, 1), (2, 2), (1, 2)),
    8: ((2, 2),),
}


class APUNode:
    def __init__(self, ID, listCombinations, numLinks, neighbors):
        self.neighbors = set([x for x in neighbors if x is not None])
        self.ID = ID
        self.numLinks = numLinks
        self.lastOnX = False
        self.lastOnY = False
        if listCombinations:
            self.combinations = listCombinations
            self.combNum = len(listCombinations)
            self.currentCombination = 0
        else:
            self.combinations = []
            self.combNum = 0
            self.currentCombination = 0
        self.haveLinks = self.numLinks

    def switchLinks(self):
        nextLink = self.currentCombination + 1
        self.currentCombination = nextLink if nextLink < self.combNum else 0
        return True if self.currentCombination > 0 else False

    def resetLinks(self):
        self.haveLinks = self.numLinks

    def resetCombinations(self):
        self.currentCombination = 0

    def resetAll(self):
        self.currentCombination = 0
        self.haveLinks = self.numLinks

    def tryEstablishLink(self, num):
        currentLink = self.haveLinks
        if currentLink < num:
            return False
        return True

    def establishLink(self, num):
        self.haveLinks -= num

    def getCurrentLink(self):
        if self.combNum > 0:
            return self.combinations[self.currentCombination]
        return []

    def __str__(self):
        return "{0}: CC: {1} CL: {2} TL: {3}".format(self.ID, self.getCurrentLink(), self.haveLinks, self.numLinks)

    def __repr__(self):
        return self.__str__()


class APU:
    def __init__(self, nodesList, nodesMap):
        self.nodesMap = nodesMap
        self.nodesList = nodesList
        self.nodesCount = len(self.nodesList)
        self.__findLastOnLine()

    def __findLastOnLine(self):
        self.xObjectsOnYAXIS = defaultdict(lambda: list())
        self.yObjectsOnXAXIS = defaultdict(lambda: list())
        lastX, lastY = self.nodesList[0]
        dictOfLastX = defaultdict(lambda: 0)
        dictOfLastX[lastY] = lastX
        self.xObjectsOnYAXIS[lastY].append((lastX, lastY))
        self.yObjectsOnXAXIS[lastX].append((lastX, lastY))
        for x, y in self.nodesList[1:]:

            self.xObjectsOnYAXIS[y].append((x, y))
            self.yObjectsOnXAXIS[x].append((x, y))

            if x != lastX:
                self.nodesMap[(lastX, lastY)].lastOnY = True
            if dictOfLastX[y] < x:
                dictOfLastX[y] = x
            lastX, lastY = x, y
        for y, x in dictOfLastX.items():
            self.nodesMap[(x, y)].lastOnX = True
        self.nodesMap[self.nodesList[self.nodesCount - 1]].lastOnY = True
        self.actualHeight = len(self.xObjectsOnYAXIS.keys())
        self.actualWidth = len(self.yObjectsOnXAXIS.keys())
        self.lastNode = self.nodesList[len(self.nodesList) - 1]
        self.maxY = max(self.xObjectsOnYAXIS.keys())
        self.maxX = max(self.yObjectsOnXAXIS.keys())
        self.minY = min(self.xObjectsOnYAXIS.keys())
        self.minX = min(self.yObjectsOnXAXIS.keys())

    def __insularityCheck(self, nodeObject, resultTree):
        OKY = True
        OKX = True
        xCoord = nodeObject.ID[0]
        if nodeObject.lastOnY:

            haveOnRight = max([xCoord] + self.yObjectsOnXAXIS.keys())
            if haveOnRight <= xCoord:
                return True
            OKY = False
            keyList = self.yObjectsOnXAXIS.keys()
            keyList.reverse()
            for key in keyList:
                if key > xCoord:
                    continue
                for node in self.yObjectsOnXAXIS[key]:
                    for child, linkWeight in resultTree[node]:
                        if child[0] > xCoord:
                            OKY = True
                            break
                    if OKY:
                        break
                if OKY:
                    break
        return OKY and OKX

    def __checkConnection(self, nodeObject, resultTree):
        if nodeObject.ID == self.lastNode:
            result = self.__insularityCheck(nodeObject, resultTree)
            return result and self.__checkPathToFirstNode(nodeObject, resultTree) and self.__checkCrossing(nodeObject,
                                                                                                           resultTree)
        elif nodeObject.lastOnY:
            return self.__insularityCheck(nodeObject, resultTree) and self.__checkCrossing(nodeObject, resultTree)
        return self.__checkCrossing(nodeObject, resultTree)

    def __checkCrossing(self, nodeObj, resultTree):
        nodeTuple = nodeObj.ID
        result = True
        for child, linkWeight in resultTree[nodeTuple]:
            if nodeTuple[0] > child[0] or nodeTuple[1] > child[1]:
                continue
            if nodeTuple[0] == child[0]:
                result &= self.__checkYCross(nodeTuple[1], child[1], nodeTuple[0], resultTree)
            else:
                result &= self.__checkXCross(nodeTuple[0], child[0], nodeTuple[1], resultTree)
                pass
            if not result:
                break
        return result

    def __checkYCross(self, y1, y2, xAxis, resultTree):
        for yCoord in range(y1 + 1, y2):
            listOfPossibleConflictNodes = self.xObjectsOnYAXIS.get(yCoord, None)
            if listOfPossibleConflictNodes is None:
                continue
            first = None
            second = None
            for x in range(xAxis - 1, self.minX - 1, -1):
                if (x, yCoord) in listOfPossibleConflictNodes:
                    first = (x, yCoord)
                    break
            if first is None:
                continue

            for x in range(xAxis + 1, self.maxX + 1):
                if (x, yCoord) in listOfPossibleConflictNodes:
                    second = (x, yCoord)
                    break
            if second is None:
                continue
            for child, linkWeight in resultTree[first]:
                if child == second:
                    return False
        return True

    def __checkXCross(self, x1, x2, yAxis, resultTree):
        for xCoord in range(x1 + 1, x2):
            listOfPossibleConflictNodes = self.yObjectsOnXAXIS.get(xCoord, None)
            if listOfPossibleConflictNodes is None:
                continue
            first = None
            second = None
            for y in range(yAxis - 1, self.minY - 1, -1):
                if (xCoord, y) in listOfPossibleConflictNodes:
                    first = (xCoord, y)
                    break
            if first is None:
                continue

            for y in range(yAxis + 1, self.maxY + 1):
                if (xCoord, y) in listOfPossibleConflictNodes:
                    second = (xCoord, y)
                    break
            if second is None:
                continue
            for child, linkWeight in resultTree[first]:
                if child == second:
                    return False
        return True

    def __checkPathToFirstNode(self, nodeObj, resultTree):
        xAxis = nodeObj.ID[0]
        nodesToCheck = self.yObjectsOnXAXIS[xAxis]
        for node in nodesToCheck:
            visited = set()
            if not self.__traverse(node, resultTree, visited):
                return False
        return True

    def __traverse(self, node, resultTree, visited):
        if node == self.nodesList[0]:
            return True
        if node in visited:
            return False
        visited.add(node)
        result = False
        for child, linkWeight in resultTree[node]:
            if child in visited:
                continue
            result |= self.__traverse(child, resultTree, visited)
            if result:
                break
        return result

    def solve(self):
        result = defaultdict(lambda: set())
        self.__solve(0, result)
        return result

    def __reset(self):
        for key, nodeObject in self.nodesMap.items():
            nodeObject.resetAll()

    def __solve(self, nodeNumber, resultTree, fromNode=None, lastLinkWeight=0):
        if nodeNumber >= self.nodesCount:
            return True

        nodeObject = self.nodesMap[self.nodesList[nodeNumber]]

        if nodeObject.haveLinks > 4:
            nodeObject.resetCombinations()
            return False

        if nodeObject.haveLinks == 0:
            solved = False
            if self.__checkConnection(nodeObject, resultTree):
                solved = self.__solve(nodeNumber + 1, resultTree)
            if solved:
                return True
            else:
                nodeObject.resetCombinations()
                return False

        linksNeed = 0
        for N in nodeObject.neighbors:
            linksNeed += min(2, self.nodesMap[N].haveLinks)

        if linksNeed < nodeObject.haveLinks:
            nodeObject.resetCombinations()
            return False

        if nodeObject.combNum == 0:
            if nodeObject.haveLinks == 0:
                return self.__solve(nodeNumber + 1, resultTree)
            else:
                return False

        hasNext = True
        while hasNext:
            currentCombination = nodeObject.getCurrentLink()
            needLinks = 0
            childOk = True
            for homeNode, child, linkWeight in currentCombination:
                needLinks += linkWeight
                if linkWeight > self.nodesMap[child].haveLinks:
                    childOk = False
                    break
            if nodeObject.haveLinks - needLinks != 0 or not childOk:
                hasNext = nodeObject.switchLinks()
                continue

            for homeNode, child, linkWeight in currentCombination:
                self.nodesMap[child].establishLink(linkWeight)
                nodeObject.establishLink(linkWeight)
                resultTree[child].add((nodeObject.ID, linkWeight))
                resultTree[nodeObject.ID].add((child, linkWeight))

            solved = False
            if self.__checkConnection(nodeObject, resultTree):
                solved = self.__solve(nodeNumber + 1, resultTree)

            if solved and nodeObject.haveLinks == 0:
                return True
            for homeNode, child, linkWeight in currentCombination:
                self.nodesMap[child].haveLinks += linkWeight
                resultTree[child].remove((nodeObject.ID, linkWeight))
                resultTree[nodeObject.ID].remove((child, linkWeight))
                nodeObject.haveLinks += linkWeight
            hasNext = nodeObject.switchLinks()
        nodeObject.resetCombinations()
        return False


def printMap(inMap):
    print "-----START-MAP-------"
    for key in inMap.keys():
        print key, inMap[key]
    print "------END-MAP--------"


def buildLinkMap(lines):
    key = 0
    while key < len(lines):
        haveNodes = lines[key].find("0")
        if haveNodes != -1:
            i = haveNodes
        else:
            key += 1
            continue
        while i < len(lines[key]):
            nodesMap[(i, key)]['links'] = grid[key][i]
            nodesSet.add((i, key))
            rightX = lines[key][i + 1:].find("0")
            rightX = rightX + i + 1 if rightX != -1 else -1
            rightY = key if rightX != -1 else -1
            YLst = "".join([x[i] for x in lines[key + 1:]])
            bottomY = YLst.find("0")

            bottomY = bottomY + key + 1 if bottomY != -1 else -1
            bottomX = i if bottomY != -1 else -1

            if rightX != -1:
                nodesMap[(i, key)]['neighbors'].append((rightX, rightY))
            else:
                nodesMap[(i, key)]['neighbors'].append(None)
            if bottomX != -1:
                nodesMap[(i, key)]['neighbors'].append((bottomX, bottomY))
            else:
                nodesMap[(i, key)]['neighbors'].append(None)

            if rightX != -1:
                i = rightX
            else:
                break
        key += 1


def getCombinations(nodeLinks, neighborsLinks):
    neighborsNum = len(neighborsLinks)

    def filterCombinations(comb):
        for x in range(len(comb)):
            if neighborsLinks[x] < comb[x]:
                return False
        return True

    nodeLnkTemplates = [x[:neighborsNum] for x in NODE_LINKS_TEMPLATE[nodeLinks]]
    combinations = list()
    for template in nodeLnkTemplates:
        combinations += filter(filterCombinations, set(itertools.permutations(template, neighborsNum)))

    return combinations


def buildNodesNeighborLinks(nMap):
    for key in nMap.keys():
        neighbors = nMap[key]['neighbors']
        combinations = getCombinations(nMap[key]['links'],
                                       [nMap[x]['links'] if x is not None else 0 for x in neighbors])
        for comb in combinations:
            nMap[key]['linksCombinations'].append(
                set([(key, neighbors[x], comb[x]) for x in range(len(comb)) if comb[x] > 0]))
    return nMap





def buildNodesMap(nodesDict):
    nodesObjMap = dict()
    for key in nodesDict.keys():
        nodesObjMap[key] = APUNode(key, nodesDict[key]['linksCombinations'], nodesDict[key]['links'],
                                   nodesDict[key]['neighbors'])
    return nodesObjMap


buildLinkMap(rawLines)

nodesMap = buildNodesNeighborLinks(nodesMap)

nodes = list(nodesSet)
nodes.sort(key=lambda x: x)

nodesObjMap = buildNodesMap(nodesMap)

apu = APU(nodes, nodesObjMap)


final = apu.solve()
printed = set()
for key in final:
    for child, linkWeight in final[key]:
        if ((key, child), linkWeight) in printed or ((child, key), linkWeight) in printed:
            continue
        printed.add(((key, child), linkWeight))
        print "{0} {1} {2} {3} {4}".format(key[0], key[1], child[0], child[1], linkWeight)
