import os

CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
CHEM3D_COM_NAME = 'Chem3D.Application.19'
CHEM3D_DOC_COM_NAME = 'Chem3D.Document'
WORK_DIR =  os.path.join(CONFIG_DIR, './temp')
INIT_SAVE_DIR = CONFIG_DIR

# XTB Setiings
PATHLIB  = 'C:/msys64/mingw64/bin'  # None if not necessary
PATH = 'D:/programs/xtb-6.4.1/bin'
XTBPATH = 'D:/programs/xtb-6.4.1/bin/share/xtb'
OMP_NUM_THREADS = 4
OMP_STACKSIZE = '1G'

DEBUG = True

XRC_FILE = os.path.join(CONFIG_DIR, 'xtbc3d.xrc')
SOLVENT_LIST = os.path.join(CONFIG_DIR, 'solventlist')

WINDOW_SIZE = (300, 255)
TEXT_VIEW_FRAME_SIZE = (800,600)

XYZ_FORMAT = '{:2s}    {:=.8f}    {:=.8f}    {:=.8f}\n'