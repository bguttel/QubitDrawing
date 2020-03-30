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

def CreateMarks(nx = 2,     #number of columns
                ny = 2,     #number of rows
                dx = 3000,  #horizontal distance
                dy = 3000,  #vertical distance
                PhotoLayer=2,
                eBeamLayer=5):
    """
    Create lithography marks on the chip.
    """
    # Mark for EB
    crmk = gds.Cell('cross', exclude_from_current=True)
    crmk.add(gds.Rectangle((-100,-10),(-10, 10),layer=eBeamLayer))
    crmk.add(gds.Rectangle((-120, -30),(10, 30),layer=PhotoLayer))
    crmk.add(gds.Rectangle((100,-10),(10,10),layer=eBeamLayer))
    crmk.add(gds.Rectangle((120,-30),(-10,30),layer=PhotoLayer))
    crmk.add(gds.Rectangle((-10,-100),(10,-10),layer=eBeamLayer))
    crmk.add(gds.Rectangle((-30,-120),(30, 10),layer=PhotoLayer))
    crmk.add(gds.Rectangle((-10,100),(10,10),layer=eBeamLayer))
    crmk.add(gds.Rectangle((-30,120),(30,-10),layer=PhotoLayer))
    crmk.add(gds.Rectangle((-4,0),(0,1),layer=eBeamLayer))
    crmk.add(gds.Rectangle((-1,1),(0,4),layer=eBeamLayer))
    crmk.add(gds.Rectangle((4,0),(0,-1),layer=eBeamLayer))
    crmk.add(gds.Rectangle((1,-1),(0,-4),layer=eBeamLayer))
    
    # Make array
    mkar = gds.CellArray(crmk, nx, ny, (dx,dy), origin=(-(nx-1)*dx/2, -(ny-1)*dy/2))
    
    return crmk, mkar

def DrawResonator(    ResonatorCellName = 'Resonator',
                      LineWidth = 6,                #spacing between resonator and grounding plane (resist)           
                      SpaceWidth = 10,              #resonator line width (resist spacing)
                      elongation = 150,             #meander horizontal segment length            
                      num_meanders = 1,             #number of meanders in the resonator
                      layer = 2):                   #Layer 2 is usually the circuit layer
    """
    This function returns a resonator cell that contains cell references to a main-line coupler,
    meander(s) and a qubit coupler.
    The cell origin is defined at the connection with the feedline.
    Notice the negative definitions line and space parameters.
    """
    
    radius = elongation/3                  #radius of turns
    '''feedline coupler'''
    coupler = gds.Cell(ResonatorCellName+'Coupler', exclude_from_current=True)
    ##Uncomment for galvanic coupling
    # coupler_path = gds.FlexPath([(0,0),(0,-10)], [LineWidth, LineWidth], LineWidth + SpaceWidth , layer=layer)
    # coupler_connection = gds.Rectangle((-SpaceWidth/2,0),(SpaceWidth/2,-LineWidth), layer = 1) #connection fo feed line- avoid evaporation.
    # coupler.add(coupler_connection)
    # coupler_path.turn(radius, 'l')
    # coupler_path.segment((140,0), relative = True)
    # coupler_end_point = (140+2*radius, -50-radius-60)
    coupler_path = gds.FlexPath([(0,-2*LineWidth-SpaceWidth),(elongation/2,-2*LineWidth-SpaceWidth)], [LineWidth, LineWidth], LineWidth + SpaceWidth , layer=layer)
    coupler_path.turn(radius, 'r')
    coupler_path.segment((0,-60), relative = True)
    coupler_end_point = (elongation/2+radius, -2*LineWidth-SpaceWidth-radius-60) #Comment for galvanic coupling
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
    meanders_end_point = tuple(map(sum, zip(coupler_end_point, (0, -0.1-num_meanders*(4*radius+0.5)))))
    meander.add(meander_path)
    
    '''qubit coupler'''
    qcoupler = gds.Cell(ResonatorCellName+'QubitCoupler', exclude_from_current=True)
    qcoupler_path=gds.FlexPath([(0,0),(0,-1)], [LineWidth, LineWidth], LineWidth + SpaceWidth , layer=layer)
    qcoupler_path.turn(radius, 'r')
    qcoupler_path.segment((-elongation/6,0), relative = True)
    qcoupler_path.turn(radius, 'l')
    TerminalWidth = 100 #Terminal part total width
    qcoupler_terminal = gds.FlexPath([(-2*radius-elongation/6-SpaceWidth/2,-2*radius),(-2*radius-elongation/6-SpaceWidth/2-TerminalWidth/2,-2*radius),
                                      (-2*radius-elongation/6-SpaceWidth/2-TerminalWidth/2,-2*radius-SpaceWidth-LineWidth), (-2*radius-elongation/6+SpaceWidth/2+TerminalWidth/2,-2*radius-SpaceWidth-LineWidth),
                                      (-2*radius-elongation/6+SpaceWidth/2+TerminalWidth/2,-2*radius), (-2*radius-elongation/6+SpaceWidth/2,-2*radius)], 
                                     LineWidth, ends= 'flush', corners="circular bend", bend_radius=0.6*LineWidth, layer=layer)
    qcoupler.add(qcoupler_path)
    qcoupler.add(qcoupler_terminal)
    
    
    
    #Adds cell references to main cell
    Resonator = gds.Cell(ResonatorCellName, exclude_from_current=True)
    Resonator.add(gds.CellReference(coupler, origin=(0, 0)))
    Resonator.add(gds.CellReference(meander, origin=coupler_end_point))
    Resonator.add(gds.CellReference(qcoupler, origin=meanders_end_point))
    
    return [Resonator]

def DrawLauncher(   LauncherCellName = 'IndependentLauncher',
                    LineWidth = 6,                 #space between line and ground plate 
                    SpaceWidth = 10,              #Deposited conducting line width
                    BigWidth = 96,                #maximum launcher-lines width
                    LauncherWidth = 352,           #total launcher width
                    layer = 2):
    """
    This function returns a launcher cell.
    The cell origin is defined at the connection with the feedline.
    Notice the negative definitions line and space parameters.
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
    Notice the negative definitions line and space parameters.
    """
    
    '''launcher'''
    launcher = DrawLauncher(   LauncherCellName = 'Launcher',
                    LineWidth = LineWidth,        #width of each parallel line
                    SpaceWidth = SpaceWidth,      #space between parallel lines
                    BigWidth = 96,                #maximum launcher-lines width
                    LauncherWidth = 352,          #total launcher width
                    layer = 2)
    
    '''main line'''
    mainline = gds.Cell(FeedlineCellName+'Mainline', exclude_from_current=True)
    mainline.add(gds.FlexPath([(0,0),(MainlineLength,0)], [LineWidth, LineWidth], LineWidth + SpaceWidth , layer=layer))
    
    #Adds cell references to main cell
    Feedline = gds.Cell(FeedlineCellName, exclude_from_current=True)
    Feedline.add(gds.CellReference(launcher, origin=(-MainlineLength/2, 0)))
    Feedline.add(gds.CellReference(mainline, origin=(-MainlineLength/2,0)))
    Feedline.add(gds.CellReference(launcher, origin=(MainlineLength/2, 0), rotation=180 , x_reflection=True))

    return [Feedline]

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
                    LineWidth = LineWidth,        #width of each parallel line
                    SpaceWidth = SpaceWidth,      #space between parallel lines
                    BigWidth = 96,                #maximum launcher-lines width
                    LauncherWidth = 352,          #total launcher width     
                    layer = 2)
    
    '''main line'''
    mainline = gds.Cell(FeedlineCellName+'Mainline', exclude_from_current=True)
    path = gds.FlexPath([(0,0),(MainlineLength,0)], [LineWidth, LineWidth], LineWidth + SpaceWidth , layer=layer)
    path.turn(LauncherWidth, 'r')
    path.segment((0,-MainlineLength/4), relative=True)
    mainline.add(path)
    
    #Adds cell references to main cell
    Feedline = gds.Cell(FeedlineCellName, exclude_from_current=True)
    Feedline.add(gds.CellReference(launcher, origin=(-MainlineLength/2, 0)))
    Feedline.add(gds.CellReference(mainline, origin=(-MainlineLength/2,0)))

    return [Feedline]

def DrawJosephsonJunction(    JosephsonJunctionCellName = 'IndependentJosephsonJunction',
                              LineWidth = 2,                #width of line connected to the junction (i.e. basis' length)
                              FingerWidth = 0.36,           #
                              FingerLength = 1,          #
                              TaperWidth = 0.5,             #Width of the basis
                              BridgeWidth = 0.14,           #Spacing left intentionally after the finger.
                              layer = 2):           
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
    return JosephsonJunction

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

def DrawFourJJloop(   FourJJloopCellName = '4JJloop',
                    FourJJloopLength = 10.5,
                    FourJJloopWidth = 0,                         #Square loop, unless width is specified
                    LineWidth = 2,                               #width of the loop wire
                    JJparameters=     {'FingerWidth': 0.36,      #Dictionary with the Josephson junction parameters
                                        'FingerLength':  1,   #
                                        'TaperWidth': 0.5,       #
                                        'BridgeWidth': 0.14},
                    JJRelations =  [1,1,1,1],                    #Relations between Josephson junction sizes
                    eBeamLayer = 5):                             #Layer for eBeam deposition
    """
    This function returns a Four Josephson-junctions loop cell.
    The cell origin is defined at the center of the loop.
    """
    if (FourJJloopWidth==0):
        FourJJloopWidth = FourJJloopLength #If width is not specifically defined make a square loop 
    FourJJloop = gds.Cell(FourJJloopCellName, exclude_from_current=True)
    
    '''Josephson Junctions'''
    JosephsonJunctionOrigins = [(-FourJJloopWidth/2,(4/10)*FourJJloopLength),(-FourJJloopWidth/2,FourJJloopLength/10),
                                (-FourJJloopWidth/2,-(2/10)*FourJJloopLength),(FourJJloopWidth/2,0)]
    JosephsonJunctionTotalLengths = []
    for i, JJrelation in enumerate(JJRelations): 
        JosephsonJunction = DrawJosephsonJunction(JosephsonJunctionCellName ='JosephsonJunction'+str(i+1),
                                          LineWidth = LineWidth,                #width of line connected to the junction
                                          FingerWidth = JJrelation*JJparameters['FingerWidth'],           #
                                          FingerLength = JJparameters['FingerLength'],          #
                                          TaperWidth = JJparameters['TaperWidth'],             #
                                          BridgeWidth = JJrelation*JJparameters['BridgeWidth'],           #
                                          layer = eBeamLayer)
        JosephsonJunctionTotalLengths.append(JJparameters['FingerLength']+JJparameters['TaperWidth']+JJrelation*JJparameters['BridgeWidth'])
        FourJJloop.add(gds.CellReference(JosephsonJunction, origin=JosephsonJunctionOrigins[i], rotation=-90))

    '''Loop line (with JJ spacings)'''
    FourJJloopLine = gds.Cell(FourJJloopCellName+'LoopLine', exclude_from_current=True)
    FourJJloopLine.add(gds.FlexPath([(-FourJJloopWidth/2,(4/10)*FourJJloopLength-JosephsonJunctionTotalLengths[0]), (-FourJJloopWidth/2,(1/10)*FourJJloopLength)], LineWidth, layer=eBeamLayer))
    FourJJloopLine.add(gds.FlexPath([(-FourJJloopWidth/2,(1/10)*FourJJloopLength-JosephsonJunctionTotalLengths[1]), (-FourJJloopWidth/2,-(2/10)*FourJJloopLength)], LineWidth, layer=eBeamLayer))
    FourJJloopLine.add(gds.FlexPath([(-FourJJloopWidth/2,-(2/10)*FourJJloopLength-JosephsonJunctionTotalLengths[2]), (-FourJJloopWidth/2,-FourJJloopLength/2),
                                     (FourJJloopWidth/2,-FourJJloopLength/2), (FourJJloopWidth/2,-JosephsonJunctionTotalLengths[3])], LineWidth, corners = "natural", layer=eBeamLayer)) #corners="circular bend", bend_radius=LineWidth
    FourJJloopLine.add(gds.FlexPath([(FourJJloopWidth/2,0),(FourJJloopWidth/2,FourJJloopLength/2),
                                      (-FourJJloopWidth/2,FourJJloopLength/2),(-FourJJloopWidth/2,(4/10)*FourJJloopLength)], LineWidth, corners="natural", layer=eBeamLayer)) #corners="circular bend", bend_radius=LineWidth
    FourJJloop.add(gds.CellReference(FourJJloopLine, origin=(0,0)))
    
    return FourJJloop

def DrawFourJJqubit    (   FourJJqubitCellName = '4JJqubit',
                    FourJJloopLength = 10.5,
                    FourJJloopWidth = 0,                        #Square loop, unless width is specified
                    LineWidth = 2,                              #width of the loop wire
                    Spacing = 20,                               #Spacing between plates and grounding plane, also half the spacing between plates
                    RectangleLength = 100,
                    RectangleWidth = 100,
                    JJparameters=     {'FingerWidth': 0.36,     #Dictionary with the Josephson junction parameters
                                        'FingerLength':  1,  #
                                        'TaperWidth': 0.5,      #
                                        'BridgeWidth': 0.14},
                    JJRelations =  [1,1,1,1],                   #Relations between Josephson junction sizes
                    CircuitLayer = 2,                           #Layer for photolithography mask
                    eBeamLayer = 5):                            #Layer for eBeam deposition     
    """
    This function returns a four-Josephson-junctions loop cell that contains references to the 4JJ (not necesserily identical) loop cell, a shunting capacitor cell
    placed next to the qubit and the connection to it.
    It separately returns the capacitor cell (two plates placed next to the loop) to be added to the resist mask.
    Three junctions (usually the bigger ones) are on one branch of the loop, and the fourth is on the other.
    The cell origin is defined at the center of the capacitor.
    """
    
    if (FourJJloopWidth==0):
        FourJJloopWidth = FourJJloopLength #If width is not specifically defined make a square loop
        
    '''Four JJ loop'''
    FourJJloop =  DrawFourJJloop(   FourJJloopCellName = FourJJqubitCellName+'Loop',
                    FourJJloopLength = FourJJloopLength,
                    FourJJloopWidth = FourJJloopWidth,
                    LineWidth = LineWidth,                #width of the RFsquid line
                    JJparameters=JJparameters,         #Dictionary with the Josephson junction parameters
                    JJRelations =  JJRelations,                       #Relations between Josephson junction sizes
                    eBeamLayer = eBeamLayer)                                  #Layer for eBeam deposition
    
    '''Shunting capcitor and qubit background'''
    RectangleLength = 100
    RectangleWidth = 100
    qubit_origin = (-RectangleWidth/2+FourJJloopWidth/2,0)
        
    FourJJCapacitor = gds.Cell(FourJJqubitCellName, exclude_from_current=True)
    Plate1 = gds.Rectangle((-RectangleWidth/2,Spacing),(RectangleWidth/2,Spacing+RectangleLength)).fillet(Spacing/2)
    Plate2 = gds.Rectangle((-RectangleWidth/2,-Spacing-RectangleLength),(RectangleWidth/2,-Spacing)).fillet(Spacing/2)
    Circle = gds.Round((0,0), 2*Spacing)
    CapacitorBackground = gds.Rectangle((-RectangleWidth/2-Spacing,-2*Spacing-RectangleLength),(Spacing+RectangleWidth/2,2*Spacing+RectangleLength)).fillet(Spacing/2)
    QubitBackground = gds.Rectangle((qubit_origin[0]-FourJJloopWidth/2-Spacing,qubit_origin[1]-FourJJloopLength/2-Spacing),(-RectangleWidth/2,qubit_origin[1]+FourJJloopLength/2+Spacing)).fillet(Spacing/2)
    FourJJCapacitor.add(gds.boolean([QubitBackground,CapacitorBackground,Circle], [Plate1,Plate2], 'not', layer=CircuitLayer))
 
    '''Connection lines and pads'''
    FourJJconnectionLine = gds.Cell(FourJJqubitCellName+'ConnectionLine', exclude_from_current=True)
    FourJJconnectionLine.add(gds.Rectangle((RectangleWidth/2-(3/2)*FourJJloopLength,Spacing+FourJJloopLength/2), (RectangleWidth/2+FourJJloopLength/2,Spacing+FourJJloopLength*(3/2)) ,layer=eBeamLayer))
    ConnectionLinePath = gds.FlexPath([(RectangleWidth/2-FourJJloopLength/2,FourJJloopLength+Spacing),(RectangleWidth/2-FourJJloopWidth/2,FourJJloopLength/2),(RectangleWidth/4-FourJJloopWidth/2,FourJJloopLength/2)], 
                                          2*LineWidth, corners="circular bend", bend_radius=2*LineWidth,  layer=eBeamLayer)
    ConnectionLinePath.segment((FourJJloopWidth/2+LineWidth/2,FourJJloopLength/2), width = LineWidth)
    FourJJconnectionLine.add(ConnectionLinePath)
    
    FourJJCapacitor.add(gds.CellReference(FourJJconnectionLine, origin=qubit_origin))
    FourJJCapacitor.add(gds.CellReference(FourJJconnectionLine,origin=qubit_origin, x_reflection=True, rotation=0))  
    FourJJCapacitor.add(gds.CellReference(FourJJloop, origin=qubit_origin))
    
    return [FourJJCapacitor, FourJJCapacitor]

def DrawBiasLine (   BiaslineCellName = 'Biasline',
                    BiaslineLength = 600,
                    LineWidth = 6,                #width of each parallel line
                    SpaceWidth = 10,              #space between parallel lines
                    BigWidth = 96,                #maximum launcher-lines width
                    LauncherWidth = 352,          #total launcher width
                    layer = 2):
    """
    This function returns a biasline cell that contains references to one mainline (two parallel lines) cell , 
    one launcher cell and a T-shape terminal.
    The cell origin is defined at the (center of the) end of the terminal.
    """
    '''launcher'''
    launcher = DrawLauncher(   LauncherCellName = BiaslineCellName+'Launcher',
                    LineWidth = LineWidth,        #width of each parallel line
                    SpaceWidth = SpaceWidth,      #space between parallel lines
                    BigWidth = 96,                #maximum launcher-lines width
                    LauncherWidth = 352,          #total launcher width     
                    layer = 2)
    
    '''main line'''
    VerticalDistance = BiaslineLength/8 #Distance from from terminal to lancher (perpendicular to launcher) 
    mainline = gds.Cell(BiaslineCellName+'Mainline', exclude_from_current=True)
    mainline.add(gds.FlexPath([(0,0),(BiaslineLength,0),(BiaslineLength,-VerticalDistance)], [LineWidth, LineWidth], LineWidth + SpaceWidth ,
                               corners="circular bend", bend_radius=LineWidth, layer=layer))
    
    '''terminal'''
    TerminalWidth = 60 #Terminal part total width
    terminal = gds.Cell(BiaslineCellName+'Terminal', exclude_from_current=True)
    
    #Antenna connected to grounding plane
    terminal.add(gds.Rectangle((-LineWidth,SpaceWidth/2+LineWidth), (0,TerminalWidth/2), layer=layer))
    terminal.add(gds.Rectangle((-LineWidth,-SpaceWidth/2-LineWidth), (0,-TerminalWidth/2), layer=layer))
    terminal.add(gds.Rectangle((SpaceWidth,-TerminalWidth/2), (SpaceWidth+LineWidth,TerminalWidth/2), layer=layer))
    
    # Antenna isolated from grounding plane
    # terminal.add(gds.FlexPath([(0,-SpaceWidth/2),(0,-SpaceWidth/2-TerminalWidth/2),(SpaceWidth+LineWidth,-SpaceWidth/2-TerminalWidth/2),
    #                             (SpaceWidth+LineWidth,SpaceWidth/2+TerminalWidth/2),(0,SpaceWidth/2+TerminalWidth/2),(0,SpaceWidth/2)], 
    #                                   LineWidth, ends= 'flush', corners="circular bend", bend_radius=0.6*LineWidth, layer=layer))
    
    #Adds cell references to main cell
    Biasline = gds.Cell(BiaslineCellName, exclude_from_current=True)
    Biasline.add(gds.CellReference(launcher, origin=(-BiaslineLength-LineWidth-SpaceWidth, VerticalDistance)))
    Biasline.add(gds.CellReference(mainline, origin=(-BiaslineLength-LineWidth-SpaceWidth,VerticalDistance)))
    Biasline.add(gds.CellReference(terminal, origin=(-LineWidth-SpaceWidth,0), rotation = -90))

    return [Biasline]