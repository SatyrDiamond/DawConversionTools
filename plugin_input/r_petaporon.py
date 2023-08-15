# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import data_bytes
from functions import tracks
from functions import note_data
from functions import placement_data
from functions import plugins
from functions import song
import plugin_input
import io
import struct
import json

peta_colors = [
[0.22, 0.52, 0.35],
[0.51, 0.88, 0.30],
[1.00, 0.95, 0.46],
[1.00, 0.75, 0.21],
[0.81, 0.47, 0.34],
[0.88, 0.25, 0.25],
[1.00, 0.50, 0.67],
[0.75, 0.25, 0.70],
[0.22, 0.60, 1.00],
[0.43, 0.93, 1.00]]

def getval(i_val):
    if i_val == 91: i_val = 11
    elif i_val == 11: i_val = 91
    elif i_val == -3: i_val = 92
    elif i_val == -2: i_val = 93
    return i_val

midi_inst = {
    'paint': [5,0,3,4,9,14,11,13,1,12]
}

class input_petaporon(plugin_input.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'input'
    def getshortname(self): return 'petaporon'
    def getname(self): return 'Petaporon'
    def gettype(self): return 'r'
    def supported_autodetect(self): return False
    def getdawcapabilities(self): 
        return {
        'track_nopl': True
        }
    def parse(self, input_file, extra_param):
        bytestream = open(input_file, 'r')
        sndstat_data = json.load(bytestream)
        cvpj_l = {}
        peta_notedata = sndstat_data['n'].encode('ascii')
        peta_noteints = struct.unpack("B"*len(peta_notedata), peta_notedata)
        peta_instset = sndstat_data['i']
        bio_peta_notebytes = data_bytes.to_bytesio(bytes(peta_noteints))

        cvpj_notelists = {}

        for instnum in range(10):
            cvpj_notelists[instnum] = []
            pluginid = plugins.get_id()
            instid = 'petaporon'+str(instnum)
            tracks.r_create_track(cvpj_l, 'instrument', instid, name='Inst #'+str(instnum+1), color=peta_colors[instnum])
            tracks.r_track_pluginid(cvpj_l, instid, pluginid)
            if instnum == 0:
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'square')
                plugins.add_plug_data(cvpj_l, pluginid, 'duty', 2)
                plugins.add_asdr_env(cvpj_l, pluginid, 'vol', 0, 0, 0, 0.1, 0, 0, 1)
            if instnum == 1:
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'square')
                plugins.add_plug_data(cvpj_l, pluginid, 'duty', 2)
                plugins.add_asdr_env(cvpj_l, pluginid, 'vol', 0, 0, 0, 0.1, 0.7, 0, 1)
            if instnum == 2:
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'square')
                plugins.add_plug_data(cvpj_l, pluginid, 'duty', 1)
                plugins.add_asdr_env(cvpj_l, pluginid, 'vol', 0, 0, 0, 0.25, 0, 0, 1)
            if instnum == 3:
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'square')
                plugins.add_plug_data(cvpj_l, pluginid, 'duty', 0)
                plugins.add_asdr_env(cvpj_l, pluginid, 'vol', 0, 0, 0, 0.2, 0, 0, 1)
            if instnum == 4:
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'square')
                plugins.add_plug_data(cvpj_l, pluginid, 'duty', 0)
                plugins.add_asdr_env(cvpj_l, pluginid, 'vol', 0, 0, 0, 0, 1, 0, 1)
            if instnum == 5:
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'triangle')
                plugins.add_plug_data(cvpj_l, pluginid, 'duty', 0)
                plugins.add_asdr_env(cvpj_l, pluginid, 'vol', 0, 0, 0, 0, 1, 0, 1)
            if instnum == 6:
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'triangle')
                plugins.add_plug_data(cvpj_l, pluginid, 'duty', 0)
                plugins.add_asdr_env(cvpj_l, pluginid, 'vol', 0, 0, 0, 0.2, 0, 0, 1)
            if instnum == 7:
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'square')
                plugins.add_plug_data(cvpj_l, pluginid, 'duty', 1)
                plugins.add_asdr_env(cvpj_l, pluginid, 'vol', 0, 0.3, 0, 0.3, 0.2, 0.3, 1)
            if instnum == 8:
                plugins.add_plug(cvpj_l, pluginid, 'retro', 'noise')
                plugins.add_asdr_env(cvpj_l, pluginid, 'vol', 0, 0, 0, 0.4, 0, 0, 1)

        for _ in range(len(peta_noteints)//5):
            partdata = bio_peta_notebytes.read(5)
            peta_note = getval(partdata[0]-35)
            peta_inst = getval(partdata[1]-35)
            peta_len = getval(partdata[2]-35)
            peta_poshigh = getval(partdata[3]-35)
            peta_poslow = getval(partdata[4]-35)
            peta_pos = peta_poslow+(peta_poshigh*94)
            cvpj_notelists[peta_inst].append(note_data.rx_makenote(peta_pos, peta_len, peta_note-12, None, None))

        for instnum in range(10):
            tracks.r_pl_notes(cvpj_l, 'petaporon'+str(instnum), placement_data.nl2pl(cvpj_notelists[instnum]))

        cvpj_l['do_singlenotelistcut'] = True

        cvpj_l['timesig'] = [sndstat_data['c'], 4]
        song.add_param(cvpj_l, 'bpm', sndstat_data['t'])

        return json.dumps(cvpj_l)