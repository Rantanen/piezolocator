
import http.server
import socketserver
import math
import serial
import random
import numpy as np
import numpy.linalg as npla
import threading
import pygame
from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from scipy.optimize import fsolve
from base64 import b64encode, b64decode

test_data = [
    b'SPURIOUS',
    b'0;1000;1000',
    b'S1',
    b'1000;0;1000',
    b'S1',
    b'1000;1000;0',
    b'S2',
    b'0;0;0',
    b'S3',
    b'500;500;0',
    b'S4',
    b'0;0;0',
    b'200;200;0',
    b'0;0;300',
]


serial_data = [
    '1000;0;1000'
]

def circleEq( x0, y0, r0 ):
    return lambda x, y: ( x - x0 )**2 + ( y - y0 )**2 - r0**2

def eq_for_sensor( sensor, dist ):
    return circleEq( sensor['x'], sensor['y'], dist )

def eq_for_point( sensors, times ):
    eqs = []

    def make_eq( x0, y0, d0 ):
        return lambda g: circleEq( x0, y0, d0 + g[2] )( g[0], g[1] )

    for s in sensors:
        d0 = times[ s['idx'] ]
        sx = s['x']
        sy = s['y']
        eqs.append( make_eq( sx, sy, d0 ) )

    return lambda guess: list( map( lambda eq: eq( guess ), eqs ) )

class CoordinateSystem:
    def __init__( self ):
        self.count = 0
        self.sensors = []
        self.calibration = []

    def add_sensor( self, times ):

        mean_times = np.mean( times, axis = 0 )
        idx = list( mean_times ).index( min( mean_times ) )

        self.calibration.extend( times )

        if( len( self.sensors ) == 0 ):
            
            self.sensors.append( {
                'x': 0,
                'y': 0,
                'idx': idx,
            } )

        elif( len( self.sensors ) == 1 ):

            first_sensor = self.sensors[0]['idx']
            dist = mean_times[ first_sensor ]
            self.sensors.append( {
                'x': dist,
                'y': 0,
                'idx': idx,
            } )

        else:

            first_sensor = self.sensors[0]['idx']
            second_sensor = self.sensors[1]['idx']
            dist_to_first = mean_times[ first_sensor ]
            dist_to_second = mean_times[ second_sensor ]

            eq = lambda guess: [
                eq_for_sensor( self.sensors[0], dist_to_first )( *guess ),
                eq_for_sensor( self.sensors[1], dist_to_first )( *guess ),
            ]
            guess = (
                self.sensors[1]['x'] * 0.5,
                np.mean(( dist_to_first, dist_to_second ) )
            )

            x, y = fsolve( eq, guess )

            self.sensors.append( {
                'x': x,
                'y': y,
                'idx': idx
            } )

    def set_center( self, times ):

        mean_times = np.mean( times, axis = 0 )
        self.center_solution = fsolve(
            eq_for_point( self.sensors, mean_times ),
            ( self.sensors[1]['x'] / 2, self.sensors[2]['y'] / 2, 1000 )
        )
        self.center = ( self.center_solution[0], self.center_solution[1] )

    def set_up( self, times ):

        mean_times = np.mean( times, axis = 0 )
        x, y, d = fsolve(
            eq_for_point( self.sensors, mean_times ),
            self.center_solution
        )
        self.up = ( x, y )

        self.up_vector = np.subtract( self.up, self.center )
        self.up_angle = np.angle([ self.up_vector[0] + self.up_vector[1]*1.0j ])
        self.up_dist = npla.norm( self.up_vector )

    def __str__( self ):
        out = 'Coordinate system:\n'
        for s in self.sensors:
            out += '  Sensor {}:\n'.format( s['idx'] )
            out += '    x: {}\n'.format( s['x'] )
            out += '    y: {}\n'.format( s['y'] )
        out += '  Center: {}\n'.format( self.center )
        out += '  Up: {}\n'.format( self.up_vector )
        return out

    def get_point( self, times ):

        guess = self.center_solution
        retry = 10
        while True:
            xyd, info, ler, msg = fsolve(
                eq_for_point( self.sensors, times ),
                self.center_solution,
                full_output = True
            )

            if ler == 1:
                break
            if retry == 0:
                return (-9999, -9999, 9999 )

            guess = (
                random.random() * self.sensors[1]['x'],
                random.random() * self.sensors[2]['y'],
                0
            )
            retry -= 1

        x, y, d = xyd
        x, y = np.subtract( ( x, y ), self.center )

        cos_angle = math.cos( self.up_angle )
        sin_angle = math.sin( self.up_angle )
        xx = x * cos_angle + y * sin_angle
        yy = y * cos_angle - x * sin_angle

        xx /= self.up_dist
        yy /= self.up_dist

        return ( xx, yy, d )

    def serialize( self ):
        return b64encode( pickle.dumps( self ) )

    @staticmethod
    def deserialize( data ):
        return pickle.loads( b64decode( data ) )

sockets = []
class StateMachine:
    SENSORS = 1
    CENTER = 2
    UP = 3
    TARGET = 4
    
    def __init__( self ):
        self.coords = CoordinateSystem()
        self.points = []
        self.state = StateMachine.SENSORS

    def add_point( self, times ):
        if( self.state == StateMachine.TARGET ):
            x, y, d = self.coords.get_point( times )
            print( x, y )
            for s in sockets:
                s.sendMessage( {
                    'type': 'HIT',
                    'x': x,
                    'y': y,
                } )
        else:
            self.points.append( times )

    def next_state( self, state ):

        if self.state == StateMachine.SENSORS:
            self.coords.add_sensor( self.points )
        elif self.state == StateMachine.CENTER:
            self.coords.set_center( self.points )
        elif self.state == StateMachine.UP:
            self.coords.set_up( self.points )

        if state == StateMachine.TARGET:
            for s in sockets:
                s.sendMessage( {
                    'type': 'CONFIGURATION',
                    'config': self.coords.serialize()
                } )

        self.points = []
        self.state = state
state = StateMachine()

state.add_point( [ 28262, 20832, 0 ] )
state.add_point( [ 31092, 20776, 0 ] )
state.add_point( [ 32090, 21788, 0 ] )
state.add_point( [ 29052, 21144, 0 ] )
state.add_point( [ 33442, 22754, 0 ] )

state.next_state( StateMachine.SENSORS )
state.add_point( [ 35349, 0, 25676 ] )
state.add_point( [ 33823, 0, 21968 ] )

state.next_state( StateMachine.SENSORS )
state.add_point( [ 0, 37314, 27633 ] )
state.add_point( [ 0, 27550, 26657 ] )
state.add_point( [ 0, 28192, 26132 ] )
state.add_point( [ 0, 31892, 27800 ] )
state.add_point( [ 0, 31381, 26868 ] )

state.next_state( StateMachine.CENTER )
state.add_point( [ 0, 6949, 6290 ] )
state.add_point( [ 0, 2875, 1498 ] )
state.add_point( [ 0, 2390, 883 ] )
state.add_point( [ 0, 3318, 854 ] )
state.add_point( [ 0, 3676, 1960 ] )

state.next_state( StateMachine.UP )
state.add_point( [ 0, 35725, 34330 ] )
state.add_point( [ 0, 33246, 32446 ] )
state.add_point( [ 0, 25838, 23198 ] )
state.add_point( [ 0, 27744, 28691 ] )

state.next_state( StateMachine.TARGET )

pygame.init()
SIZE = (1300,1300)
RADIUS = 600
MID = ( int(SIZE[0]/2), int(SIZE[1]/2 ) )
windowSurface = pygame.display.set_mode( SIZE )

BLACK = (0,0,0)
WHITE = (255,255,255)
windowSurface.fill( BLACK )
pygame.draw.circle( windowSurface, WHITE, MID, RADIUS, 3 )

pygame.display.update()

with serial.Serial( '/dev/ttyUSB1', 9600 ) as ser:
    while True:
        print( "Waiting" )
        l = ser.readline()
        print( l )

        print( "strip" )
        l = l.strip()
        if( l == b'SPURIOUS' ):
            continue

        print( "split" )
        l = l.strip()
        nums = list( map( int, l.split( b';' ) ) )
        print( "get_point" )
        x, y, d = state.coords.get_point( nums )
        print( x, y )

        xx = int( MID[0] - RADIUS * y )
        yy = int( MID[1] - RADIUS * x )
        pygame.draw.circle( windowSurface, WHITE, (xx, yy), 10, 3 )
        pygame.display.update()

