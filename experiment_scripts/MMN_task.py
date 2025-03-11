# Emilia Butters, University of Cambridge, February 2023

#%%%%%%%%%% IMPORT LIBRARIES %%%%%%%%%%
from psychopy import visual, core, sound, data, gui, logging
from psychopy.visual import TextStim, ImageStim, MovieStim3
from psychopy.hardware import keyboard
from scipy.io.wavfile import write
from datetime import datetime


import psychopy.event
import pandas as pd
import numpy as np
import random as rd
import os
import serial

#%%%%%%%%%% Path directories %%%%%%%%%%
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

#%%%%%%%%%% Experiment %%%%%%%%%%

class Experiment:

    def __init__(self, portname, test, fullscreen, monitor, volume):
        self.__port_name = portname
        self.__path = '/Users/emilia/Documents/Dementia task piloting/Lumo'
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
        self.__fullscreen = fullscreen
        self.__mode = test
        self.__monitor = monitor
        self.volume = volume

    #%%%%% SETTING UP EXPERIMENT %%%%%
    def __setup(self):
        print(f"Setting up experiment...")
        experiment_name = 'Optical Neuroimaging and Cognition (ONAC)'
        self.__experiment_info = {'Participant': ''}
        if self.__mode:
            dlg = gui.DlgFromDict(dictionary=self.__experiment_info, sortKeys=False, title=experiment_name)
            if not dlg.OK:
                print("User pressed 'Cancel'!")
                core.quit()
        else:
            self.__experiment_info = {'Participant': 'test'}

        self.__experiment_info['date'] = data.getDateStr()
        self.__experiment_info['expName'] = experiment_name
        self.__experiment_info['psychopyVersion'] = '2021.2.3'
        self.__endfilename = _thisDir + os.sep + u'data/%s_%s_%s_%s' % (self.__experiment_info['Participant'],
                                                           experiment_name, self.__experiment_info['date'], 'MMN_task')

        self.__this_exp = data.ExperimentHandler(name=experiment_name, extraInfo=self.__experiment_info,
                                                 originPath='C:/Users/emilia/PycharmProjects/experiment/MMN_task.py',
                                                 savePickle=True, saveWideText=True,
                                                 dataFileName=self.__endfilename)
        # Setting up a log file
        log_file = logging.LogFile(self.__endfilename + '.log', level=logging.EXP)
        logging.console.setLevel(logging.WARNING)
        self.__filename_save = '/P' + str(self.__experiment_info['Participant'])

        end_exp_now = False
        frame_tolerance = 0.001

        if self.__mode:
            if self.__port_name is not None:
                self.__port = serial.Serial(self.__port_name, baudrate=9600)

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

    def __break(self):
        print(f'Break time!')
        break_text = (self.__path + '/Instructions/task_finished.png')
        break_stim = ImageStim(self.__win, break_text, units='pix', size=self.__size)
        self.__win.color = [0, 0, 0]
        break_stim.draw()
        self.__win.flip()
        self.__check_for_escape()
        psychopy.event.waitKeys()

    def __ready(self):
        ready_text = ImageStim(self.__win, image=(self.__path + '/ready.png'), units='pix', size=self.__size)
        ready_text.draw()
        self.__win.flip()
        self.__check_for_escape()
        psychopy.event.waitKeys()

    def __wait(self, duration=2):
        core.wait(duration+rd.random()/10)

    def __blank_screen(self, duration=1, colour='black'):
        if colour == 'black':
            self.__blank.draw()
            self.__win.flip()
            core.wait(duration)
            self.__win.flip()
            self.__check_for_escape()
        elif colour == 'grey':
            self.__win.color = [0, 0, 0]
            self.__win.flip()
            self.__blank.draw()
            self.__win.flip()
            core.wait(duration)
            self.__win.color = [-1, -1, -1]
            self.__win.flip()
            self.__check_for_escape()

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

    def __showimage(self, image, duration=None):
        showimg = ImageStim(self.__win, image=(self.__path + image), size=self.__size)
        self.__win.color = [0, 0, 0]
        showimg.draw()
        self.__win.flip()
        if duration is not None:
            core.wait(duration)
            self.__win.flip()
            self.__check_for_escape()
        else:
            psychopy.event.waitKeys()

    def __start_trigger(self):
        self.__win.callOnFlip(self.__port.write, 'Z'.encode())
        self.__win.flip()
        self.__check_for_escape()
        d = datetime.utcnow()
        self.__this_exp.addData('Time', d)
        self.__this_exp.nextEntry()

    def mismatched_negativity(self):
        '''
        Task 3: mismatched negativity task
        This is based on the mismatched negativity task currently used in Milos with MEG and EEG.

        :return: dataframe of tones presented

        '''

        print(f'Running mismatched negativity task...')
        movie_stimulus = self.__path + '/mismatched_negativity_task/video_1.mp4'
        auditory_stimuli = pd.read_csv(self.__path + '/mismatched_negativity_task/fixed_stims.csv')

        auditory_stimuli = auditory_stimuli[1:]
        auditory_stimuli = auditory_stimuli.reset_index()

        # Instructions
        if self.__mode:
            self.__present_instructions(self.__path + '/mismatched_negativity_task/mismatched_negativity_instructions.csv')

        self.__blank.draw()
        if self.__mode:
            self.__start_trigger()
        self.__win.flip()
        self.__check_for_escape()
        self.__wait(duration=2)

        MMN_data = []

        next_flip = self.__win.getFutureFlipTime(clock='ptb')
        movie_stim = MovieStim3(self.__win, movie_stimulus)
        movie_stim.setAutoDraw(True)
        while movie_stim.status != visual.FINISHED:
            for k in range(len(auditory_stimuli)):
                trigger = auditory_stimuli['Trigger'][k]
                condition = auditory_stimuli['Condition'][k]
                sound_file = self.__path + '/mismatched_negativity_task/auditory_stimuli/' + \
                                         auditory_stimuli['Sound'][k] + '.wav'
                sound_play = sound.Sound(sound_file, secs=1, hamming=True, volume=self.volume)
                duration = auditory_stimuli['Timing'][k]
                trigger_sent = False
                sound_played = False
                self.__clock.reset()
                while self.__clock.getTime() < duration:
                    if self.__mode and not trigger_sent:
                        self.__win.callOnFlip(self.__port.write, trigger.encode())
                        trigger_sent = True
                    if not sound_played:
                        sound_play.play(when=next_flip)
                        sound_played = True
                    self.__win.flip()
                    self.__check_for_escape()

                df = pd.DataFrame({'condition': [condition], 'sound': auditory_stimuli['Sound'][k]})
                MMN_data.append(df)
                self.__this_exp.addData('Condition', [condition])
                self.__this_exp.addData('Sound', auditory_stimuli['Sound'][k])
                self.__this_exp.nextEntry()

        self.__break()

        # Data saving
        print(f'Saving data...')
        MMN_data = pd.concat(MMN_data)
        MMN_data = MMN_data.reset_index()
        MMN_data.to_csv((self.__path + '/mismatched_negativity_task/participant_data/' + str(self.__filename_save)
                         + '_mismatched_negativity_task_data' + self.__experiment_info['date'] + '.csv'), header=True)

    def __end_all_experiment(self, duration=1):
        """
        Begins ending routine

        :param duration: Duration of wait time before exiting.
        """

        print(f"Ending experiment...")
        self.__showimage('/Instructions/task_finished_mid.png', duration)
        self.__win.mouseVisible = True
        self.__win.flip()
        self.__this_exp.saveAsWideText(self.__endfilename + '.csv', delim='auto')
        self.__this_exp.saveAsPickle(self.__endfilename)
        logging.flush()
        if self.__mode:
            self.__port.close()
        self.__win.close()
        core.quit()

 #%%%%% RUN EXPERIMENT %%%%%%
    def run(self):
        self.__setup()
        self.mismatched_negativity()
        self.__end_all_experiment()

e = Experiment(portname='/dev/tty.usbserial-FTBXN67I', fullscreen=True, test=True, monitor=True, volume=1)
e.run()

