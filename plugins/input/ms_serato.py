# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from objects.file_proj import proj_serato
from functions import colors
from objects.convproj import sample_entry
import plugins
import urllib.parse
import os
import copy

contentpath = os.path.join(os.path.expanduser('~'), 'Music\\Serato Studio\\Content\\')

def parse_filepath(i_file):
	filename = urllib.parse.unquote(i_file)
	if filename.startswith('content://'): filepath = contentpath+filename[10:]
	elif filename.startswith('file://'): filepath = filename[8:]
	else: filepath = filename
	return filepath.replace("\\","/").replace("//","/")

def calc_audiostretch(orgpoint, original_bpm, bpm, playback_speed, printd):
	outpos = orgpoint
	outpos *= 2
	outpos /= 120/bpm
	outpos /= playback_speed
	outpos /= bpm/original_bpm
	return outpos

class input_serato(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'input'
	def getshortname(self): return 'serato'
	def gettype(self): return 'rs'
	def getdawinfo(self, dawinfo_obj): 
		dawinfo_obj.track_lanes = True
		dawinfo_obj.name = 'Serato Studio'
		dawinfo_obj.file_ext = 'ssp'
	def supported_autodetect(self): return False
	def parse(self, convproj_obj, input_file, dv_config):
		convproj_obj.type = 'ms'
		convproj_obj.set_timings(960, True)

		useaudioclips = True

		project_obj = proj_serato.serato_song()
		project_obj.load_from_file(input_file)

		sample_data = {}

		for num, scene_deck in enumerate(project_obj.scene_decks):
			cvpj_trackid = 'track_'+str(num+1)
			cvpj_instid = 'track_'+str(num+1)+'_0'
			if not useaudioclips: track_obj = convproj_obj.add_track(cvpj_trackid, 'instruments', 1, False)
			elif useaudioclips: track_obj = convproj_obj.add_track(cvpj_trackid, 'audio' if scene_deck.type == 'sample' else 'instruments', 1, False)
			track_obj.visual.name = scene_deck.name

			if scene_deck.channel_strip.post_fader_effects != None:
				for fxnum, pfe in enumerate(scene_deck.channel_strip.post_fader_effects):
					if pfe != None:

						fx_effect = pfe['effect']
						fxplugid = cvpj_trackid+'_fx_'+str(fxnum)
						fxtype = fx_effect[10:] if fx_effect.startswith(':/effects/') else fx_effect
						fxplugin_obj = convproj_obj.add_plugin(fxplugid, 'native-serato-fx', fxtype)
						fxplugin_obj.role = 'effect'
						
						if 'value' in pfe:
							fx_value = pfe['value']
							fxplugin_obj.params.add('amount', fx_value, 'float')


			if scene_deck.type == 'drums':
				for dnum, drumdata in enumerate(scene_deck.drums):
					cvpj_instid_p = 'track_'+str(num+1)+'_'+str(dnum)
					if drumdata.used:
						drumsamp = drumdata.sample

						samplefile = drumsamp.file

						if samplefile:
							samplepath = parse_filepath(drumsamp.file)

							plugin_obj, sampleref_obj, samplepart_obj = convproj_obj.add_plugin_sampler(cvpj_instid_p, samplepath)
							inst_obj = convproj_obj.add_instrument(cvpj_instid_p)
							inst_obj.pluginid = cvpj_instid_p
							inst_obj.visual.name = urllib.parse.unquote(samplefile).split('/')[-1]

							if drumsamp.color:
								inst_obj.visual.color.set_hex(drumsamp.color[3:])

							samplepart_obj.point_value_type = 'percent'
							samplepart_obj.start = drumsamp.start/sampleref_obj.dur_sec
							samplepart_obj.end = drumsamp.end/sampleref_obj.dur_sec
							samplepart_obj.stretch.preserve_pitch = True
							samplepart_obj.pitch = drumsamp.pitch_shift
							samplepart_obj.stretch.set_rate_speed(project_obj.bpm, drumsamp.playback_speed, False)
							samplepart_obj.trigger = 'oneshot'

			if scene_deck.type == 'instrument':
				inst_obj = convproj_obj.add_instrument(cvpj_instid)
				inst_obj.visual.name = scene_deck.name
				inst_obj.visual.color.set_float([0.48, 0.35, 0.84])

			if scene_deck.type == 'sample':
				if useaudioclips == False:
					plugin_obj, pluginid = convproj_obj.add_plugin_genid('native-serato-inst', 'sampler')
					inst_obj = convproj_obj.add_instrument(cvpj_instid)
					inst_obj.pluginid = pluginid
	
					if scene_deck.sample_file:
						inst_obj.visual.name = urllib.parse.unquote(scene_deck.sample_file).split('/')[-1]
	
						samplepath = parse_filepath(scene_deck.sample_file)
	
						convproj_obj.add_sampleref(samplepath, samplepath)
	
						samplepart_obj = plugin_obj.samplepart_add('sample')
						samplepart_obj.sampleref = samplepath
						samplepart_obj.stretch.set_rate_speed(project_obj.bpm, scene_deck.playback_speed, False)
	
					plugin_obj.datavals.add('type', scene_deck.type)
					plugin_obj.datavals.add('name', scene_deck.name)
					plugin_obj.datavals.add('original_key', scene_deck.original_key)
					plugin_obj.datavals.add('tempo_map', scene_deck.tempo_map)
					plugin_obj.datavals.add('original_bpm', scene_deck.original_bpm)
					plugin_obj.datavals.add('bpm', scene_deck.bpm)
					plugin_obj.datavals.add('bar_mode_enabled', scene_deck.bar_mode_enabled)
	
					colorlist = []
	
					for kn, sample_region in enumerate(scene_deck.cues):
						if sample_region: 
							plugin_obj.regions.add(kn, kn, sample_region)
							if 'color' in sample_region: colorlist.append(sample_region['color'])
	
					colorocc = dict([[colorlist.count(x),x] for x in set(colorlist)])
					maxnum = max(list(colorocc))
					if colorocc:
						coloro = colorocc[maxnum][3:]
						inst_obj.visual.color.set_hex(coloro)
				else:
					s_sample_entry = sample_data[num] = {}
					s_sample_entry['deck'] = scene_deck

					if scene_deck.sample_file:
						playspeed = scene_deck.playback_speed
						playspeed *= 120/project_obj.bpm
						playspeed *= project_obj.bpm/scene_deck.original_bpm

						samplepath = parse_filepath(scene_deck.sample_file)
						sampleref_obj = convproj_obj.add_sampleref(samplepath, samplepath)
						sampleref_obj.visual.name = urllib.parse.unquote(scene_deck.sample_file).split('/')[-1]
						samplepart_obj = sample_entry.cvpj_sample_entry()
						samplepart_obj.sampleref = samplepath
						samplepart_obj.pitch = scene_deck.key_shift
						samplepart_obj.stretch.set_rate_tempo(project_obj.bpm, playspeed, False)
						samplepart_obj.stretch.preserve_pitch = True

						s_sample_entry['part'] = samplepart_obj
						s_sample_entry['sampleref'] = sampleref_obj

		for num, scene in enumerate(project_obj.scenes):
			sceneid = 'scene_'+str(num+1)
			scene_obj = convproj_obj.add_scene(sceneid)
			scene_obj.visual.name = scene.name
			scene_obj.visual.color.set_hex(project_obj.audio_deck_color_collection[num])

			for decknum, deck_sequence in enumerate(scene.deck_sequences):
				cvpj_trackid = 'track_'+str(decknum+1)

				scene_deck = project_obj.scene_decks[decknum]
				usechannel = 1 if scene_deck.type == 'drums' else 0

				if deck_sequence.notes:
					trscene_obj = convproj_obj.add_track_scene(cvpj_trackid, sceneid, 'main')

					if scene_deck.type == 'drums':
						placement_obj = trscene_obj.add_notes()
						placement_obj.position = 0
						placement_obj.duration = scene.length
						for note in deck_sequence.notes:
							if note.start < scene.length:
								key = note.number+note.channel
								if key >= 60: key -= 60
								placement_obj.notelist.add_m('track_'+str(decknum+1)+'_'+str(key), note.start, note.duration, 0, note.velocity/100, None)
						placement_obj.notelist.sort()

					if scene_deck.type == 'instrument':
						placement_obj = trscene_obj.add_notes()
						placement_obj.position = 0
						placement_obj.duration = scene.length
						for note in deck_sequence.notes:
							if note.start < scene.length:
								key = note.number-60
								placement_obj.notelist.add_m('track_'+str(decknum+1)+'_0', note.start, note.duration, key, note.velocity/100, None)

					if scene_deck.type == 'sample':
						if useaudioclips == False:
							placement_obj = trscene_obj.add_notes()
							placement_obj.position = 0
							placement_obj.duration = scene.length
							for note in deck_sequence.notes:
								if note.start < scene.length:
									key = note.number
									placement_obj.notelist.add_m('track_'+str(decknum+1)+'_0', note.start, note.duration, key, note.velocity/100, None)
						else:
							placement_obj = None
							s_sample_entry = sample_data[decknum]
							if 'part' in s_sample_entry:
								sampledeck = s_sample_entry['deck']
								samplepart = s_sample_entry['part']
								sampleref = s_sample_entry['sampleref']

								extendlast = not sampledeck.momentary

								samplenotes = {}

								for note in deck_sequence.notes:
									key = note.number
									cuedata = sampledeck.cues[key]

									color = None
									if 'color' in cuedata:
										color = cuedata['color'][3:]

									startoffset = calc_audiostretch(cuedata['start'], scene_deck.original_bpm, project_obj.bpm, sampledeck.playback_speed, True)
									endoffset = calc_audiostretch(cuedata['end'], scene_deck.original_bpm, project_obj.bpm, sampledeck.playback_speed, False)

									samplenotes[note.start] = [note.duration, startoffset*960, endoffset*960, color]

									#placement_obj.cut_type = 'cut'
									#placement_obj.cut_start = startoffset*960

								#a.sort(key=lambda x: x[1])


								samplenotes = dict(sorted(samplenotes.items()))
								if extendlast and samplenotes:
									poslist = list(samplenotes)
									for n in range(len(poslist)-1):
										curpos = poslist[n+1]
										prevpos = poslist[n]
										curnote = samplenotes[poslist[n]][0] = curpos-prevpos
									lastpos = poslist[-1]
									samplenotes[lastpos][0] = scene.length-lastpos

								for nstart, ndata in samplenotes.items():
									nend, startoffset, endoffset, color = ndata
	
									if endoffset-startoffset:

										duration = min(nend, endoffset-startoffset, scene.length-nstart)

										if min(endoffset-startoffset, duration) > 3:

											placement_obj = trscene_obj.add_audio()
											placement_obj.sample = copy.deepcopy(samplepart)
											placement_obj.position = nstart
											placement_obj.duration = duration

											placement_obj.visual.color.set_hex(color)

											placement_obj.cut_type = 'cut'
											placement_obj.cut_start = startoffset

		for arrangement in project_obj.arrangement.tracks:
			if arrangement.type == 'scene':
				for clip in arrangement.clips:
					scenepl_obj = convproj_obj.add_scenepl()
					scenepl_obj.position = clip.start
					scenepl_obj.duration = clip.length
					scenepl_obj.id = 'scene_'+str(clip.scene_slot_number+1)
				break

		if 'name' in project_obj.metadata: convproj_obj.metadata.name = project_obj.metadata['name']
		if 'artist' in project_obj.metadata: convproj_obj.metadata.author = project_obj.metadata['artist']
		if 'genre' in project_obj.metadata: convproj_obj.metadata.genre = project_obj.metadata['genre']
		if 'label' in project_obj.metadata: convproj_obj.metadata.comment_text = project_obj.metadata['label']

		convproj_obj.do_actions.append('do_addloop')
		convproj_obj.params.add('bpm', project_obj.bpm, 'float')