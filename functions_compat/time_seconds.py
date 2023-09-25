# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

from functions import params

def step2sec(i_value, i_bpm): return (i_value/8)*(120/i_bpm)
def sec2step(i_value, i_bpm): return (i_value*8)/(120/i_bpm)

def do_placements(cvpj_placements, i_bpm, i_is_seconds):
    if i_is_seconds == True:
        for cvpj_placement in cvpj_placements:
            if 'position' in cvpj_placement: cvpj_placement['position'] = step2sec(cvpj_placement['position'], i_bpm)
            if 'duration' in cvpj_placement: cvpj_placement['duration'] = step2sec(cvpj_placement['duration'], i_bpm)
    else:
        for cvpj_placement in cvpj_placements:
            if 'position' in cvpj_placement: cvpj_placement['position'] = sec2step(cvpj_placement['position'], i_bpm)
            if 'duration' in cvpj_placement: cvpj_placement['duration'] = sec2step(cvpj_placement['duration'], i_bpm)

def process_all(s_track_pl, i_bpm, i_is_seconds):
    if 'notes' in s_track_pl: do_placements(s_track_pl['notes'], i_bpm, i_is_seconds)
    if 'audio' in s_track_pl: do_placements(s_track_pl['audio'], i_bpm, i_is_seconds)
    if 'placements_notes' in s_track_pl: do_placements(s_track_pl['placements_notes'], i_bpm, i_is_seconds)
    if 'placements_audio' in s_track_pl: do_placements(s_track_pl['placements_audio'], i_bpm, i_is_seconds)

def process(cvpj_l, cvpj_type, i_is_seconds):
    bpm = params.get(cvpj_l, [], 'bpm', 120)[0]
    print('[compat] Beats/Seconds: BPM:', bpm)

    if cvpj_type in ['r', 'ri', 'c']:
        if 'track_placements' in cvpj_l:
            for id_track_pl in cvpj_l['track_placements']:
                s_track_pl = cvpj_l['track_placements'][id_track_pl]
                process_all(s_track_pl, bpm, i_is_seconds)

    if cvpj_type in ['m', 'mi']:
        for playlist_id in cvpj_l['playlist']:
            playlist_id_data = cvpj_l['playlist'][playlist_id]
            process_all(playlist_id_data, bpm, i_is_seconds)