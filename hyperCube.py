import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np

import math

def linear_transformation(matrix, vector):
    product = np.zeros(len(matrix))
    for i in range(len(matrix)):
        product += vector[i]*matrix[i]

    return product

def matrix_multiplication(m1, m2): # for square matrices only
    l = len(m1)
    product = np.zeros((l,l))
    for i in range(l):
        product[i] = linear_transformation(m1, m2[i])

    return product

def g_3d_r_m(a, b, c): # generate 3d rotation matrix
    a = math.radians(a)
    b = math.radians(b)
    c = math.radians(c)

    rZ = np.array([[math.cos(a), math.sin(a), 0], [-math.sin(a), math.cos(a), 0], [0,0,1]])
    rY = np.array([[math.cos(b), 0, math.sin(b)], [0,1,0], [-math.sin(b), 0, math.cos(b)]])
    rX = np.array([[1,0,0], [0, math.cos(c), math.sin(c)], [0, -math.sin(c), math.cos(c)]])

    r = matrix_multiplication(rZ, matrix_multiplication(rY, rX))

    return r

def g_4d_r_m(a1,b1,c1,a2,b2,c2,a3,b3,c3,a4,b4,c4): # generate 4d rotation matrix

    r = np.zeros((4,3,3)) # normal rotations
    r[0] = g_3d_r_m(a1,b1,c1)
    r[1] = g_3d_r_m(a2,b2,c2)
    r[2] = g_3d_r_m(a3,b3,c3)
    r[3] = g_3d_r_m(a4,b4,c4)

    hr = np.zeros((4,4,4)) # hyper rotation in 4D
    for i in range(4):
        ex = 3-i # exclude
        xc = 0
        yc = 0 # x, y counter for the current 3d matrix
        for x in range(4):
            yc = 0
            for y in range(4):
                if (x != ex and y != ex):
                    hr[i,x,y] = r[i,xc,yc]

                if (x == ex or y == ex): # the unchanged row and coulumn
                    hr[i,x,y] = 0
                    if (x== ex and y == ex):
                        hr[i,x,y] = 1

                if(y != ex):
                    yc += 1

            if(x != ex):
                xc += 1

    return matrix_multiplication(matrix_multiplication(matrix_multiplication(hr[3],hr[2]),hr[1]),hr[0])

def SG_projection(sx, sy, sz, sk, px, py, pz, pk):
    x = sx - ((sk*(sx-px))/(sk-pk))
    y = sy - ((sk*(sy-py))/(sk-pk))
    z = sz - ((sk*(sz-pz))/(sk-pk))

    return (x,y,z)

def shape(edges, vertices):
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()

def main():
    i4_Original = np.array([[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]])

    i4 = np.array(i4_Original)

    
    pygame.init()

    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL)
    pygame.display.set_caption('Hyper Cube')
    
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

    glTranslatef(0.0, 0.0, -7.0) # starting position

    glRotatef(-70,1,0,0) # starting orientation

    z_rotate = 0
    y_rotate = 0

    k_rotate = 0

    while True:
        vertices4D = ( # representatin as basis vector combination
            i4[0]-i4[1]-i4[2]+i4[3], #0
            i4[0]+i4[1]-i4[2]+i4[3], #1
            -i4[0]+i4[1]-i4[2]+i4[3], #2
            -i4[0]-i4[1]-i4[2]+i4[3], #3
            i4[0]-i4[1]+i4[2]+i4[3], #4
            i4[0]+i4[1]+i4[2]+i4[3], #5
            -i4[0]-i4[1]+i4[2]+i4[3], #6
            -i4[0]+i4[1]+i4[2]+i4[3], #7
            i4[0]-i4[1]-i4[2]-i4[3], #8
            i4[0]+i4[1]-i4[2]-i4[3], #9
            -i4[0]+i4[1]-i4[2]-i4[3], #10
            -i4[0]-i4[1]-i4[2]-i4[3], #11
            i4[0]-i4[1]+i4[2]-i4[3], #12
            i4[0]+i4[1]+i4[2]-i4[3], #13
            -i4[0]-i4[1]+i4[2]-i4[3], #14
            -i4[0]+i4[1]+i4[2]-i4[3] #15
        )

        source = (0,0,0,3) # source of projection, can be changed
        vertices = []

        for vertex in vertices4D:
            vertices.append(SG_projection(vertex[0],vertex[1],vertex[2],vertex[3],source[0],source[1],source[2],source[3]))

        edges = ( # connecting the vertices in a very non efficient way
            (0,1),
            (0,3),
            (0,4),
            (2,1),
            (2,3),
            (2,7),
            (6,3),
            (6,4),
            (6,7),
            (5,1),
            (5,4),
            (5,7),
            (0,8),
            (8,9),
            (9,10),
            (10,11),
            (8,12),
            (10,15),
            (15,14),
            (12,14),
            (11,14),
            (11,8),
            (15,13),
            (13,12),
            (13,9),
            (1,9),
            (2,10),
            (3,11),
            (4,12),
            (5,13),
            (6,14),
            (7,15)
        )
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

            if event.type == pygame.KEYDOWN:# both of these are responsible for inputs, can be modified
                if event.key == pygame.K_LEFT:
                    z_rotate = 1
                if event.key == pygame.K_RIGHT:
                    z_rotate = -1
                if event.key == pygame.K_UP:
                    y_rotate = 1
                if event.key == pygame.K_DOWN:
                    y_rotate = -1
                if event.key == pygame.K_k:
                    k_rotate = 1
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    z_rotate = 0
                if event.key == pygame.K_RIGHT:
                    z_rotate = 0
                if event.key == pygame.K_UP:
                    y_rotate = 0
                if event.key == pygame.K_DOWN:
                    y_rotate = 0
                if event.key == pygame.K_k:
                    k_rotate = 0

        if z_rotate == 1: # those are responsible for what the inputs do, can be modified
            glRotatef(1,0,1,0)

        if z_rotate == -1:
            glRotatef(-1,0,1,0)

        if y_rotate == 1:
            glRotatef(1,1,0,0)

        if y_rotate == -1:
            glRotatef(-1,1,0,0)

        if k_rotate == 1:
            i4 = matrix_multiplication(g_4d_r_m(0,0,0,0,0,0,0,0,3,0,0,0),i4)

        i4 = matrix_multiplication(g_4d_r_m(0.3,0,0,0,0,0,0,0,1,0,0,0),i4) # auto rotation on 2 out of 12 axes
        
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        shape(edges, vertices)
        pygame.display.flip()
        pygame.time.wait(10)

main()



