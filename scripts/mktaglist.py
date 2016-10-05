# -*- coding: utf-8 -*-
#
#===============================================================================
#
# Taglist Generator
#
# This script generates taglist.yaml files in Mopy\Bashed Patches\Oblivion and
# Mopy\Bashed Patches\Skyrim using the LOOT API and source masterlists. The
# masterlists must be named "masterlist.txt" or "masterlist.yaml" and put in the
# folders mentioned above, or be present in a LOOT install that was installed
# using its installer.
# To generate the taglist for a game, you must have the game installed. This
# script will generate taglists for all detected games.
#
# Usage:
#   mktaglist.py
#
#===============================================================================

import sys
import os
import _winreg
from collections import OrderedDict

sys.path.append('../Mopy/bash/compiled')

import loot_api

games_info = OrderedDict([(u'Oblivion', None), (u'Skyrim', None),
                          (u'Fallout3', None), (u'FalloutNV', None),
                          (u'Fallout4', None),
                          ])

# Detect games.
for g in games_info:
    try:
        reg_key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
            u'Software\\Bethesda Softworks\\%s' % g, 0,
            _winreg.KEY_READ | _winreg.KEY_WOW64_32KEY)
    except OSError as e:
        if e.errno == 2: continue # The system cannot find the file specified
    value = _winreg.QueryValueEx(reg_key, u'Installed Path')
    if value[1] == _winreg.REG_SZ and os.path.exists(value[0]):
        games_info[g] = value[0]
        print u'Found %s.' % g


# Detect LOOT masterlists' installation path in AppData/Local
localAppData = os.path.join(os.environ["LOCALAPPDATA"], 'LOOT')
if not os.path.exists(localAppData):
    raise Exception("No LOOT masterlists install found in %s" % localAppData)

# Detect masterlists
for g, app_dir in games_info.iteritems():
    if app_dir is not None and os.path.exists(os.path.join(localAppData, g)):
        games_info[g] = (
            app_dir, os.path.join(localAppData, g, 'masterlist.yaml'))

print u'Loaded the LOOT API v%s using wrapper version %s' % (loot_api.Version.string(), loot_api.WrapperVersion.string())

loot_codes = dict(zip(games_info.keys(), (
    loot_api.GameType.tes4,
    loot_api.GameType.tes5,
    loot_api.GameType.fo3,
    loot_api.GameType.fonv,
    loot_api.GameType.fo4,
)))

for game, info in games_info.iteritems():
    if info is None: continue
    print u'Getting masterlist from %s' % info[1]
    taglistDir = u'../Mopy/Bash Patches/%s/taglist.yaml' % game
    # taglistDir = u'../%s - taglist.yaml' % game
    if os.path.exists(info[1]):
        lootDb = loot_api.create_database(loot_codes[game], info[0])
        lootDb.load_lists(info[1])
        lootDb.write_minimal_list(taglistDir, True)
        print u'%s masterlist converted.' % game
    else:
        print u'Error: %s masterlist not found.' % game

print u'Taglist generator finished.'

raw_input(u'Done')
