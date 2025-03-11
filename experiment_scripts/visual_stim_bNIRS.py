# Emilia Butters, University of Cambridge, February 2023

#%%%%%%%%%% IMPORT LIBRARIES %%%%%%%%%%
from psychopy import visual, core, sound, data, gui, logging
from psychopy.visual import TextStim, ImageStim, MovieStim3, DotStim
from psychopy.hardware import keyboard
from psychopy.constants import FINISHED, NOT_STARTED

import psychopy.event
import pandas as pd
import numpy as np
import random as rd
import os
import serial
import psychtoolbox as ptb
import random as rd

#%%%%%%%%%% Path directories %%%%%%%%%%
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

#%%%%%%%%%% Experiment %%%%%%%%%%

class Experiment:

    def __init__(self, fullscreen, monitor):
        self.__path = '/Users/emilia/Documents/Dementia task piloting/Mini-CYRIL'
        self.__win = None
        self.__clock = None
        self.__kb = None
        self.__port = None
        self.__blank = None
        self.__fixation_cross = None
        self.__filename_save = None
        self.__experiment_info = None
        self.__this_exp = None
        self.__endfilename = None
        self.__size = None
        self.__fullscreen = fullscreen
        self.__monitor = monitor

    #%%%%% SETTING UP EXPERIMENT %%%%%
    def __setup(self):
        print(f"Setting up experiment...")
        experiment_name = 'Optical Neuroimaging and Cognition (ONAC)'
        self.__experiment_info = {'Participant': ''}
        dlg = gui.DlgFromDict(dictionary=self.__experiment_info, sortKeys=False, title=experiment_name)
        if not dlg.OK:
            print("User pressed 'Cancel'!")
            core.quit()
        self.__experiment_info['date'] = data.getDateStr()
        self.__experiment_info['expName'] = experiment_name
        self.__experiment_info['psychopyVersion'] = '2021.2.3'
        self.__endfilename = _thisDir + os.sep + u'data/%s_%s_%s_%s' % (self.__experiment_info['Participant'],
                                                                        experiment_name, self.__experiment_info['date'],
                                                                        'visual_stim_bNIRS')

        self.__this_exp = data.ExperimentHandler(name=experiment_name, extraInfo=self.__experiment_info,
                                                 originPath='C:/Users/emilia/PycharmProjects/experiment/visual_stim_bNIRS.py',
                                                 savePickle=True, saveWideText=True,
                                                 dataFileName=self.__endfilename)
        # Setting up a log file
        log_file = logging.LogFile(self.__endfilename + '.log', level=logging.EXP)
        logging.console.setLevel(logging.WARNING)

        end_exp_now = False
        frame_tolerance = 0.001

        if self.__monitor:
            self.__size = (1920, 1080)
            screen = 1
        else:
            self.__size = (1440, 900)
            screen = 0

        # Set up window
        self.__win = visual.Window(self.__size, color=[-1, -1, -1], fullscr=self.__fullscreen, screen=screen)

        # Monitor frame rate
        self.__experiment_info['frameRate'] = self.__win.getActualFrameRate()
        if self.__experiment_info['frameRate'] is not None:
            frame_dur = 1.0 / round(self.__experiment_info['frameRate'])
        else:
            frame_dur = 1.0 / 60.0

        # Hide mouse
        self.__win.mouseVisible = False

        # Setting up useful trial components
        self.__clock = core.Clock()
        self.__kb = keyboard.Keyboard()
        self.__blank = TextStim(self.__win, text='')
        self.__fixation_cross = TextStim(self.__win, text='+', height=0.1, color=(-1, -1, 1))

#%%%%% SOME USEFUL FUNCTIONS %%%%%

    def __check_for_escape(self):
        if self.__kb.getKeys(keyList=['escape']):
            self.__end_all_experiment()
            core.quit()

    def __baseline(self, duration=30):
        self.__win.color = [0, 0, 0]
        self.__clock.reset()
        while self.__clock.getTime() < (duration + (rd.random() / 10)):  # Randomise the baseline duration
            self.__fixation_cross.draw()
            self.__win.flip()
            self.__check_for_escape()
        self.__win.color = [-1, -1, -1]

    def __ready(self):
        ready_text = ImageStim(self.__win, image=(self.__path + '/ready.png'), units='pix', size=self.__size)
        ready_text.draw()
        self.__win.flip()
        self.__check_for_escape()
        psychopy.event.waitKeys()

    def __wait(self, duration=2):
        core.wait(duration+rd.random()/10)

    def __present_instructions(self, filepath):
        """
        Presents instructions of different types.

        :param filepath: The filepath of the instruction csv.
        """

        instructions = pd.read_csv(filepath)
        self.__win.color = [0, 0, 0]
        for j in instructions['path']:
            instruction_stim = ImageStim(self.__win, j, units='pix', size=self.__size)
            instruction_stim.draw()
            self.__win.flip()
            self.__check_for_escape()
            psychopy.event.waitKeys()


    #%%%%% TASKS %%%%%

    def __overall_instructions(self):
        """
        Overall study instructions

        """

        print(f"Presenting instructions...")
        self.__present_instructions((self.__path + "/Instructions/overall_instructions.csv"))

    def visual_stimulation(self):
        '''
        Task 4: visual stimulation paradigm.

        Returns
        -------

        '''

        print(f"Running visual stimulation paradigm")

        # Set up trial components
        wedge_1 = visual.RadialStim(self.__win, tex='sqrXsqr', color=1, size=1.5,
                                   visibleWedge=[0, 360], radialCycles=6, angularCycles=12, interpolate=False,
                                   autoLog=False, pos=(0, 0))
        wedge_2 = visual.RadialStim(self.__win, tex='sqrXsqr', color=-1, size=1.5,
                                   visibleWedge=[0, 360], radialCycles=6, angularCycles=12, interpolate=False,
                                   autoLog=False, pos=(0, 0))

        fixation_cross = TextStim(self.__win, text='+', height=0.2, color=[0, 0, 0], pos=(0, 0))
        dot = DotStim(self.__win, units='pix', nDots=1, fieldPos=(0, 0), dotSize=25, fieldShape='circle',
                      color=(1, 0, 1),
                      speed=0)
        visual_stim_data = []

        # Instructions
        # self.__present_instructions(self.__path + '/visual_stimulation/instructions.csv')

        for i in range(0, 12):
            print('Trial number: %s out of %s' % (i, 12))
            frequency = 1/7.5
            detected=False
            self.__baseline(10)
            self.__check_for_escape()

            start_int = rd.randint(1, 7)
            dot_ints = tuple((start_int, start_int + 2))

            self.__clock.reset()

            while self.__clock.getTime() < 10:
                if self.__clock.getTime() % frequency < frequency / 2.0:
                    stim = wedge_1
                else:
                    stim = wedge_2
                stim.draw()
                fixation_cross.draw()
                if dot_ints[0] < self.__clock.getTime() < dot_ints[1]:
                    dot.draw()
                    if not detected:
                        keys = self.__kb.getKeys(keyList=['space'])
                        if len(keys)>0:
                            response = 1
                            detected = True
                        else:
                            response = 0
                self.__win.flip()
                self.__check_for_escape()
            self.__kb.clearEvents()
            self.__baseline(5)

            df = pd.DataFrame({'detected': [response]})
            visual_stim_data.append(df)

        # Data saving
        print(f'Saving data...')
        visual_stim_data_export = pd.concat(visual_stim_data, ignore_index=True)
        visual_stim_data_export.to_csv(
            (self.__path + '/visual_stimulation/participant_data/P' + str(self.__experiment_info['Participant']) + '_visual_stim_data' \
            + self.__experiment_info['date'] + '.csv'), header=True, index=False)

    #%%%%% END EXPERIMENT ROUTINE %%%%%
    def __end_all_experiment(self, duration=1):
        """
        Begins ending routine

        :param duration: Duration of wait time before exiting.
        """

        print(f"Ending experiment...")
        end_text = (self.__path + '/Instructions/task_finished_mid.png')
        ending = ImageStim(self.__win, end_text)
        ending.draw()
        self.__win.flip()
        self.__wait(duration)
        self.__win.mouseVisible = True
        self.__win.flip()
        logging.flush()
        self.__win.close()
        core.quit()

    #%%%%% RUN EXPERIMENT %%%%%%
    def run(self):
        self.__setup()
        self.visual_stimulation()
        self.__end_all_experiment()




e = Experiment(fullscreen=True, monitor=True)
e.run()