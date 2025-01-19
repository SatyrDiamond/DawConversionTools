# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins
import math
import os
import numpy as np

def get_timebase(i_val):
	if i_val == 2: return 0.004
	if i_val == 3: return 0.005
	if i_val == 16: return 0.010
	if i_val == 17: return 0.020
	if i_val == 18: return 0.040
	if i_val == 19: return 0.050
	

class input_mmf(plugins.base):
	def is_dawvert_plugin(self):
		return 'input'
	
	def get_shortname(self):
		return 'mmf'
	
	def get_name(self):
		return 'Mobile Music File'
	
	def get_priority(self):
		return 0
	
	def get_prop(self, in_dict): 
		in_dict['file_ext'] = ['mmf']
		in_dict['fxrack_params'] = ['vol','pan','pitch']
		in_dict['auto_types'] = ['nopl_ticks']
		in_dict['track_nopl'] = True
		in_dict['plugin_included'] = ['universal:midi']
		in_dict['audio_filetypes'] = ['wav']
		in_dict['fxtype'] = 'rack'
		in_dict['projtype'] = 'rm'

	def get_detect_info(self, detectdef_obj):
		detectdef_obj.headers.append([0, b'MMMD'])

	def parse(self, convproj_obj, dawvert_intent):
		from objects import audio_data
		from objects.songinput import midi_in
		from objects.file_proj import proj_mmf

		convproj_obj.fxtype = 'rack'
		convproj_obj.type = 'rm'

		project_obj = proj_mmf.smaf_song()

		if dawvert_intent.input_mode == 'file':
			if not project_obj.load_from_file(dawvert_intent.input_file): exit()

		samplefolder = dawvert_intent.path_samples['extracted']

		firstma2 = False
		#if True in [isinstance(x, proj_mmf.smaf_track_ma2) for x in project_obj.tracks2]:

			#for grpnum, track in enumerate(project_obj.tracks2):
			#	if track:
			#		timebase = get_timebase(track.timebase_dur)
			#		realtime = int(timebase*(math.pi*10000))
			#		if not firstma2: 
			#			song_obj = midi_in.midi_song(16, realtime, 120, [4,4])
			#			track_obj = song_obj.create_track(len(track.sequence))
			#			firstma2 = True
			#		
			#			track_obj.track_name = 'MA2 #'+str(grpnum)
#
			#		curpos = 0
			#		for msg in track.sequence:
			#			curpos += msg.resttime
#
			#			channel = msg.channel+(grpnum*4)
#
			#			if msg.event_type == 'note':
			#				track_obj.note_dur(curpos, channel, msg.note_key+36+(msg.note_oct*12), 100, msg.duration)
#
			#			elif msg.event_type == 'program':
			#				track_obj.program_change(curpos, channel, msg.value)
#
			#			elif msg.event_type == 'bank':
			#				track_obj.control_change(curpos, channel, 0, msg.value)
#
			#			elif msg.event_type == 'volume':
			#				track_obj.control_change(curpos, channel, 7, msg.value)
#
			#			elif msg.event_type == 'pan':
			#				track_obj.control_change(curpos, channel, 10, msg.value)
#
			#			elif msg.event_type == 'expression':
			#				track_obj.control_change(curpos, channel, 11, msg.value)
#
			#			else:
			#				print(msg.event_type)
#
			#song_obj.postprocess()
			#song_obj.to_cvpj(convproj_obj)

		for track in project_obj.tracks3:
			if track != None:
				timebase = get_timebase(track.timebase_dur)
				realtime = int(timebase*(math.pi*10000))
				song_obj = midi_in.midi_song(16, realtime, 120, [4,4])
				song_obj.fx_offset = 1

				track_obj = song_obj.create_track(len(track.sequence))
				curpos = 0
				for event in track.sequence:
					curpos += event[0]
					if event[1] == 8: track_obj.note_dur(curpos, event[2], event[3], 127, event[4])
					elif event[1] == 9: track_obj.note_dur(curpos, event[2], event[3], event[4], event[5])
					elif event[1] == 11: track_obj.control_change(curpos, event[2], event[3], event[4])
					elif event[1] == 12: track_obj.program_change(curpos, event[2], event[3])
					elif event[1] == 14: track_obj.pitchwheel(curpos, event[2], event[3])

				song_obj.postprocess()

				for soundnum, hzsnd in track.audio.items():
					hz, sounddata = hzsnd
					strnum = str(soundnum).zfill(2)

					wav_path = samplefolder + 'snd_' + strnum + '.wav'
					audio_obj = audio_data.audio_obj()
					audio_obj.decode_from_codec('yamaha_aica', sounddata)
					audio_obj.rate = hz
					audio_obj.to_file_wav(wav_path)

					sampleref_obj = convproj_obj.sampleref__add(wav_path, wav_path, None)

				for x in song_obj.instruments.midi_instruments.data:
					if x['bank'] == 124: 
						x['is_custom'] = 1
						x['custom_name'] = 'MA-3 Voice #'+str(x['inst'])
						x['custom_color_used'] = 1
						x['custom_color'] = [30,30,30]
					if x['bank'] == 125: 
						x['is_custom'] = 1
						x['custom_name'] = 'MA-3 Drum/Stream #'+str(x['inst'])
						x['custom_color_used'] = 1
						x['custom_color'] = [30,30,30]
				
				song_obj.to_cvpj(convproj_obj)

				audiotracks = {}

				audiofx = convproj_obj.fxrack[1]
				audiofx.visual.name = 'MA-3 Audio'
				audiofx.visual.color.set_float([0.2,0.2,0.2])

				maxnum = 0
				for soundnum, sounddata in track.audio.items():
					strnum = str(soundnum).zfill(2)
					audtrack_obj = convproj_obj.track__add('audio'+strnum, 'audio', 1, False)
					audtrack_obj.fxrack_channel = 1
					audtrack_obj.visual.name = 'Sound #'+str(soundnum)
					audtrack_obj.params.add('vol', 0.3, 'float')
					audiotracks[soundnum] = audtrack_obj
					if soundnum>maxnum: maxnum = soundnum

				filternstream = track_obj.notes.data.data['key']<16
				findex = np.where(filternstream)

				for audionote in track_obj.notes.data.data[findex]:
					wav_path = samplefolder + 'snd_' + str(audionote['key']+1).zfill(2) + '.wav'
					soundnum = audionote['key']+1
					if soundnum in audiotracks:
						audtrack_obj = audiotracks[soundnum]
						placement_obj = audtrack_obj.placements.add_audio()
						placement_obj.time.set_startend(audionote['start'], audionote['end'])
						placement_obj.sample.sampleref = wav_path
						placement_obj.sample.vol = audionote['vol']/127

				break

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.params.add('bpm', 120, 'float')