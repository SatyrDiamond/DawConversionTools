# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugin_plugconv

import struct
import math
from functions_plugparams import params_vital
from functions import plugin_vst2

class plugconv(plugin_plugconv.base):
    def __init__(self): pass
    def is_dawvert_plugin(self): return 'plugconv'
    def getplugconvinfo(self): return ['native-piyopiyo', None, 'piyopiyo'], ['vst2', None, None], True, False
    def convert(self, cvpj_l, pluginid, plugintype, extra_json):
        print('[plug-conv] Converting PiyoPiyo to Vital:',pluginid)
        params_vital.create()
        params_vital.setvalue('osc_1_on', 1)
        params_vital.setvalue('osc_1_level', 0.5)
        params_vital.setvalue('volume', 4000)
        params_vital.setvalue_timed('env_1_release', 20)
        params_vital.importcvpj_wave(cvpj_l, pluginid, 1, None)

        params_vital.importcvpj_env_block(cvpj_l, pluginid, 1, 'vol')
        params_vital.importcvpj_env_points(cvpj_l, pluginid, 1, 'vol')

        params_vital.set_modulation(1, 'lfo_1', 'osc_1_level', 1, 0, 1, 0, 0)
        vitaldata = params_vital.getdata()
        plugin_vst2.replace_data(cvpj_l, pluginid, 'name','any', 'Vital', 'chunk', vitaldata.encode('utf-8'), None)
        return True