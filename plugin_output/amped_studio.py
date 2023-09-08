# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
import io
import os
import zipfile
from functions import placements
from functions import plugins
from functions import data_values
from functions import params
from functions import tracks
from functions import audio
from functions import auto
from functions import notelist_data

id_out_num = 10000
audioidnum = 0

def getid(): 
    global id_out_num
    id_out_num += 1
    return id_out_num

def addsample(zip_wt, filepath): 
    global audioidnum
    global audio_id
    outnum = None
    filebasename = os.path.basename(filepath)
    if filebasename not in audio_id:
        audio_id[filebasename] = audioidnum
        if os.path.exists(filepath):
            filetype = filebasename.split('.')[1]
            if filetype in ['wav']: zip_wt.write(filepath, str(audioidnum))
            else: zip_wt.writestr(str(audioidnum), audio.convert_to_wav(filepath))
            outnum = audioidnum
            audioidnum += 1
    else:
        outnum = audio_id[filebasename]
    return outnum

def amped_maketrack(): 
    amped_trackdata = {}
    amped_trackdata["id"] = getid()
    amped_trackdata["name"] = ""
    amped_trackdata["color"] = "mint"
    amped_trackdata["pan"] = 0
    amped_trackdata["volume"] = 1
    amped_trackdata["mute"] = False
    amped_trackdata["solo"] = False
    amped_trackdata["armed"] = {"mic": False, "keys": False}
    amped_trackdata["regions"] = []
    amped_trackdata["devices"] = []
    amped_trackdata["automations"] = []
    return amped_trackdata

def amped_makeregion(position, duration, offset): 
    amped_region = {}
    amped_region["id"] = getid()
    amped_region["position"] = position/4
    amped_region["length"] = duration/4
    amped_region["offset"] = offset/4
    amped_region["loop"] = 0
    amped_region["clips"] = []
    amped_region["midi"] = {"notes": [], "events": [], "chords": []}
    amped_region["name"] = ""
    amped_region["color"] = "mint"
    return amped_region

def cvpjauto_to_ampedauto(autopoints):
    ampedauto = []
    for autopoint in autopoints:
        ampedauto.append({"pos": autopoint['position']/4, "value": autopoint['value']})
    return ampedauto

class output_cvpj_f(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'Amped Studio'
    def getshortname(self): return 'amped'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawcapabilities(self): 
        return {
        'placement_cut': True,
        'auto_nopl': True,
        'placement_audio_stretch': ['rate']
        }
    def getsupportedplugins(self): return []
    def parse(self, convproj_json, output_file):
        global audio_id
        cvpj_l = json.loads(convproj_json)
        cvpj_placements = cvpj_l['track_placements']
        audio_id = {}

        zip_bio = io.BytesIO()
        zip_amped = zipfile.ZipFile(zip_bio, mode='w', compresslevel=None)

        amped_bpm = int(params.get(cvpj_l, [], 'bpm', 120)[0])
        amped_numerator = 4
        amped_denominator = 4
        if 'timesig' in cvpj_l: amped_numerator, amped_denominator = cvpj_l['timesig']

        amped_tracks = []
        amped_filenames = {}

        if 'track_order' in cvpj_l and 'track_data' in cvpj_l:
            for cvpj_trackid in cvpj_l['track_order']:
                cvpj_trackdata = cvpj_l['track_data'][cvpj_trackid]

                amped_trackdata = amped_maketrack()
                amped_trackdata["name"] = cvpj_trackdata['name'] if 'name' in cvpj_trackdata else ''
                amped_trackdata["pan"] = params.get(cvpj_trackdata, [], 'pan', 0)[0]
                amped_trackdata["volume"] = params.get(cvpj_trackdata, [], 'vol', 1.0)[0]
                amped_trackdata["mute"] = not params.get(cvpj_trackdata, [], 'on', 1.0)[0]
                amped_trackdata["solo"] = bool(params.get(cvpj_trackdata, [], 'solo', 1.0)[0])

                if cvpj_trackid in cvpj_placements:

                    if 'notes' in cvpj_placements[cvpj_trackid]: 
                        cvpj_noteclips = notelist_data.sort(cvpj_placements[cvpj_trackid]['notes'])
                        for cvpj_noteclip in cvpj_noteclips:
                            amped_position = cvpj_noteclip['position']
                            amped_duration = cvpj_noteclip['duration']
                            amped_offset = 0
                            if 'cut' in cvpj_noteclip:
                                cutdata = cvpj_noteclip['cut']
                                cuttype = cutdata['type']
                                if cuttype == 'cut': 
                                    amped_offset = cutdata['start']/4 if 'start' in cutdata else 0
                            amped_region = amped_makeregion(amped_position, amped_duration, amped_offset)

                            amped_notes = []

                            if 'notelist' in cvpj_noteclip:
                                for cvpj_note in cvpj_noteclip['notelist']:
                                    amped_notes.append({
                                        "position": cvpj_note['position']/4, 
                                        "length": cvpj_note['duration']/4, 
                                        "key": int(cvpj_note['key']+60),
                                        "velocity": cvpj_note['vol']*100 if 'vol' in cvpj_note else 100, 
                                        "channel": 0
                                        })

                            amped_region["midi"]['notes'] = amped_notes

                            amped_trackdata["regions"].append(amped_region)

                    if 'audio' in cvpj_placements[cvpj_trackid]:
                        cvpj_audioclips = notelist_data.sort(cvpj_placements[cvpj_trackid]['audio'])
                        for cvpj_audioclip in cvpj_audioclips:
                            amped_position = cvpj_audioclip['position']
                            amped_duration = cvpj_audioclip['duration']
                            amped_offset = 0

                            rate = 1

                            if 'cut' in cvpj_audioclip:
                                cutdata = cvpj_audioclip['cut']
                                cuttype = cutdata['type']
                                if cuttype == 'cut': 
                                    amped_offset = cutdata['start']/4 if 'start' in cutdata else 0

                            if 'audiomod' in cvpj_audioclip:
                                cvpj_audiomod = cvpj_audioclip['audiomod']
                                stretch_method = cvpj_audiomod['stretch_method'] if 'stretch_method' in cvpj_audiomod else None
                                stretch_data = cvpj_audiomod['stretch_data'] if 'stretch_data' in cvpj_audiomod else {'rate': 1.0}
                                stretch_rate = stretch_data['rate'] if 'rate' in stretch_data else 1
                                if stretch_method == 'rate_speed': rate = stretch_rate
                                if stretch_method == 'rate_tempo': rate = stretch_rate*(amped_bpm/120)

                            audioid = None
                            if 'file' in cvpj_audioclip:
                                audioid = addsample(zip_amped, cvpj_audioclip['file'])
                            amped_audclip = {}
                            amped_audclip['contentGuid'] = {}
                            if audioid != None: amped_audclip['contentGuid']['userAudio'] = {"exportedId": audioid}
                            amped_audclip['position'] = 0
                            amped_audclip['gain'] = 1
                            amped_audclip['length'] = amped_duration+amped_offset
                            amped_audclip['offset'] = amped_offset
                            amped_audclip['stretch'] = 1/rate
                            amped_audclip['reversed'] = False

                            amped_region = amped_makeregion(amped_position, amped_duration, 0)
                            amped_region["clips"] = [amped_audclip]
                            amped_trackdata["regions"].append(amped_region)


                    for autoname in [['vol','volume'], ['pan','pan']]:
                        autopoints = tracks.a_auto_nopl_getpoints(cvpj_l, ['track',cvpj_trackid,autoname[0]])
                        if autopoints != None: 
                            ampedauto = cvpjauto_to_ampedauto(auto.remove_instant(autopoints, 0, False))
                            amped_trackdata["automations"].append({"param": autoname[1], "points": ampedauto})

                amped_tracks.append(amped_trackdata)

        for aid in audio_id:
            amped_filenames[audio_id[aid]] = aid

        amped_out = {}
        amped_out["fileFormat"] = "AMPED SONG v1.3"
        amped_out["createdWith"] = "nothing"
        amped_out["settings"] = {"deviceDelayCompensation": True}
        amped_out["tracks"] = amped_tracks
        amped_out["masterTrack"] = {"volume": 1, "devices": []}
        amped_out["workspace"] = {"library":False,"libraryWidth":300,"trackPanelWidth":160,"trackHeight":80,"beatWidth":24,"contentEditor":{"active":False,"trackId":5,"mode":"noteEditor","beatWidth":48,"noteEditorKeyHeight":10,"velocityPanelHeight":90,"velocityPanel":False,"audioEditorVerticalZoom":1,"height":400,"scroll":{"left":0,"top":0},"quantizationValue":0.25,"chordCreator":{"active":False,"scale":{"key":"C","mode":"Major"}}},"trackInspector":True,"trackInspectorTrackId":5,"arrangementScroll":{"left":0,"top":0},"activeTool":"arrow","timeDisplayInBeats":False,"openedDeviceIds":[],"virtualKeyboard":{"active":False,"height":187,"keyWidth":30,"octave":5,"scrollPositions":{"left":0,"top":0}},"xybeatz":{"active":False,"height":350,"zones":[{"genre":"Caribbean","beat":{"bpm":100,"name":"Zouk Electro 2"}},{"genre":"Soul Funk","beat":{"bpm":120,"name":"Defunkt"}},{"genre":"Greatest Breaks","beat":{"bpm":100,"name":"Walk This Way"}},{"genre":"Brazil","beat":{"bpm":95,"name":"Samba Partido Alto 1"}}],"parts":[{"x":0.75,"y":0.75,"gain":1},{"x":0.9,"y":0.2,"gain":1},{"x":0.8,"y":0.45,"gain":1},{"x":0.7,"y":0.7,"gain":1},{"x":0.7,"y":1,"gain":1},{"x":0.5,"y":0.5,"gain":1}],"partId":5,"fullKit":True,"soloPartId":-1,"complexity":50,"zoneId":0,"lastPartId":1},"displayedAutomations":{}}
        amped_out["looping"] = {"active": False, "start": 0, "end": 0}
        amped_out["tempo"] = amped_bpm
        amped_out["timeSignature"] = {"num": 4, "den": 4}
        amped_out["metronome"] = {"active": False, "level": 1}
        amped_out["playheadPosition"] = 0

        if 'timemarkers' in cvpj_l:
            for timemarkdata in cvpj_l['timemarkers']:
                if timemarkdata['type'] == 'loop_area':
                    amped_out["looping"] = {"active": True, "start": timemarkdata['position']/4, "end": timemarkdata['end']/4}

        zip_amped.writestr('amped-studio-project.json', json.dumps(amped_out))
        zip_amped.writestr('filenames.json', json.dumps(amped_filenames))
        zip_amped.close()
        open(output_file, 'wb').write(zip_bio.getbuffer())