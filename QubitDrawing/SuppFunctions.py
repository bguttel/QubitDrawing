# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 13:50:17 2020

@author: User
"""

import numpy as np
from scipy import special as sp

"""Supplementary functions for the QubitDrawingFunctions module."""

def Rotation2Letter(number):
    '''Sometimes gdspy uses angle numbers and sometimes the letters l or r'''
    if number == 90:
        return 'l'
    elif number ==-90:
        return 'r'
    else:
        print('Not recognized Rotation2Letter number!')
        return

def TupleSum (tuple1,tuple2):
    Sum = tuple(map(sum, zip(tuple1, tuple2)))
    return Sum

def TupleNegative (tuple1):
    Negative = tuple(-1*np.asarray(tuple1))
    return Negative

def coplanar_waveguide(epsilon_r,       #Dielectric constant of the substrate
                                  d,    #[length], substrate's height
                                  W,    #[length], microstrip width
                                  S):   #[length], Space from ground plane
    '''Impedance and effective relative permittivity of a micro strip placed on a dialectric material.
    https://sci-hub.tw/10.1049/el:19840120. (or Simons p.21).
    Calculation using elliptic integrals of the first kind.
    Matching the calculator in https://www.microwaves101.com/calculators/864-coplanar-waveguide-calculator'''
    
    k_0 = W/(W+2*S)
    k_1 = np.sinh(np.pi*W/(4*d))/np.sinh((np.pi*(W+2*S))/(4*d))
    k_00 = np.sqrt(1-np.square(k_0)) #k'_0 in book notation
    k_11 = np.sqrt(1-np.square(k_1)) #k'_1 in book notation
    epsilon_e = 1+ (((epsilon_r-1)/2) * (sp.ellipk(k_1)/sp.ellipk(k_11)) * (sp.ellipk(k_00)/sp.ellipk(k_0)))
    Z_0 = (30*np.pi/np.sqrt(epsilon_e))*(sp.ellipk(k_00)/sp.ellipk(k_0))
    return Z_0, epsilon_e

def Wavelength2Frequency(Wavelength,   #[m]
                         epsilon_e=1): #Effective relative permittivity, default is vacuum.

    c = 299792458                   #[m/s], speed of light in vacuum
    v_p =  c/np.sqrt(epsilon_e)     #[m/s], phase velocity                               
    Frequency = v_p/Wavelength      #[Hz]
    return Frequency

def Frequency2Wavelength(Frequency,    #[Hz]
                         epsilon_e=1): #Effective relative permittivity, default is vacuum.

    c = 299792458                   #[m/s], speed of light in vacuum
    v_p =  c/np.sqrt(epsilon_e)     #[m/s], phase velocity                               
    Wavelength = v_p/Frequency     
    return Wavelength