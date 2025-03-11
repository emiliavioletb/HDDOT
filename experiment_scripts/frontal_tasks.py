# Emilia Butters, University of Cambridge, February 2023


#%%%%%%%%%% IMPORT LIBRARIES %%%%%%%%%%
from psychopy import visual, core, sound, data, gui, logging
from psychopy.visual import TextStim, ImageStim, MovieStim3
from psychopy.hardware import keyboard
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

    def __init__(self, portname, test, fullscreen, monitor):
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
        self.__size = None
        self.__fullscreen = fullscreen
        self.__mode = test
        self.__monitor = monitor

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
                                                           experiment_name, self.__experiment_info['date'], 'frontal_tasks')

        self.__this_exp = data.ExperimentHandler(name=experiment_name, extraInfo=self.__experiment_info,
                                                 originPath='C:/Users/emilia/PycharmProjects/experiment/frontal_tasks.py',
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
        showimg = ImageStim(self.__win, image=image, size=self.__size)
        self.__win.color = [0, 0, 0]
        showimg.draw()
        self.__win.flip()
        self.__check_for_escape()
        if duration is not None:
            core.wait(duration)
            self.__win.flip()
            self.__check_for_escape()
        else:
            psychopy.event.waitKeys()

    def __chunking(self, lst, n):
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    def __start_trigger(self):
        print('Sending start trigger')
        self.__win.callOnFlip(self.__port.write, 'Z'.encode())
        self.__win.flip()
        self.__check_for_escape()
        d = datetime.utcnow()
        self.__this_exp.addData('Time', d)
        self.__this_exp.nextEntry()

    #%%%%% TASKS %%%%%
    def __overall_instructions(self):
        """
        Overall study instructions

        """

        print(f"Presenting instructions...")
        self.__present_instructions((self.__path + "/Instructions/overall_instructions.csv"))

    def resting_state(self, duration=5):
        """
        Task 5: resting state

        :param duration: Duration of resting state.
        """

        print(f"Running resting state...")
        # LOAD TRIAL COMPONENTS
        resting_state_tone = sound.Sound(value='C', secs=0.1, volume=2)

        # INSTRUCTIONS
        self.__present_instructions(self.__path + '/resting_state/resting_state_instructions.csv')

        # EXPERIMENT BLOCK
        self.__blank.draw()
        if self.__mode:
            self.__start_trigger()
        self.__win.flip()
        self.__check_for_escape()
        self.__wait(duration=2)

        # Start resting state
        self.__clock.reset()
        trigger_sent = False
        while self.__clock.getTime() < (duration * 60+2+(rd.random()/10)):
            while self.__clock.getTime() < (duration*20):
                if self.__mode and not trigger_sent:
                    self.__win.callOnFlip(self.__port.write, 'G'.encode())
                    trigger_sent = True
                self.__blank.draw()
                self.__win.flip()
                self.__check_for_escape()

        if self.__mode:
            self.__port.write('H'.encode())

        resting_state_tone.play()

        self.__break()

    def memory_task(self):

        """

        Implicit memory task

        """
        print('Running implicit memory task')
        # Set up trial components
        text = TextStim(self.__win, text='')
        encoding_text = 'Indoor or outdoor?'
        testing_text = 'Old or new?'

        correct_text = TextStim(self.__win, text='Correct!', color=[0, 1, -1])
        incorrect_text = TextStim(self.__win, text='Incorrect', color=[1, 0, 0])
        no_key_pressed = TextStim(self.__win, text='No key pressed!', color=[-1, -1, 1])

        # Load stimuli
        encoding_stimuli = pd.read_csv(self.__path + '/memory_task/official_stimuli/stimuli/encoded.csv')
        new_stimuli = pd.read_csv(self.__path + '/memory_task/official_stimuli/stimuli/recall.csv')
        practice_stimuli = pd.read_csv(self.__path + '/memory_task/official_stimuli/practice_stimuli/practice.csv')

        # Randomise stimuli
        rand_encoding_stimuli = encoding_stimuli.sample(frac=1, ignore_index=True)
        rand_testing_stimuli = new_stimuli.sample(frac=1, ignore_index=True)

        # Present instructions
        self.__present_instructions((self.__path + '/memory_task/memory_task_instructions.csv'))

        #Practice trials
        print('Running practice trials')
        self.__baseline(5)
        practice_stim = ImageStim(self.__win, units='pix', size=(960, 600))
        text.text = encoding_text
        self.__kb.clearEvents()
        for k in list(range(6)):
            self.__kb.clearEvents()
            img = self.__path + '/memory_task/official_stimuli/practice_stimuli/' + practice_stimuli['filename'][k]
            practice_stim.setImage(img)
            self.__clock.reset()
            key_pressed = False
            while self.__clock.getTime() < 5:
                if self.__clock.getTime() < 3:
                    practice_stim.draw()
                else:
                    text.draw()
                    if not key_pressed:
                        keys = self.__kb.getKeys(keyList=['left', 'right'], waitRelease=False)
                        if len(keys) > 0:
                            key_pressed = True
                self.__win.flip()
                self.__check_for_escape()

            if key_pressed: # If a key is pressed, check if right or wrong
                response = str(keys[-1].name)
                if response == practice_stimuli['corr_ans'][k]:
                    correct_text.draw()
                else:
                    incorrect_text.draw()
            elif not key_pressed:
                    no_key_pressed.draw()
            self.__kb.clearEvents()
            self.__win.flip()
            self.__check_for_escape()
            self.__wait(2)
            self.__blank_screen()

        self.__ready()
        if self.__mode:
            self.__start_trigger()

        self.__wait(2)

        # Set up trial components
        print('Running testing trials')
        phases = ['encoding', 'recall']
        prompts = [encoding_text, testing_text]
        stimuli = [rand_encoding_stimuli, rand_testing_stimuli]

        stimulus = ImageStim(self.__win, units='pix', size=(960, 600))
        block_data = []

        for a in range(len(phases)):
            a = 1
            phase = phases[a]
            if a == 0:
                block_trigger = 'J'
            else:
                block_trigger = 'L'
            text.text = prompts[a]
            all_stimuli = list(self.__chunking(stimuli[a], 2))

            for block in all_stimuli:

                block = block.reset_index()

                self.__baseline(10)

                if self.__mode:
                    self.__win.callOnFlip(self.__port.write, block_trigger.encode())

                for j in range(len(block)):
                    img = self.__path + '/memory_task/official_stimuli/' + block['filename'][j]
                    stimulus.setImage(img)
                    correct_answer = block['corr_ans'][j]
                    condition_setting = block['condition_setting'][j]
                    condition_memory = block['condition_memory'][j]

                    key_pressed_img = False
                    key_pressed_text = False
                    clock_reset_img = False
                    clock_reset_text = False

                    self.__clock.reset()
                    self.__kb.clock.reset()

                    while self.__clock.getTime() < 5:
                        if not clock_reset_img:
                            self.__win.callOnFlip(self.__kb.clock.reset)
                            self.__kb.clearEvents()
                            keys = []
                            clock_reset_img = True
                        if self.__clock.getTime() < 3:
                            stimulus.draw()
                            if not key_pressed_img:
                                keys_img = self.__kb.getKeys(keyList=['left', 'right'], waitRelease=False)
                                if len(keys_img) > 0:
                                    key_pressed_img = True
                                    self.__kb.clearEvents()
                        else:
                            if not clock_reset_text:
                                self.__win.callOnFlip(self.__kb.clock.reset)
                                clock_reset_text = True
                            text.draw()
                            if not key_pressed_text:
                                keys_text = self.__kb.getKeys(keyList=['left', 'right'], waitRelease=False)
                                if len(keys_text) > 0:
                                    key_pressed_text = True
                                    self.__kb.clearEvents()
                        self.__win.flip()
                        self.__check_for_escape()

                    if key_pressed_img:
                        response_img = str(keys_img[-1].name)
                        reaction_time_img = keys_img[-1].rt
                        if response_img == correct_answer:
                            result_img = 1
                        else:
                            result_img = 0
                    elif not key_pressed_img:
                        result_img = np.nan
                        reaction_time_img = np.nan
                        response_img = np.nan

                    if key_pressed_text:
                        response_text = str(keys_text[-1].name)
                        reaction_time_text = keys_text[-1].rt
                        if response_text == correct_answer:
                            result_text = 1
                        else:
                            result_text = 0
                    elif not key_pressed_text:
                        result_text = np.nan
                        reaction_time_text = np.nan
                        response_text = np.nan

                    looped_data = pd.DataFrame({'phase': phase,
                                       'stimulus': text.text,
                                       'condition_setting': [condition_setting],
                                        'condition_memory': [condition_memory],
                                       'trial_number': [block['index'][j]],
                                       'reaction_time_img': [reaction_time_img],
                                       'response_img': [result_img],
                                        'reaction_time_text': [reaction_time_text],
                                        'response_text': [result_text],
                                       'correct_answer': [correct_answer],
                                       'key_pressed_img': [response_img],
                                        'key_pressed_text': [response_text]})
                    block_data.append(looped_data)

                    self.__this_exp.addData('IMT_stimulus', text.text)
                    self.__this_exp.addData('IMT_rt', reaction_time_text)
                    self.__this_exp.addData('IMT_response', result_text)
                    self.__this_exp.addData('IMT_corr_ans', correct_answer)
                    self.__this_exp.addData('IMT_key_pressed', response_text)
                    self.__this_exp.addData('IMT_phase', phase)
                    self.__this_exp.addData('IMT_condition_setting', condition_setting)
                    self.__this_exp.addData('IMT_condition_memory', condition_memory)
                    self.__this_exp.addData('Task', 'IMT')
                    self.__this_exp.nextEntry()

            if a == 0:
                self.__present_instructions((self.__path + '/memory_task/memory_task_instructions_recall.csv'))
                self.__wait()
                self.__blank_screen(duration=1, colour='black')

        self.__break()
        data_export = pd.concat(block_data, ignore_index=True)
        data_export.to_csv((self.__path + '/memory_task/participant_data/' + str(self.__filename_save) \
                                        + '_memory_task_data_' + self.__experiment_info['date'] + '.csv'), header=True, index=False)

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
        # self.memory_task()
        self.resting_state()
        self.__end_all_experiment()

e = Experiment(portname='/dev/tty.usbserial-FTBXN67J', fullscreen=True, test=True, monitor=True)
e.run()
