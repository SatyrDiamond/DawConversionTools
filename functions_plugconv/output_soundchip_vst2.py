# SPDX-FileCopyrightText: 2023 SatyrDiamond
# SPDX-License-Identifier: GPL-3.0-or-later

import pathlib

from functions import audio_wav
from functions import list_vst
from functions import vst_inst

from functions_plugparams import data_vc2xml

def convert_inst(instdata, out_daw):
	pluginname = instdata['plugin']
	plugindata = instdata['plugindata']

	if pluginname == 'opn2':
		xmlout = vst_inst.opnplug_convert(plugindata)
		list_vst.replace_data(instdata, 2, 'any', 'OPNplug', 'raw', data_vc2xml.make(xmlout), None)
