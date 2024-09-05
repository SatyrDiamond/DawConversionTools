# SPDX-FileCopyrightText: 2024 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import plugins

import os
import math
from functions import extpluglog

class plugconv(plugins.base):
	def __init__(self): pass
	def is_dawvert_plugin(self): return 'plugconv'
	def getplugconvinfo(self, plugconv_obj): 
		plugconv_obj.in_plugins = [['native-lmms', None]]
		plugconv_obj.in_daws = ['lmms']
		plugconv_obj.out_plugins = [['native-flstudio', None]]
		plugconv_obj.out_daws = ['flp']
		
	def convert(self, convproj_obj, plugin_obj, pluginid, dv_config):
		if plugin_obj.type.subtype == 'stereomatrix':  
			extpluglog.convinternal('LMMS', 'Stereo Matrix', 'FL Studio', 'Fruity Stereo Shaper')
			plugin_obj.plugts_transform('./data_main/plugts/lmms_flstudio.pltr', 'stereomatrix', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.subtype == 'spectrumanalyzer':  
			extpluglog.convinternal('LMMS', 'Spectrum Analyzer', 'FL Studio', 'Fruity Spectroman')
			plugin_obj.plugts_transform('./data_main/plugts/lmms_flstudio.pltr', 'spectrumanalyzer', convproj_obj, pluginid)
			return 0

		if plugin_obj.type.subtype == 'stereoenhancer':  
			extpluglog.convinternal('LMMS', 'Stereo Enhancer', 'FL Studio', 'Fruity Stereo Enhancer')
			plugin_obj.plugts_transform('./data_main/plugts/lmms_flstudio.pltr', 'stereoenhancer', convproj_obj, pluginid)
			return 0

		return 2
