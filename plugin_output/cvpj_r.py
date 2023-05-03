# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_output
import json
from functions import placements

class output_cvpj_f(plugin_output.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'output'
    def getname(self): return 'DEBUG'
    def getshortname(self): return 'cvpj_r'
    def gettype(self): return 'r'
    def plugin_archs(self): return None
    def getdawcapabilities(self): 
        return {
        'fxrack': True,
        'r_track_lanes': False,
        'no_pl_auto': False,
        'pl_audio_events': False,
        }
    def parse(self, convproj_json, output_file):
        projJ = json.loads(convproj_json)

        with open(output_file, "w") as fileout:
            fileout.write("CONVPROJ___R\n")
            json.dump(projJ, fileout, indent=4, sort_keys=True)