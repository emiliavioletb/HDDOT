# Emilia Butters, University of Cambridge, February 2023

#%%%%%%%%%% IMPORT LIBRARIES %%%%%%%%%%
from psychopy import visual, core, sound, data, gui, logging
from psychopy.visual import TextStim, ImageStim, MovieStim3
from psychopy.hardware import keyboard
from psychopy.constants import FINISHED, NOT_STARTED
from datetime import datetime

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

    def __init__(self, portname, fullscreen, test, monitor):
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
                                                           experiment_name, self.__experiment_info['date'], 'NM_task')

        self.__this_exp = data.ExperimentHandler(name=experiment_name, extraInfo=self.__experiment_info,
                                                 originPath='C:/Users/emilia/PycharmProjects/experiment/NM_task.py',
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

        # Set up window
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
        self.__fixation_cross = TextStim(self.__win, text='+', height=0.3, color=(-1, -1, 1))

#%%%%% SOME USEFUL FUNCTIONS %%%%%

    def __check_for_escape(self):
        if self.__kb.getKeys(keyList=['escape']):
            self.__end_all_experiment()
            core.quit()

    def __baseline(self, duration=30):
        self.__win.color = [0, 0, 0]
        self.__win.flip()
        self.__check_for_escape()
        self.__clock.reset()
        while self.__clock.getTime() < (duration + (rd.random() / 10)):  # Randomise the baseline duration
            self.__fixation_cross.draw()
            self.__win.flip()
            self.__check_for_escape()
        self.__win.color = [-1, -1, -1]

    def __break(self):
        print(f'Break time!')
        break_text = (self.__path + '/Instructions/break.png')
        self.__win.color = [0, 0, 0]
        break_stim = ImageStim(self.__win, break_text, units='pix', size=self.__size)
        break_stim.draw()
        self.__win.flip()
        self.__check_for_escape()
        psychopy.event.waitKeys()

    def __ready(self):
        ready_text = ImageStim(self.__win, image=(self.__path + '/Instructions/task_start.png'), units='pix', size=self.__size)
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
        for j in instructions['path']:
            instruction_stim = ImageStim(self.__win, j, units='pix', size=self.__size)
            instruction_stim.draw()
            self.__win.flip()
            self.__check_for_escape()
            psychopy.event.waitKeys()

    def __showimage(self, image, duration=None):
        showimg = ImageStim(self.__win, image=(image), size=self.__size)
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
        print('Sending start trigger')
        self.__win.callOnFlip(self.__port.write, 'Z'.encode())
        self.__win.flip()
        self.__check_for_escape()
        d = datetime.utcnow()
        self.__this_exp.addData('Time', d)
        self.__this_exp.nextEntry()

    #%%%%% TASKS %%%%%

    def naturalistic_motor_task(self):
        """
        Task 7: Naturalistic motor task

        """

        print(f"Running naturalistic motor task...")

        # Load task components
        naturalistic_motor_stims = pd.read_csv(self.__path +
                                               '/naturalistic_motor_task/naturalistic_motor_task_stimuli.csv')
        naturalistic_motor_data = []
        naturalistic_motor_stim = TextStim(self.__win, text='')

        # Instructions
        # print(f'Presenting naturalistic motor task instructions...')
        #
        # naturalistic_motor_instructions = MovieStim3(self.__win, (self.__path + '/naturalistic_motor_task/instruction_video.mp4'), \
        #                                              size = (1440, 800))
        # while naturalistic_motor_instructions.status != visual.FINISHED:
        #     naturalistic_motor_instructions.draw()
        #     self.__win.flip()

        self.__ready()

        self.__wait(1)
        if self.__mode:
            self.__start_trigger()

        # Start testing trials
        print(f'Starting naturalistic motor task testing...')
        for k in list(range(3)):
            self.__kb.clearEvents()
            for j in range(len(naturalistic_motor_stims)):
                naturalistic_motor_stim.text = naturalistic_motor_stims['stimulus'].iloc[j]
                trigger = naturalistic_motor_stims['trigger'].iloc[j]
                end_trigger = naturalistic_motor_stims['end_trigger'].iloc[j]
                audio_stim = sound.Sound(naturalistic_motor_stims['instruction'].iloc[j])

                time = 10

                self.__baseline(7)

                trigger_sent = False
                key_pressed = False
                sound_played = False
                next_flip = self.__win.getFutureFlipTime(clock='ptb')
                self.__clock.reset()
                self.__kb.clock.reset()
                if trigger =='C':
                    time = 20
                while self.__clock.getTime() < time and not key_pressed:
                    naturalistic_motor_stim.draw()
                    if self.__mode and not trigger_sent:
                        self.__win.callOnFlip(self.__port.write, trigger.encode())
                        trigger_sent = True
                    if not sound_played:
                        audio_stim.play(when=next_flip)
                        sound_played = True
                    self.__win.flip()
                    self.__check_for_escape()
                    if trigger != 'C':
                        keys = self.__kb.getKeys(keyList=None, waitRelease=False)
                        time += 1
                        if len(keys) > 0:
                            break
                if self.__mode:
                    self.__port.write(end_trigger.encode())
                df = pd.DataFrame({'Stimulus': [naturalistic_motor_stim.text],
                                   'Duration': [keys[-1].rt],
                                   'Trial': [k]})
                naturalistic_motor_data.append(df)
                self.__this_exp.addData('NMT_stimulus', naturalistic_motor_stim.text)
                self.__this_exp.addData('NMT_duration', keys[-1].rt)
                self.__this_exp.addData('Task', 'NMT')
                self.__this_exp.nextEntry()
                self.__wait(1)
                self.__kb.clearEvents()

            # Break
            if k != 2:
                self.__break()

        # Data saving
        print(f'Saving data...')
        naturalistic_motor_data = pd.concat(naturalistic_motor_data, ignore_index=True)
        naturalistic_motor_data.to_csv((self.__path + '/naturalistic_motor_task/participant_data/' + str(self.__filename_save) \
                                        + '_naturalistic_motor_task_data' + self.__experiment_info['date'] + '.csv'), \
                                       header=True, index=False)

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
        self.naturalistic_motor_task()
        self.__end_all_experiment()

e = Experiment(portname='/dev/tty.usbserial-FTBXN67I', fullscreen=True, test=True, monitor=True)
e.run()
