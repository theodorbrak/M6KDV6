# -*- coding: utf-8 -*-

import pygame

#assuming a structure of
# Node:
#   item : "name", str
#   equation : "equation" str, can also be a number in str
#   nId : node ID, int
#
# Graph:
#   nodes : dictionary of nodes {nId : node}
#   

def convertion(text, var_dict):
    if protection(text):
        try :
            result = eval(text, var_dict)
            assert type(result) == int
            return result
        except:
            print("except problem")
            return False
    else:
        print("protek")
        return False

def protection(text):
    assert type(text) == str, "not a string"

    allowed_characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-+*/()"
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    disallowed_words = ["import", "execute", "run", "if"]


    word = ""
    for character in text:
        if not character in allowed_characters:
            print(f"no bueno char : {character}")
            return False
        if character in alphabet:
            word += character
        elif word.lower() in disallowed_words:
            print(f"no bueno word : {word}")
            return False
        else:
            word == ""
    if word.lower() in disallowed_words:
        print(f"no bueno word : {word}")
        return False
    return True

class Node:
    def __init__(self, item, equation, nId):
        self.position = (None, None)
        self.item = item
        self.equation = equation
        self.nId = nId

class Graph:
    def __init__(self):
        self.nodes = {} # nId : node

    def max_nId(self):
        max_nId = 0
        for node in self.nodes:
            if node.nId > max_nId:
                max_nId = node.nId
        return max_nId

def find_dependencies(node):

    equation = node.equation

    ignored_words = ["sqrt"]
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

    dependencies = []

    for character in equation:
        if character in alphabet:
                    word += character
        elif not word.lower() in ignored_words:
            dependencies.append(word)
            word = ""
        else:
            word = ""
    if not word.lower() in ignored_words:
        dependencies.append(word)
    return dependencies

def item_to_nId(item, graph):

    for node in graph.nodes:
        if item == node.item:
            return node.nId
    else:
        return False

def calculating_algorithm(graph):
    #finding a root (static input number)
    #
    assert len(graph.nodes) > 0, "no nodes"

    calculated = []
    dependencies = {} # nId : dependencies
    
    for i in graph.nodes.keys():
            if not i in calculated:
                calculated.append(i)
                try:
                    recursive_calculation(graph, dependencies)
                except:
                    print("looping equation or missing nodes")

                for key in dependencies.keys():
                    if key not in calculated:
                        calculated.append(key)

    # So now dependencies should have all nIds associated to their node's value

    return dependencies

def recursive_calculation(graph, nId, dependencies):

    dependencies[nId] = find_dependencies(graph.nodes[nId])

    if dependencies[nId] == []:
        dependencies[nId] = float(graph.nodes[nId].equation)
        return
    
    for item in dependencies[nId]:
        item_nId = item_to_nId(item)
        if item_nId not in dependencies.keys():
            recursive_calculation(graph, item_nId, dependencies)

    var_dict = {}
    for item in dependencies[nId]:
        item_nId = item_to_nId(item)
        var_dict[item] = dependencies[item_nId]

    dependencies[nId] = float(convertion(graph.nodes[nId].equation, var_dict))

def draw_number(screen, font, number, pos):
    text = str(number)
    render = font.render(text, True, (0,0,0))
    pygame.draw.rect(screen, (255,255,255),((pos[0] - 5, pos[1] - 5),(40, 10)))
    screen.blit(render, pos)

def draw_all_numbers(screen, font, graph, node_values):

    for nId in node_values.keys():
        pos = graph.nodes[nId].position
        draw_number(screen, font, node_values[nId], (pos[0] - 15, pos[1] + 40))