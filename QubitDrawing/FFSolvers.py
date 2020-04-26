# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 16:26:49 2020

@author: Quantico
"""

import gdspy as gds
import os
from PIL import Image
import numpy as np
import tripy
# import QubitDrawingFunctions as qbdraw

"""This module contains functions to simulate gds polygons in FastFieldSolvers apps and get inducatnce and capacirtance matrices using
FastHenry and FasterCap, respectively.
The 2D FasterCap function should not be used for chip geometry."""

def FastHenry(Name,
              Polygons=[], #List with polygons
              units='um',
              LineWidth = 2,
              LineHeight = 0.1,
              WidthDiscretization= 7,
              HeightDiscretization = 7):      
    """
    This function recieves a list of 2D polygons (arrays-like[N][2]) and creates
    a text file that can be used to calculate an inductance matrix between
    objects using FastHenry.
    """
    
    '''Create and open file'''
    #If file exists, try next number.
    c=0
    while c<100:
        FileName = Name+str(c)
        try:
            with open(FileName+".txt") as file:
                print("File "+FileName+" already exists, trying next number.")
                c+=1
        except IOError:
            c=100
    file = open(FileName+".txt", "a")
    
    '''Header: setting simulation chracteristics'''
    file.write('**New Element - '+FileName+':\n\n')
    file.write('* Default units \n \
            .units ' +units+'\n')
    file.write('* Default height, width and discretization\n \
            .default nwinc='+str(WidthDiscretization)
            +' nhinc='+str(HeightDiscretization)+' h='+str(LineHeight)
            +' w='+str(LineWidth)+'\n')       
    file.write('* Default units \n \
            .units ' +units+'\n')
    file.write('* Default height, width and discretization\n \
            .default nwinc='+str(WidthDiscretization)
            +' nhinc='+str(HeightDiscretization)+' h='+str(LineHeight)
            +' w='+str(LineWidth)+'\n')
    file.write('\n')
    
    '''Writing the cell's polygons in terms of nodes and elongations'''   
    
    for P,Polygon in enumerate(Polygons):
        '''Polygon Nodes''' 
        file.write('*Polygon'+str(P)+' Nodes:\n')
        for i in range (len(Polygon)):
            file.write('nQB_'+str(P)+'_'+str(i)+ ' '+str(Polygon[i][0])+' '+ str(Polygon[i][1])+'\n')
        file.write('nQB'+str(i+1)+ ' '+str(Polygon[0][0])+' '+ str(Polygon[0][1])+'\n') #Repeat the first point of the polygon
            
        '''Polygon Elongations'''
        file.write('*Polygon'+str(P)+' Elongations:\n')
        for i in range (len(Polygon)):
              file.write('eQB_'+str(P)+'_'+str(i)+ ' nQB'+str(i) +' nQB'+str(i+1)+'\n')
        file.write('\n')
    
    '''Ender'''
    file.write('\n.End \n \n')
    file.close()
    return

"""
FastHenry execution using this code.
The software 'GhostScript' should be downloaded and added to the system PATH in order to convert the schema from .ps to .png
"""
# #Create a text (.inp) file with the circuit elements
# CircuitName = 'two' #The text file name
# LineWidth = 2               #The dafaule width of the elements' wires
# units = 'um'                #Length units. Usually microns-'um'

# path = gds.RobustPath((1, -1), 0.2)
# path.segment((1, 1))
# print(path)
# # FastHenry(CircuitName, LineWidth=LineWidth, units=units)

# FastHenryPath = 'C:/Users/User/DownloadPrograms/FastHenry/bin/' #Path to folder in which fasthenry.exe and zbuf.exe are.
# CircuitPath = 'C:/Users/User/DownloadPrograms/FastHenry/two/'

# #Run inp file in the command line to get an inductance matrix named Zc.mat?
# while True:
#     answer=input('Get the inductance matrix using FastHenry? [y/n]')
#     if answer=='y':
#         os.system('powershell.exe -command cd '+CircuitPath+' ; ./'+CircuitName+'.inp') #Might need to add the fasthenry.exe path string for the more general case
#         print('Calculated inductance matrix can be found in file '+CircuitName+'.mat')       
#         # os.rename(CircuitPath+'Zc.mat', CircuitPath+CircuitName+'.mat')
#         break
#     elif answer=='n':
#         break
#     else:
#         print('Please only type y or n')
        
# #Run FastHenry visualization to get the circuit's image in .png format?
# while True:
#     answer=input("Get the circuit's schema using FastHenry? [y/n]")
#     if answer=='y':
#         os.system('powershell.exe -command cd '+FastHenryPath+' ; ./fasthenry.exe ./'+CircuitPath+CircuitName+'.inp -f simple') #Might need to add the fasthenry.exe path string for the more general case
#         os.system('powershell.exe -command cd '+FastHenryPath+' ; ./zbuf.exe ./zbuffile') #Might need to add the fasthenry.exe path string for the more general case    
#         with Image.open(CircuitPath+'zbuffile.ps') as im:
#             im.save(CircuitPath+CircuitName+'.png')
#         os.remove(CircuitPath+'zbuffile.ps')
#         os.remove(CircuitPath+'zbuffile')
#         os.remove(CircuitPath+'zbuffile_shadings')
#         print("Circuit's schema can be found in file "+CircuitName+'.png')
#         break
#     elif answer=='n':
#         break
#     else:
#         print('Please only type y or n')
        
# #Open the folder?
# while True:
#     answer=input("Open the folder containing the files? [y/n]")
#     if answer=='y':
#         os.system('start '+CircuitPath)
#         break
#     elif answer=='n':
#         break
#     else:
#         print('Please only type y or n')

def FasterCap(Name,
              Polygons=[], #List with polygons
              PolygonsNames=[]):      
    """
    This function recieves a list of 2D polygons (arrays-like[N][2]) and creates
    a text file that can be used to calculate an capacitance matrix between
    objects using FasterCap in its 3D mode.
    """
    
    '''Create and open file'''
    #If file exists, try next number.
    c=0
    while c<100:
        FileName = Name+'_FasterCap_'+str(c)
        try:
            with open(FileName+".txt") as file:
                print("File "+FileName+" already exists, trying next number.")
                file.close()
                c+=1
        except IOError:
            c=100
    file = open(FileName+".txt", "a")
    
    '''Header: setting simulation chracteristics'''
    file.write('*0 '+FileName+'\n')
    file.write('*Fast(er)Cap input file to calculate capacitance of polygon \n')
    file.write('\n')
            
    '''Writing the cell's polygons in terms of triangles'''   
    if PolygonsNames ==[]:
        for P in range(len(Polygons)):
            PolygonsNames.append('Polygon'+str(P+1))            
    for P,Polygon in enumerate(Polygons):
        file.write('\n*G '+str(PolygonsNames[P])+'\t|3D coordinates of the three vertices of the triangle T patch\n\n')
        triangles = tripy.earclip(Polygon)
        for triangle in triangles:
            file.write('T '+str(PolygonsNames[P])+'\t')
            for vertex in range(3):
                file.write(str(format(triangle[vertex][0],'.4f'))+'\t'+str(round(triangle[vertex][1],4))+'\t10.0\t') #10.0 is the default z coordinate
            file.write('\n')
            
    return

def FasterCap2D(Name,
              Polygons=[],      #List with polygons
              PolygonsNames=[], #If not defined the polygons will be numbered
              epsilon_e=[]):    #Relative (effective) permittivity outside the conductors      
    """
    This function recieves a list of 2D polygons (arrays-like[N][2]) and creates
    a text file that can be used to calculate an capacitance matrix between
    objects using FasterCap using its 2D mode.
    The file consists the geometry files in the end and their references (and dielectric definitions) in the beginning.
    """
    
    '''Create and open file'''
    #If file exists, try next number.
    c=0
    while c<100:
        FileName = Name+'_FasterCap_'+str(c)
        try:
            with open(FileName+".txt") as file:
                print("File "+FileName+" already exists, trying next number.")
                file.close()
                c+=1
        except IOError:
            c=100
    file = open(FileName+".txt", "a")
    
    ''''Numbering the polygons if no names were given'''
    if PolygonsNames ==[]:
        for P in range(len(Polygons)):
            PolygonsNames.append('Polygon'+str(P+1)) 
    
    ''''Assuming air (relative permittivity =1) unless specifically givenvalues'''
    if epsilon_e ==[]:
        for P in range(len(Polygons)):
            epsilon_e.append(1.0) 
            
    '''Header and references to the geometry files'''
    file.write('* 2D '+FileName+'\n')
    file.write('* Fast(er)Cap 2D input file to calculate capacitance between polygons \n')
    file.write('\n')
    for P,Polygon in enumerate(Polygons):
        file.write('C '+str(PolygonsNames[P])+'\t'+str(epsilon_e[P])+'\t0.0\t0.0\n')
    
    file.write('\nEnd\n\n***Start of the geometry files')
    
    '''Writing the cell's polygons in terms of segments in separate files'''              
    for P,Polygon in enumerate(Polygons):
        file.write('\nFile '+str(PolygonsNames[P])+'\n')
        file.write('\n*G '+str(PolygonsNames[P])+'\t|2D coordinates of the two points of the S segment\n\n')
        for point_index in range(len(Polygon)-1):
            file.write('S '+str(PolygonsNames[P])+'\t')
            file.write(str(format(Polygon[point_index][0],'.4f'))+'\t'+str(format(Polygon[point_index][1],'.4f'))+'\t')
            file.write(str(format(Polygon[point_index+1][0],'.4f'))+'\t'+str(format(Polygon[point_index+1][1],'.4f')))
            file.write('\n')
        #Add last segment between last and first points
        file.write('S '+str(PolygonsNames[P])+'\t')
        file.write(str(format(Polygon[-1][0],'.4f'))+'\t'+str(format(Polygon[-1][1],'.4f'))+'\t')
        file.write(str(format(Polygon[0][0],'.4f'))+'\t'+str(format(Polygon[0][1],'.4f'))+'\n')
        file.write('End\n')
    return

# FasterCap(Name = 'TRY', Polygons=[[[0.0,1.0],[1.0,1.0],[1.0,0.0],[0.0,0.0]]])