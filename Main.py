# -*- coding: utf-8 -*-

# @author: fleau




import math, pygame, sys


def draw_text_box(screen, draw_underscore, text, font, pos=(0, 325)):
    if draw_underscore:
        text += "_"
    pygame.draw.rect(screen, (255,255,255), ((0, 300),(1200, 50)))
    pygame.draw.rect(screen, (50,50,50), ((0, 300),(1200, 50)), 4)

    render = font.render(text, True, (0,0,0))
    screen.blit(render, (pos[0]+25, pos[1]-12))

def check_edge_existence(graph, node_1, node_2):
    for edge in graph.edges.values():
        nIds = [edge.nId_1, edge.nId_2]

        if node_1.nId in nIds and node_2.nId in nIds:
            return True, edge
    return False, None

def draw_disc(screen, color, size, pos):
    surface = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (size,size), size)
    screen.blit(surface, (pos[0]-size, pos[1]-size))

def render_outlined_text(text, color, font, width):
    outline_color = (255 - color[0], 255 - color[1], 255 - color[2])
    base = font.render(text, True, color)
    edge = font.render(text, True, outline_color)
    surface = pygame.Surface((base.get_width() + width*2, base.get_height() + width*2), pygame.SRCALPHA)

    for x in range(-width, width + 1):
        for y in range(-width, width + 1):
            if x * x + y * y <= width * width:
                surface.blit(edge, (width + x, width + y))
    surface.blit(base, (width, width))
    return surface


def draw_sidebar(index, font, pos, screen):
    bars = ("Edit", "settings", "graphs")
    
    text = font.render(bars[index], True, (255,240,240))
    pygame.draw.rect(screen, (80, 80, 80), (pos, (80, 32)))
    pygame.draw.rect(screen, (30, 30, 30), (pos, (80, 32)), 2)

    screen.blit(text, (pos[0]+16, pos[1]+8))


def mouse_press_status_toggle_check(status, to_be_checked, mouse_pos, graph):
    mx, my = mouse_pos[0], mouse_pos[1]
    bool_ = to_be_checked in ["delete_node", "add_edge", "delete_edge"]
    if not status[to_be_checked][0] or bool_:
        for node in graph.nodes.values():
            if (mx - node.position[0])**2 + (my - node.position[1])**2 <= node_size**2:
                if bool_:
                    return node, True 
                status[to_be_checked] = [True, node]
    else:
        status[to_be_checked][0] = False

    if bool_:
        return None, False

def make_surface(size, color):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    surface.fill(color)
    return surface

def delta_position(coords_1, coords_2):
    dx1 = coords_2[0] - coords_1[0]
    dy1 = coords_2[1] - coords_1[1]
    return (dx1, dy1)

def draw_edit_tab(screen, text_dict, image_dict): #current screen size 1200px witdh, 650px height
    surface = make_surface((1200, 100), (100, 100, 100, 180))

    screen.blit(surface, (0, 550)) #big gray area

    screen.blit(pygame.transform.scale(image_dict["close.png"], (32,32)), (1150, 560))

    screen.blit(pygame.transform.scale(image_dict["add.png"], (32,32)), (1000, 585))        # 1000:1032x,   585:617y
    screen.blit(pygame.transform.scale(image_dict["substract.png"], (32,32)), (960, 585))   # 960:992x,     585:617y
    screen.blit(text_dict["Nodes"], (950,550))

    screen.blit(pygame.transform.scale(image_dict["add.png"], (32,32)), (850, 585))         # 850:882,   585:617y
    screen.blit(pygame.transform.scale(image_dict["substract.png"], (32,32)), (810, 585))   # 810:842,     585:617y
    screen.blit(text_dict["Edges"], (800,550))

    
    
class Node:
    def __init__(self, position, nId):
        self.position = position            #Location on the board [x, y]
        self.nId = nId                      #Node ID
        self.item = None                    #text or img idk yet maybe both. both ? both. both.

    def set_item(self, item):
        self.item = item
    
    def draw(self, screen, cam_pos, size):
        centre =  (round(self.position[0] - cam_pos[0]), round(self.position[1] - cam_pos[1]))
        if not screen.get_rect().inflate(size*2, size*2).collidepoint(centre):
            return
        pygame.draw.circle(screen, (140, 140, 240), centre, size)
        pygame.draw.circle(screen, (0,0,0), centre, size,3)

    def draw_setting(self, screen):
        surface = make_surface((300, 200), (50, 50, 50, 180))
        screen.blit(surface, (self.position[0]+15, self.position[1]+15))

class Edge:
    def __init__(self, node_1, node_2, equation, eId):
        self.nId_1 = node_1.nId     # source node nId
        self.nId_2 = node_2.nId     # destination node nId
        self.equation = equation    # The equation
        self.eId = eId              # edge ID

    def change_source(self, node):
        self.nId_1 = node.nId

    def change_destination(self, node):
        self.nId_2 = node.nId

    def change_equation(self, equation):
        self.equation = equation

    def draw(self, screen, cam_pos, width, node_radius, graph):
            centre_1 =  (round(graph.nodes[self.nId_1].position[0] - cam_pos[0]), round(graph.nodes[self.nId_1].position[1] - cam_pos[1]))
            centre_2 =  (round(graph.nodes[self.nId_2].position[0] - cam_pos[0]), round(graph.nodes[self.nId_2].position[1] - cam_pos[1]))
            if not screen.get_rect().inflate(width*2, width*2).collidepoint(centre_1) or not screen.get_rect().inflate(width*2, width*2).collidepoint(centre_2):
                return
            # Math
            d_pos = delta_position(centre_1, centre_2)
            alpha = math.atan2(d_pos[1], d_pos[0])

            b1, h1 = node_radius*math.cos(alpha), node_radius*math.sin(alpha)
            b2, h2 = node_radius*math.cos(alpha + math.pi), node_radius*math.sin(alpha + math.pi)
            tip1 = (centre_1[0] + b1, centre_1[1] + h1)
            tip2 = (centre_2[0] + b2, centre_2[1] + h2)
            pygame.draw.line(screen, (0,0,0), tip1, tip2, width)

            L = width*8
            L_2 = L*math.sqrt(2)/4

            theta = alpha + math.pi

            p1 = (tip2[0] + L*math.cos(theta - math.pi/4),    tip2[1] + L*math.sin(theta - math.pi/4))
            p2 = (tip2[0] + L_2*math.cos(theta),            tip2[1] + L_2*math.sin(theta))
            p3 = (tip2[0] + L*math.cos(theta + math.pi/4),    tip2[1] + L*math.sin(theta + math.pi/4))

            pygame.draw.polygon(screen,(0,0,0),[tip2,(p1),(p2),(p3)])

class Graph:
    def __init__(self):
        self.nodes = {} # nId : node
        self.edges = {} # eId : edge

    def add_node(self, node):
        self.nodes[node.nId] = node

    def add_edge(self, edge):
        self.edges[edge.eId] = edge

    def remove_node(self, node):
        for eId in list(self.edges):
            e = self.edges[eId]
            if e.nId_1 == node.nId or e.nId_2 == node.nId:
                self.remove_edge(e)
        self.nodes.pop(node.nId)

    def remove_edge(self, edge):
        self.edges.pop(edge.eId)

    def draw(self, screen, cam_pos, node_size, edge_thickness):
        for node in self.nodes.values():
            node.draw(screen, cam_pos, node_size)
        for edge in self.edges.values():
            edge.draw(screen, cam_pos, edge_thickness, node_size, self)

        

pygame.init()
screen = pygame.display.set_mode((1200, 650)) #built for 1280 x 720 i have to do this
clock = pygame.time.Clock()
pygame.display.set_caption("Satisfactory node graph calculator") # wink wink

font_sidebar = pygame.font.SysFont(None, 30)
font_edit_menu = pygame.font.SysFont(None, 40)

eId, nId = 0, 0 # Indexes
node_size = 36.0 # Size in pixels of a node
edge_thickness = 4 # Width in pixels of an edgeeeeeee
camera_position = [0,0]
typed = ""


status = {"pickup" : [False, None], 
          "setting" : [False, None], 
          "edit_tab" : True, 
          "delete_node" : [False, None],
          "delete_edge" : [False, [None,None]],
          "add_edge" : [False, None],
          "typing" : [False, None]}

bar_offset = {"edit_tab" : 0}
default_images = {"close.png" : pygame.image.load("assets/image/default/close.png"), "add.png" : pygame.image.load("assets/image/default/add.png"),"substract.png" : pygame.image.load("assets/image/default/substract.png")}
default_sounds = {"error.ogg" : pygame.mixer.Sound("assets/sound/default/error.ogg")}
all_fancy_text = {"Nodes" : render_outlined_text("Nodes", (255,255,255), font_edit_menu, 2), "Edges" : render_outlined_text("Edges", (255,255,255), font_edit_menu, 2)}


screen.fill((255, 220, 220))
graph = Graph()

test_node_1 = Node([100, 50], 0)
graph.add_node(test_node_1)
test_node_2 = Node([80, 500], 1)
graph.add_node(test_node_2)
test_node_3 = Node([800, 500], 2)
graph.add_node(test_node_3)
nId = 3

test_edge_1 = Edge(test_node_1, test_node_2, "3x+2",0)
graph.add_edge(test_edge_1)
test_edge_2 = Edge(test_node_3, test_node_2, "3x**2+2",1)
graph.add_edge(test_edge_2)
eId = 2

#graph.remove_node(test_node_3) making money

running = True
while running:
    dt = clock.tick(60)/1000
    mx, my = pygame.mouse.get_pos()

    if status["pickup"][0]:
        status["pickup"][1].position = (mx, my)
    

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN and status["typing"][0]:
            if event.key == pygame.K_RETURN:
                typing_result = typed
                status["typing"][0] = False
            elif event.key == pygame.K_BACKSPACE:
                typed = typed[:-1]
            else:
                typed += event.unicode
                
        if event.type == pygame.MOUSEBUTTONDOWN and not status["typing"][0]:
            if event.button == 1:
                trio_check = status["delete_node"][0] or status["delete_edge"][0] or status["add_edge"][0]

                if status["delete_node"][0]:
                    del_node, bool_ = mouse_press_status_toggle_check(status, "delete_node", (mx,my), graph)
                    if bool_:
                        if del_node.nId == status["delete_node"][1]:
                            graph.remove_node( graph.nodes[del_node.nId])
                            status["delete_node"][1] = None
                        else:
                            status["delete_node"][1] = del_node.nId

                if status["add_edge"][0] or status["delete_edge"][0]:
                    active = "add_edge" if status["add_edge"][0] else "delete_edge"
                    
                    selected_node, bool_ = mouse_press_status_toggle_check(status, active, (mx,my), graph)
                    if bool_:
                        if status[active][1] == None:
                            status[active][1] = selected_node

                        elif status[active][1] == selected_node:
                            status[active][1] = None

                        else:
                            edge_exist_check, edge = check_edge_existence(graph, status[active][1], selected_node)
                            if edge_exist_check and active == "delete_edge":
                                graph.remove_edge(edge)
                            elif not edge_exist_check and active == "add_edge":
                                status["typing"] = [True, "add_edge"]
                            else:
                                default_sounds["error.ogg"].play()

                if not trio_check:
                    mouse_press_status_toggle_check(status, "pickup", (mx,my), graph)
                if not status["pickup"][0]:
                    if 1150<=mx<=1182+bar_offset["edit_tab"] and 560<=my<=592: #button top left corner 1150, 560
                        status["edit_tab"] = not status["edit_tab"]
                        if not bar_offset["edit_tab"]:
                            bar_offset["edit_tab"] = 18
                        else:
                            bar_offset["edit_tab"] = 0

                    elif 1000<=mx<=1032 and 585<=my<=617 and status["edit_tab"]: # 1000:1032x, 585:617y
                        graph.add_node(Node((600, 325), nId))
                        nId += 1

                    elif 960<=mx<=992 and 585<=my<=617 and status["edit_tab"] and (status["delete_node"][0] or not trio_check): # 960:992x,     585:617y
                        status["delete_node"][0] = not status["delete_node"][0]
                        status["delete_node"][1] = None

                    #toilet break followed by instant meal breek

                    elif 850<=mx<=882 and 585<=my<=617 and status["edit_tab"] and (status["add_edge"][0] or not trio_check): # 850:882,   585:617y
                        status["add_edge"][0] = not status["add_edge"][0]
                        status["add_edge"][1] = None

                    elif 810<=mx<=842 and 585<=my<=617 and status["edit_tab"] and (status["delete_edge"][0] or not trio_check):# 810:842,     585:617y
                        status["delete_edge"][0] = not status["delete_edge"][0]
                        status["delete_edge"][1] = None

                    

            if event.button == 3:
                if not trio_check:
                    mouse_press_status_toggle_check(status, "setting", (mx,my), graph)
                else:
                    status["delete_node"][1] = None
                    status["add_edge"][1] = None
                    status["delete_edge"][1] = None


        if event.type == pygame.QUIT:
            running = False

    if status["typing"][0] == False and status["typing"][1] != None:
        if status["typing"][1] == "add_edge":
            graph.add_edge(Edge(status["add_edge"][1], selected_node, typing_result, eId))
            eId += 1
            status["typing"][1] = None
            typed = ""

            status["add_edge"] = [False, None]
    
    screen.fill((255, 220, 220))
    graph.draw(screen, camera_position, node_size, edge_thickness)

    if status["typing"][0]:
        time = pygame.time.get_ticks()
        show_underscore = (time//500)%2
        draw_text_box(screen, show_underscore, typed, font_edit_menu)

    if status["add_edge"][0]:
        add_mode1 = font_edit_menu.render("Adding an", True, (40,40,40))
        add_mode2 = font_edit_menu.render("Edge", True, (40,40,40))
        screen.blit(add_mode1, (1000, 20))
        screen.blit(add_mode2, (1000, 45))
        if not status["add_edge"][1] == None:
            node_pos = status["add_edge"][1].position
            draw_disc(screen, (0, 255, 0, 180), int(node_size), node_pos)

    if status["delete_edge"][0]:
        if not status["delete_edge"][1] == None:
            node_pos = status["delete_edge"][1].position
            draw_disc(screen, (255, 128, 0, 180), int(node_size), node_pos)

    if status["delete_node"][0] or status["delete_edge"][0]:
        del_mode = font_edit_menu.render("Deletion Mode", True, (40,40,40))
        screen.blit(del_mode, (1000, 20))
        if status["delete_node"][0]:
            del_mode2 = font_edit_menu.render("[Node]", True, (40,40,40))
        else:
            del_mode2 = font_edit_menu.render("[Edge]", True, (40,40,40))
        screen.blit(del_mode2, (1000, 45))
    
    if not status["delete_node"][1] == None:
        node_pos = graph.nodes[status["delete_node"][1]].position
        draw_disc(screen, (255, 0, 0, 180), int(node_size), node_pos)
        text = font_sidebar.render("Confirm ?", True, (40,40,40))
        screen.blit(text, (node_pos[0]-node_size, node_pos[1]-node_size-20))

    if status["setting"][0]:
        status["setting"][1].draw_setting(screen)

    if not status["edit_tab"]:
        pos_edit = [1175, 560]
        if 1125<=mx and 560<=my<=592:
            pos_edit[0] -= 50 
        draw_sidebar(0, font_sidebar, pos_edit, screen) 
    else:
        draw_edit_tab(screen, all_fancy_text, default_images)
        
    
    pygame.display
    pygame.display.flip()
pygame.quit()
sys.exit()