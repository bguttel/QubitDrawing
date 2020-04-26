# -*- coding: utf-8 -*-
"""
Created on Wed Mar 25 18:26:30 2020

@author: User
"""
import gdspy as gds
import numpy as np
import QubitDrawingFunctions as qbdraw

"""This module is for non-used functions. If needed they should be added to the 'QubitDrawingFunction'
main module."""






"""The following function is a 4JJ Qubit with Enclosing Capacitor and not on the side. Seems more difficult to get
to and apply magnetic flux than the other design."""
def DrawFourJJqubit    (   FourJJqubitCellName = '4JJqubit',
                    FourJJloopLength = 10.5,
                    FourJJloopWidth = 0,
                    LineWidth = 2,                #width of the RFsquid line
                    JJparameters=     {'FingerWidth': 0.36,           #Dictionary with the Josephson junction parameters
                                        'FingerLength':  1.36,         #
                                        'TaperWidth': 0.5,             #
                                        'BridgeWidth': 0.14},
                    JJRelations =  [1,1,1,1],                          #Relations between Josephson junction sizes
                    CircuitLayer = 2,                                   #Layer for photolithography mask
                    eBeamLayer = 5):                                    #Layer for eBeam deposition     
    """
    This function returns a Four Josephson-junctions loop cell that contains references to the 4JJ (not necesserily identical) loop cell, a shunting capacitor cell and the connection to it.
    It separately returns the capacitor cell (two rectangles enclosing the loop) to be added to the resist mask.
    Three junction (usually the bigger ones) are on one branch of the loop, and the fourth is on the other.
    The cell origin is defined at the center of the loop.
    """
    
    '''Four JJ loop'''
    FourJJloop =  DrawFourJJloop(   FourJJloopCellName = FourJJqubitCellName,
                    FourJJloopLength = FourJJloopLength,
                    FourJJloopWidth = FourJJloopWidth,
                    LineWidth = LineWidth,                #width of the RFsquid line
                    JJparameters=JJparameters,         #Dictionary with the Josephson junction parameters
                    JJRelations =  JJRelations,                       #Relations between Josephson junction sizes
                    eBeamLayer = eBeamLayer)                                  #Layer for eBeam deposition
    
    '''Connection lines and pads'''
    FourJJconnectionLine = gds.Cell(FourJJqubitCellName+'ConnectionLine', exclude_from_current=True)
    ConnectionCurve = gds.Curve(1.5*LineWidth, 0).L(
        LineWidth, 0.5*LineWidth, LineWidth, 18*LineWidth, 1.5*LineWidth, 18.5*LineWidth, -1.5*LineWidth, 18.5*LineWidth,
        -LineWidth, 18*LineWidth, -LineWidth, 0.5*LineWidth, -1.5*LineWidth, 0)
    FourJJconnectionLine.add(gds.Polygon(ConnectionCurve.get_points(),layer=eBeamLayer))
    FourJJconnectionLine.add(gds.Rectangle((-6.5*LineWidth,18.5*LineWidth), (6.5*LineWidth,25*LineWidth) ,layer=eBeamLayer))
    
    '''Shunting capcitor and qubit background'''
    RectangleLength = 100
    RectangleWidth = 100
    Spacing = 20            #Spacing between rectangles and grounding plane, also half the spacing between rectangles

    FourJJCapacitor = gds.Cell(FourJJqubitCellName+'Capacitor', exclude_from_current=True)
    Rectangle1 = gds.Rectangle((-RectangleWidth/2,Spacing),(RectangleWidth/2,Spacing+RectangleLength)).fillet(Spacing/2)
    Rectangle2 = gds.Rectangle((-RectangleWidth/2,-Spacing-RectangleLength),(RectangleWidth/2,-Spacing)).fillet(Spacing/2)
    Circle = gds.Round((0,0), 2*Spacing)
    Background = gds.Rectangle((-RectangleWidth/2-Spacing,-2*Spacing-RectangleLength),(Spacing+RectangleWidth/2,2*Spacing+RectangleLength)).fillet(Spacing/2)
    FourJJCapacitor.add(gds.boolean([Background,Circle], [Rectangle1,Rectangle2], 'not', layer=CircuitLayer))
    
  
    FourJJloop.add(gds.CellReference(FourJJconnectionLine, origin=(0,FourJJloopLength/2+LineWidth/2)))
    FourJJloop.add(gds.CellReference(FourJJconnectionLine, origin=(0,-FourJJloopLength/2-LineWidth/2), rotation=180))
    FourJJloop.add(gds.CellReference(FourJJCapacitor, origin=(0,0)))
    
    return [FourJJloop,FourJJCapacitor]

def DrawRFsquid(   RFsquidCellName = 'RFsquid',
                    RFsquidLength = 155.5,
                    RFsquidWidth = 12,
                    LineWidth = 2,                #width of the RFsquid line
                    JJparameters=     {'FingerWidth': 0.36,           #Dictionary with the Josephson junction parameters
                                        'FingerLength':  1.36,         #
                                        'TaperWidth': 0.5,             #
                                        'BridgeWidth': 0.14},
                    layer = 2):
    """
    This function returns an RFsquid cell (in a list) that contains references to a line cell and
    a Josephson junction cell.
    The cell origin is defined at the center of the RFsquid loop.
    """
    
    '''Josephson Junctions'''
    RFsquidJJ = DrawJosephsonJunction(JosephsonJunctionCellName = RFsquidCellName+'JosephsonJunction',
                                      LineWidth = LineWidth,                #width of line connected to the junction
                                      FingerWidth = JJparameters['FingerWidth'],           #
                                      FingerLength = JJparameters['FingerLength'],          #
                                      TaperWidth = JJparameters['TaperWidth'],             #
                                      BridgeWidth = JJparameters['BridgeWidth'],           #
                                      layer = layer)
    
    '''line'''
    JosephsonJunctionTotalLength = JJparameters['FingerLength']+JJparameters['TaperWidth']+JJparameters['BridgeWidth']
    RFsquidLine = gds.Cell(RFsquidCellName+'Line', exclude_from_current=True)
    RFsquidLineCoordinates= [(0,(-RFsquidWidth+LineWidth)/2) , ((RFsquidLength-LineWidth)/2, (-RFsquidWidth+LineWidth)/2),
                                  ((RFsquidLength-LineWidth)/2,(RFsquidWidth-LineWidth)/2) , ((-RFsquidLength+LineWidth)/2,(RFsquidWidth-LineWidth)/2),
                                  ((-RFsquidLength+LineWidth)/2,(-RFsquidWidth+LineWidth)/2) , (-JosephsonJunctionTotalLength,(-RFsquidWidth+LineWidth)/2)]
    RFsquidLine.add(gds.FlexPath(RFsquidLineCoordinates, LineWidth, corners="circular bend", bend_radius=LineWidth , layer=layer))
    
    #Adds cell references to main cell
    RFsquid = gds.Cell(RFsquidCellName, exclude_from_current=True)
    RFsquid.add(gds.CellReference(RFsquidLine, origin=(0,0)))
    RFsquid.add(gds.CellReference(RFsquidJJ, origin=(-JosephsonJunctionTotalLength,(-RFsquidWidth+LineWidth)/2)))
        
    return [RFsquid]