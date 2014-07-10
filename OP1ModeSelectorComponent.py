##################################################################
# 
#   Copyright (C) 2012 Imaginando, Lda & Teenage Engineering AB
#   
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 2
#   of the License, or any later version.
#  
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   For more information about this license please consult the
#   following webpage: http://www.gnu.org/licenses/gpl-2.0.html
#
##################################################################

import Live;

from consts import *

# Ableton Live imports

from _Framework.ModeSelectorComponent import ModeSelectorComponent
from _Framework.ButtonElement import ButtonElement
from _Framework.EncoderElement import EncoderElement
from _Framework.InputControlElement import *

class OP1ModeSelectorComponent(ModeSelectorComponent):
    __doc__ = ' SelectorComponent that assigns buttons to functions based on the shift button '
    
    def __init__(self, parent, transport, mixer, session):
        ModeSelectorComponent.__init__(self)

        self._current_mode = -1
        self._mode_index = 0

        self._parent = parent
        self._transport = transport
        self._mixer = mixer
        self._session = session

        self._shift_active = False;

        # creating buttons for the arrows keys
        self._left_arrow_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_LEFT_ARROW)
        self._right_arrow_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_RIGHT_ARROW)
        
        # creating button for the shift key
        self._shift_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, OP1_SHIFT_BUTTON)
        self._shift_button.add_value_listener(self.shift_pressed)

        # creating buttons for the note shifted keys
        self.note_keys_shifted_buttons = []
        self.note_keys_shifted_ccs = [77, 79, 81, 83, 84, 86, 88, 89, 91, 93, 95, 96, 98]

        # creating a list of shifted note keys buttons
        for i in range(len(self.note_keys_shifted_ccs)):
            self.note_keys_shifted_buttons.append(ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, self.note_keys_shifted_ccs[i]))

        # creating buttons for the note keys
        self.note_keys_buttons = []
        self.note_keys_ccs = [53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76]

        # creating a list of note keys buttons
        for i in range(len(self.note_keys_ccs)):
            self.note_keys_buttons.append(ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, self.note_keys_ccs[i]))

    def disconnect(self):
        ModeSelectorComponent.disconnect(self)
        self._transport = None
        return None

    def number_of_modes(self):
        return NUM_MODES

    def shift_pressed(self, value):
        # handling shift pressed (only for transport mode)
        if (self._current_mode==OP1_MODE_TRANSPORT):
            if (value==127):
                self._transport.set_seek_buttons(None, None)
                self._left_arrow_button.add_value_listener(self.shifted_left_arrow_pressed)
                self._right_arrow_button.add_value_listener(self.shifted_right_arrow_pressed)
            else:
                self._left_arrow_button.remove_value_listener(self.shifted_left_arrow_pressed)
                self._right_arrow_button.remove_value_listener(self.shifted_right_arrow_pressed)
                self._transport.set_seek_buttons(self._right_arrow_button, self._left_arrow_button)

    def shifted_left_arrow_pressed(self, value):
        # handling negative loop offset behavior
        if (value==127):
            if (self._parent.song().loop_start>0):
                self._parent.song().loop_start -= 1

    def shifted_right_arrow_pressed(self, value):
        # handling positive loop offset behavior
        if (value==127):
            self._parent.song().loop_start += 1

    def set_loop(self, index, set_loop_start):
        # handling set loop
        self._parent.song().loop = 1

        if (set_loop_start):
            self._parent.song().loop_start = round(self._parent.song().current_song_time)

        if (index==0):
            self._parent.song().loop_length = 1
        elif (index==1):
            self._parent.song().loop_length = 2
        elif (index==2):
            self._parent.song().loop_length = 4
        elif (index==3):
            self._parent.song().loop_length = 8
        elif (index==4):
            self._parent.song().loop_length = 16
        elif (index==5):
            self._parent.song().loop_length = 32
        elif (index==6):
            self._parent.song().loop_length = 64
        elif (index==7):
            self._parent.song().loop_length = 128
        elif (index==8):
            self._parent.song().loop_length = 256
        elif (index==9):
            self._parent.song().loop_length = 512
        elif (index==10):
            self._parent.song().loop_length = 1024
        elif (index==11):
            self._parent.song().loop_length = 2048
        elif (index==12):
            self._parent.song().loop_length = 4096

    def note_key_pressed(self, value, sender):
        # determining index of note key button in list
        index = self.note_keys_buttons.index(sender)

        if (self._current_mode==OP1_MODE_MIXER):
            # if on mixer mode, use not key to select a track
            all_tracks = ((self.song().visible_tracks + self.song().return_tracks)) + (self.song().master_track,) #modified
            if (index < len(all_tracks)):
                self.song().view.selected_track = all_tracks[index]

        elif (self._current_mode==OP1_MODE_TRANSPORT):
            # if on transport mode, use key to set loop
            self.set_loop(index, False)
            

    def note_key_shifted_pressed(self, value, sender):
        # determining index of note key button in list
        index = self.note_keys_shifted_buttons.index(sender)

        if (self._current_mode==OP1_MODE_TRANSPORT):
            # if on transport mode, use key to set loop with loop start change
            self.set_loop(index, True)

    def clip_color_changed(self):
        self._parent.log("clip color changed")

    def has_clip_listener(self):
        self._parent.log("slot has clip")

    def update(self):
        # handle current mode change
        if self.is_enabled():
            # clearing last mappings
            self.clear()

            # updating current mode index
            self._current_mode = self._mode_index

            # based on current mode, perform necessay re mappings
            if (self._mode_index == OP1_MODE_PERFORM):
                # nothing is done for perform mode
                self._parent.log("PERFORM MODE")

            elif (self._mode_index == OP1_MODE_TRANSPORT):
                self._parent.log("TRANSPORT MODE")
                
                # settings arrows as seek buttons
                self._transport.set_seek_buttons(self._right_arrow_button, self._left_arrow_button)

                # adding value listeners for note keys and note shifted keys

                for i in range(NUM_TRACKS):
                    self.note_keys_buttons[i].add_value_listener(self.note_key_pressed, True)

                for i in range(NUM_TRACKS):
                    self.note_keys_shifted_buttons[i].add_value_listener(self.note_key_shifted_pressed, True)
                
            elif (self._mode_index == OP1_MODE_MIXER):
                self._parent.log("MIXER MODE")

                # setting arrow butons as track select buttons
                self._mixer.set_select_buttons(self._right_arrow_button, self._left_arrow_button)

                # adding value listeners for note keys
                for i in range(NUM_TRACKS):
                    self.note_keys_buttons[i].add_value_listener(self.note_key_pressed, True)

            elif (self._mode_index == OP1_MODE_CLIP):
                self._parent.log("CLIP MODE")

                # setting arrows as track bank buttons
                self._session.set_track_bank_buttons(self._right_arrow_button, self._left_arrow_button)

                # setting last key note as stop all clip button
                self._session.set_stop_all_clips_button(ButtonElement(True, MIDI_NOTE_TYPE, CHANNEL, 100))

                # setting track stop clip buttons
                self._session.set_stop_track_clip_buttons(tuple(self.note_keys_shifted_buttons))

                # setting track individual clip launch button
                for i in range(NUM_TRACKS):
                    self._session.scene(0).clip_slot(i).set_launch_button(self.note_keys_buttons[i])
                    
                # setting scene launch button
                self._session.scene(0).set_launch_button(self.note_keys_buttons[NUM_TRACKS])                    

        return None

    def clear(self):
        if (self._current_mode == OP1_MODE_PERFORM):
            self._parent.log("CLEARING PERFORM MODE")

        elif (self._current_mode == OP1_MODE_TRANSPORT):
            self._parent.log("CLEARING TRANSPORT MODE")

            # removing value listeners for note keys
            for i in range(NUM_TRACKS):
                self.note_keys_buttons[i].remove_value_listener(self.note_key_pressed)

            # removing value listeners for shifted note keys
            for i in range(NUM_TRACKS):
                self.note_keys_shifted_buttons[i].remove_value_listener(self.note_key_shifted_pressed)

            # clearing transport seek buttons
            self._transport.set_seek_buttons(None, None)
            
        elif (self._current_mode == OP1_MODE_MIXER):
            self._parent.log("CLEARING MIXER MODE")
            
            # removing value listeners for note key press
            for i in range(NUM_TRACKS):
                self.note_keys_buttons[i].remove_value_listener(self.note_key_pressed)

            self._parent.clear_tracks_assigments()

            # clearing mixer track select buttons
            self._mixer.set_select_buttons(None, None)
            
        elif (self._current_mode == OP1_MODE_CLIP):
            self._parent.log("CLEARING CLIP MODE")

            # clearing session track bank buttons
            self._session.set_track_bank_buttons(None,None)

            # clearing session stop all clips button
            self._session.set_stop_all_clips_button(None)

            # clearing session track stop clip buttons
            self._session.set_stop_track_clip_buttons(None)
            
            # clearing individual clip launch button
            for i in range(NUM_TRACKS):
                self._session.scene(0).clip_slot(i).set_launch_button(None)

            # clearing session launch button
            self._session.scene(0).set_launch_button(None)
