# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 14:55:47 2020

@author: Quantico
"""

import gdspy as gds
import numpy as np

def saveCell2GDS(cell, gdsName):
    """ This function save the given cell to GDS file with the name 'gdsName' """
    layout = gds.GdsLibrary()
    layout.add(cell, overwrite_duplicate=True)
    layout.write_gds(gdsName+'.gds')

def createMarks(nx = 2,
                ny = 2,
                dx = 3000,
                dy = 3000,
                ):
    """
    Create marks on the chip
    """
    # Mark for EB
    crmk = gds.Cell('cross', exclude_from_current=True)
    crmk.add(gds.Rectangle((-100,-10),(-10, 10),layer=2))
    crmk.add(gds.Rectangle((-120, -30),(10, 30),layer=3))
    crmk.add(gds.Rectangle((100,-10),(10,10),layer=2))
    crmk.add(gds.Rectangle((120,-30),(-10,30),layer=3))
    crmk.add(gds.Rectangle((-10,-100),(10,-10),layer=2))
    crmk.add(gds.Rectangle((-30,-120),(30, 10),layer=3))
    crmk.add(gds.Rectangle((-10,100),(10,10),layer=2))
    crmk.add(gds.Rectangle((-30,120),(30,-10),layer=3))
    crmk.add(gds.Rectangle((-4,0),(0,1),layer=2))
    crmk.add(gds.Rectangle((-1,1),(0,4),layer=2))
    crmk.add(gds.Rectangle((4,0),(0,-1),layer=2))
    crmk.add(gds.Rectangle((1,-1),(0,-4),layer=2))
    
    # Make array
    mkar = gds.CellArray(crmk, nx, ny, (dx,dy), origin=(-(nx-1)*dx/2, -(ny-1)*dy/2))
    
    return crmk, mkar

def DrawResonator(    ResonatorCellName = 'Resonator',
                      LineWidth = 6,                #width of each parallel resonator line           
                      SpaceWidth = 10,              #space between parallel lines
                      elongation = 110,             #meander horizontal segment length
                      radius = 40,                  #radius of turns
                      num_meanders = 1,             #number of meanders in the resonator
                      layer = 2):                   #Layer 2 is usually the circuit layer
    """
    This function returns a resonator cell that contains cell references to a main-line coupler,
    meander(s) and a qubit coupler.
    The cell origin is defined at the connection with the feedline.
    """

    '''feedline coupler'''
    coupler = gds.Cell(ResonatorCellName+'Coupler', exclude_from_current=True)
    ##Uncomment for galvanic coupling
    # coupler_path = gds.FlexPath([(0,0),(0,-10)], [LineWidth, LineWidth], LineWidth + SpaceWidth , layer=layer)
    # coupler_connection = gds.Rectangle((-SpaceWidth/2,0),(SpaceWidth/2,-LineWidth), layer = 1) #connection fo feed line- avoid evaporation.
    # coupler.add(coupler_connection)
    # coupler_path.turn(radius, 'l')
    # coupler_path.segment((140,0), relative = True)
    # coupler_end_point = (140+2*radius, -50-radius-60)
    coupler_path = gds.FlexPath([(0,-2*LineWidth-SpaceWidth),(140,-2*LineWidth-SpaceWidth)], [LineWidth, LineWidth], LineWidth + SpaceWidth , layer=layer)
    coupler_path.turn(radius, 'r')
    coupler_path.segment((0,-60), relative = True)
    coupler_end_point = (140+radius, -2*LineWidth-SpaceWidth-radius-60) #Comment for galvanic coupling
    coupler.add(coupler_path)

    
    '''meanders'''
    meander = gds.Cell(ResonatorCellName+'Meander', exclude_from_current=True)
    meander_path = gds.FlexPath([(0,0),(0,-0.1)], [LineWidth, LineWidth], LineWidth + SpaceWidth , layer=layer)
    for i in range (num_meanders):
        meander_path.turn(radius, 'r')
        meander_path.segment((-elongation,0), relative = True)
        meander_path.turn(radius, 'll')
        meander_path.segment((elongation,0), relative = True)
        meander_path.turn(radius, 'r')
        meander_path.segment((0,-0.5), relative = True)
    meander_end_point = tuple(map(sum, zip(coupler_end_point, (0, -0.1-num_meanders*(4*radius+0.5)))))
    meander.add(meander_path)
    
    '''qubit coupler'''
    qcoupler = gds.Cell(ResonatorCellName+'QubitCoupler', exclude_from_current=True)
    qcoupler_path=gds.FlexPath([(0,0),(0,-1)], [LineWidth, LineWidth], LineWidth + SpaceWidth , layer=layer)
    qcoupler_path.turn(radius, 'r')
    qcoupler_path.segment((-elongation/2,0), relative = True)
    qcoupler_path.turn(radius, 'l')
    TerminalWidth = 100 #Terminal part
    qcoupler_terminal = gds.FlexPath([(-2*radius-elongation/2-SpaceWidth/2,-2*radius),(-2*radius-elongation/2-SpaceWidth/2-TerminalWidth/2,-2*radius),
                                      (-2*radius-elongation/2-SpaceWidth/2-TerminalWidth/2,-2*radius-SpaceWidth-LineWidth), (-2*radius-elongation/2-SpaceWidth/2+TerminalWidth/2,-2*radius-SpaceWidth-LineWidth),
                                      (-2*radius-elongation/2-SpaceWidth/2+TerminalWidth/2,-2*radius), (-2*radius-elongation/2+SpaceWidth/2,-2*radius)], LineWidth, ends= 'flush', corners="circular bend", bend_radius=LineWidth, layer=layer)
    qcoupler.add(qcoupler_path)
    qcoupler.add(qcoupler_terminal)
    
    
    
    #Adds cells and cell references to pattern
    Resonator = gds.Cell(ResonatorCellName, exclude_from_current=True)
    pattern = [Resonator, coupler, meander, qcoupler]
    Resonator.add(gds.CellReference(coupler, origin=(0, 0)))
    Resonator.add(gds.CellReference(meander, origin=coupler_end_point))
    Resonator.add(gds.CellReference(qcoupler, origin=meander_end_point))
    
    return pattern

def DrawLauncher(   LauncherCellName = 'IndependentLauncher',
                    LineWidth = 6,
                    SpaceWidth = 10,              #space between parallel lines
                    BigWidth = 96,                #maximum launcher-lines width
                    LauncherWidth = 352,           #total launcher width
                    layer = 2):
    """
    This function returns a launcher cell.
    The cell origin is defined at the connection with the feedline.
    """
    Launcher = gds.Cell(LauncherCellName, exclude_from_current=True)
    LauncherCurve = gds.Curve(0,SpaceWidth/2).L(
        0, LineWidth+(SpaceWidth/2), -2*BigWidth, LauncherWidth/2, -5*BigWidth, LauncherWidth/2, -5*BigWidth, -LauncherWidth/2,
        -2*BigWidth, -LauncherWidth/2, 0, -LineWidth-(SpaceWidth/2), 0, -SpaceWidth/2, -2*BigWidth, -(LauncherWidth/2) + BigWidth,
        -2*BigWidth, -(LauncherWidth/2) + BigWidth, -4*BigWidth, -(LauncherWidth/2) + BigWidth, -4*BigWidth, (LauncherWidth/2) - BigWidth,
        -2*BigWidth, (LauncherWidth/2) - BigWidth)
                                                 
    Launcher.add(gds.Polygon(LauncherCurve.get_points(),layer=layer))
    return Launcher

def DrawTransmissionFeedline(   FeedlineCellName = 'Feedline',
                    MainlineLength = 2000,
                    LineWidth = 6,                #width of each parallel line
                    SpaceWidth = 10,              #space between parallel lines
                    BigWidth = 96,                #maximum launcher-lines width
                    LauncherWidth = 352,          #total launcher width
                    layer = 2):
    """
    This function returns a symmetrical feedline cell that contains references to one mainline (two parallel lines) cell 
    and one launcher cell, placed on both sides of the main line.
    The cell origin is defined at the center of the mainline.
    """
    
    '''launcher'''
    launcher = DrawLauncher(   LauncherCellName = 'Launcher',
                    LineWidth = 6,                  #width of each parallel line
                    SpaceWidth = 10,              #space between parallel lines
                    BigWidth = 96,                #maximum launcher-lines width
                    LauncherWidth = 352,           #total launcher width
                    layer = 2)
    
    '''main line'''
    mainline = gds.Cell(FeedlineCellName+'Mainline', exclude_from_current=True)
    mainline.add(gds.FlexPath([(0,0),(MainlineLength,0)], [LineWidth, LineWidth], LineWidth + SpaceWidth , layer=layer))
    
    #Adds cells and cell references to pattern
    Feedline = gds.Cell(FeedlineCellName, exclude_from_current=True)
    pattern = [Feedline, launcher, mainline]
    Feedline.add(gds.CellReference(launcher, origin=(-MainlineLength/2, 0)))
    Feedline.add(gds.CellReference(mainline, origin=(-MainlineLength/2,0)))
    Feedline.add(gds.CellReference(launcher, origin=(MainlineLength/2, 0), rotation=180 , x_reflection=True))

    return pattern

def DrawReflectionFeedline(   FeedlineCellName = 'Feedline',
                    MainlineLength = 3000,
                    LineWidth = 6,                #width of each parallel line
                    SpaceWidth = 10,              #space between parallel lines
                    BigWidth = 96,                #maximum launcher-lines width
                    LauncherWidth = 352,          #total launcher width
                    layer = 2):
    """
    This function returns a symmetrical feedline cell that contains references to one mainline (two parallel lines) cell 
    and one launcher cell, placed on both sides of the main line.
    The cell origin is defined at the center of the mainline.
    """
    '''launcher'''
    launcher = DrawLauncher(   LauncherCellName = 'Launcher',
                    LineWidth = 6,                  #width of each parallel line
                    SpaceWidth = 10,              #space between parallel lines
                    BigWidth = 96,                #maximum launcher-lines width
                    LauncherWidth = 352,            #total launcher width     
                    layer = 2)
    
    '''main line'''
    mainline = gds.Cell(FeedlineCellName+'Mainline', exclude_from_current=True)
    path = gds.FlexPath([(0,0),(MainlineLength,0)], [LineWidth, LineWidth], LineWidth + SpaceWidth , layer=layer)
    path.turn(LauncherWidth, 'r')
    path.segment((0,-MainlineLength/4), relative=True)
    mainline.add(path)
    
    #Adds cells and cell references to pattern
    Feedline = gds.Cell(FeedlineCellName, exclude_from_current=True)
    pattern = [Feedline, launcher, mainline]
    Feedline.add(gds.CellReference(launcher, origin=(-MainlineLength/2, 0)))
    Feedline.add(gds.CellReference(mainline, origin=(-MainlineLength/2,0)))

    return pattern

def DrawJosephsonJunction(    JosephsonJunctionCellName = 'IndependentJosephsonJunction',
                              LineWidth = 2,                #width of line connected to the junction
                              FingerWidth = 0.36,           #
                              FingerLength = 1.36,          #
                              TaperWidth = 0.5,             #
                              BridgeWidth = 0.14,           #
                              layer = 1,
                              ignore_layer = 1):
    """
    This function returns a Josephson junction cell.
    The cell origin is defined at the connection with the line.
            |\__
            | __|
            |/
    """
    JosephsonJunction = gds.Cell(JosephsonJunctionCellName, exclude_from_current=True)
    JosephsonJunctionCurve = gds.Curve(0, LineWidth/2).L(
    TaperWidth, FingerWidth/2, TaperWidth+FingerLength, FingerWidth/2, TaperWidth+FingerLength, -FingerWidth/2,
    TaperWidth, -FingerWidth/2, 0, -LineWidth/2)
                                                 
    JosephsonJunction.add(gds.Polygon(JosephsonJunctionCurve.get_points(),layer=layer))
    JosephsonJunction.add(gds.Rectangle((TaperWidth+FingerLength,-FingerWidth/2),(TaperWidth+FingerLength+BridgeWidth,FingerWidth/2),layer=ignore_layer))
    return JosephsonJunction

def DrawRFsquid(   RFsquidCellName = 'RFsquid',
                    RFsquidLength = 155.5,
                    RFsquidWidth = 12,
                    LineWidth = 2,                #width of the RFsquid line
                    JJparameters=     {'FingerWidth': 0.36,           #Dictionary with the Josephson junction parameters
                                        'FingerLength':  1.36,         #
                                        'TaperWidth': 0.5,             #
                                        'BridgeWidth': 0.14,           #
                                        'ignore_layer': 1 },
                    layer = 2):
    """
    This function returns an RFsquid cell that contains references to a line cell and
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
                                      layer = layer,
                                      ignore_layer = JJparameters['ignore_layer'])
    
    '''line'''
    JosephsonJunctionTotalLength = JJparameters['FingerLength']+JJparameters['TaperWidth']+JJparameters['BridgeWidth']
    RFsquidLine = gds.Cell(RFsquidCellName+'Line', exclude_from_current=True)
    RFsquidLineCoordinates= [(0,(-RFsquidWidth+LineWidth)/2) , ((RFsquidLength-LineWidth)/2, (-RFsquidWidth+LineWidth)/2),
                                  ((RFsquidLength-LineWidth)/2,(RFsquidWidth-LineWidth)/2) , ((-RFsquidLength+LineWidth)/2,(RFsquidWidth-LineWidth)/2),
                                  ((-RFsquidLength+LineWidth)/2,(-RFsquidWidth+LineWidth)/2) , (-JosephsonJunctionTotalLength,(-RFsquidWidth+LineWidth)/2)]
    RFsquidLine.add(gds.FlexPath(RFsquidLineCoordinates, LineWidth, corners="circular bend", bend_radius=LineWidth , layer=layer))
    
    #Adds cells and cell references to pattern
    RFsquid = gds.Cell(RFsquidCellName, exclude_from_current=True)
    pattern = [RFsquid, RFsquidJJ, RFsquidLine]
    RFsquid.add(gds.CellReference(RFsquidLine, origin=(0,0)))
    RFsquid.add(gds.CellReference(RFsquidJJ, origin=(-JosephsonJunctionTotalLength,(-RFsquidWidth+LineWidth)/2)))
        
    return pattern

def DrawFourJJloop(   FourJJloopCellName = 'FourJJloop',
                    FourJJloopLength = 155.5,
                    FourJJloopWidth = 100,
                    LineWidth = 2,                #width of the RFsquid line
                    JJparameters=     {'FingerWidth': 0.36,           #Dictionary with the Josephson junction parameters
                                        'FingerLength':  1.36,         #
                                        'TaperWidth': 0.5,             #
                                        'BridgeWidth': 0.14,           #
                                        'ignore_layer': 1 },
                    JJRelations =  [1,1,1,1],                          #Relations between Josephson junction sizes
                    layer = 2):
    """
    This function returns a Four Josephson-junctions loop cell that contains references to a line cell, four
    (Not neccerilay identical) Josephson junction cells, one of which is capacitively shunted.
    Three junction (usually the bigger ones) are on one branch of the loop, and the fourth is shunted.
    The cell origin is defined at the center of the loop.
    """
    
    FourJJloop = gds.Cell(FourJJloopCellName, exclude_from_current=True)
    pattern = [FourJJloop]
    
    '''Josephson Junctions'''
    JosephsonJunctionOrigins = [(-FourJJloopWidth/2,FourJJloopLength/4),(-FourJJloopWidth/2,0),
                                (-FourJJloopWidth/2,-FourJJloopLength/4),(FourJJloopWidth/2,0)]
    JosephsonJunctionTotalLengths = []
    for i, JJrelation in enumerate(JJRelations): 
        JosephsonJunction = DrawJosephsonJunction(JosephsonJunctionCellName = FourJJloopCellName+'JosephsonJunction'+str(i+1),
                                          LineWidth = LineWidth,                #width of line connected to the junction
                                          FingerWidth = JJrelation*JJparameters['FingerWidth'],           #
                                          FingerLength = JJparameters['FingerLength'],          #
                                          TaperWidth = JJparameters['TaperWidth'],             #
                                          BridgeWidth = JJrelation*JJparameters['BridgeWidth'],           #
                                          layer = layer,
                                          ignore_layer = JJparameters['ignore_layer'])
        JosephsonJunctionTotalLengths.append(JJparameters['FingerLength']+JJparameters['TaperWidth']+JJrelation*JJparameters['BridgeWidth'])
        FourJJloop.add(gds.CellReference(JosephsonJunction, origin=JosephsonJunctionOrigins[i], rotation=-90))
        # pattern += JosephsonJunction
        
    '''Shunting Coapacitor'''
    RectanagleDimesions = [100,30]  #Dimensions of each capacitor's rectangle
    Spacing = 10                    #Spacing between rectangles
    DistanceFromLoop = 20
    ShuntingCapacitor = gds.Cell(FourJJloopCellName+'ShuntingCapacitor', exclude_from_current=True)
    ShuntingCapacitor.add(gds.Rectangle((-RectanagleDimesions[0]/2,-Spacing/2-RectanagleDimesions[1]),(RectanagleDimesions[0]/2,-Spacing/2), layer=layer))
    ShuntingCapacitor.add(gds.Rectangle((-RectanagleDimesions[0]/2,Spacing/2),(RectanagleDimesions[0]/2,RectanagleDimesions[1]+Spacing/2), layer=layer))
    ShuntingCapacitor.add(gds.FlexPath([(0,Spacing/2+RectanagleDimesions[1]),(0,Spacing/2+RectanagleDimesions[1]+4*LineWidth),(-RectanagleDimesions[0]/2-DistanceFromLoop,Spacing/2+RectanagleDimesions[1]+4*LineWidth)],
                                       LineWidth, corners="circular bend", bend_radius=LineWidth, layer=layer))
    ShuntingCapacitor.add(gds.FlexPath([(0,-Spacing/2-RectanagleDimesions[1]),(0,-Spacing/2-RectanagleDimesions[1]-4*LineWidth),(-RectanagleDimesions[0]/2-DistanceFromLoop,-Spacing/2-RectanagleDimesions[1]-4*LineWidth)],
                                       LineWidth, corners="circular bend", bend_radius=LineWidth, layer=layer))
    FourJJloop.add(gds.CellReference(ShuntingCapacitor, origin=(FourJJloopWidth/2+DistanceFromLoop+RectanagleDimesions[0]/2,0)))
    
    
    '''line (with JJ spacings)'''
    FourJJloopLine = gds.Cell(FourJJloopCellName+'Line', exclude_from_current=True)
    FourJJloopLine.add(gds.FlexPath([(-FourJJloopWidth/2,(FourJJloopLength/4)-JosephsonJunctionTotalLengths[0]), (-FourJJloopWidth/2,0)], LineWidth, layer=layer))
    FourJJloopLine.add(gds.FlexPath([(-FourJJloopWidth/2,-JosephsonJunctionTotalLengths[1]), (-FourJJloopWidth/2,-FourJJloopLength/4)], LineWidth, layer=layer))
    FourJJloopLine.add(gds.FlexPath([(-FourJJloopWidth/2,(-FourJJloopLength/4)-JosephsonJunctionTotalLengths[2]), (-FourJJloopWidth/2,-FourJJloopLength/2),
                                     (FourJJloopWidth/2,-FourJJloopLength/2), (FourJJloopWidth/2,-JosephsonJunctionTotalLengths[3])], LineWidth, corners="circular bend", bend_radius=LineWidth, layer=layer))
    FourJJloopLine.add(gds.FlexPath([(FourJJloopWidth/2,0),(FourJJloopWidth/2,FourJJloopLength/2),
                                      (-FourJJloopWidth/2,FourJJloopLength/2),(-FourJJloopWidth/2,FourJJloopLength/4)], LineWidth, corners="circular bend", bend_radius=LineWidth, layer=layer))
    FourJJloop.add(gds.CellReference(FourJJloopLine, origin=(0,0)))
    
    return pattern