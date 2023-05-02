# Copyright 2018 Jonathan McDowell <noodles@earth.li>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from enum import Enum

import urllib.request

# Must send these headers to not be ignored
HEADERS = {'User-Agent': 'MEI-LAN-REMOTE-CALL'}
# Known key commands
KEYS = ['POWER', 'OP_CL',
        'PLAYBACK', 'PAUSE', 'STOP', 'SKIPFWD', 'SKIPREV', 'REV',
        'D0', 'D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'D9', 'D12',
        'SHARP',  # '#'
        'CLEAR',  # '*' /  CANCEL
        'UP', 'DOWN', 'LEFT', 'RIGHT', 'SELECT', 'RETURN', 'EXIT',
        'MLTNAVI',          # HOME
        'DSPSEL',           # STATUS
        'TITLE', 'MENU', 'PUPMENU',
        'SHFWD1', 'SHFWD2', 'SHFWD3', 'SHFWD4', 'SHFWD5',
        'SHREV1', 'SHREV2', 'SHREV3', 'SHREV4', 'SHREV5',
        'JLEFT', 'JRIGHT',
        'RED', 'BLUE', 'GREEN', 'YELLOW',
        'NETFLIX', 'SKYPE', 'V_CAST', '3D', 'NETWORK', 'AUDIOSEL',
        'KEYS', 'CUE', 'CHROMA',
        'MNBACK', 'MNSKIP', '2NDARY', 'PICTMD', 'DETAIL', 'RESOLUTN',
        # Playback view?
        'OSDONOFF', 'P_IN_P',
        ]


class PlayerVariant(Enum):
    AUTO = 1
    BD = 2
    UB = 3


class PanasonicBD:
    """Class to interact with Panasonic Blu-Ray Players."""

    def __init__(self, host, variant=PlayerVariant.AUTO):
        self._host = host
        self._state = None
        self._duration = 0
        self._variant = variant

    def send_cmd(self, url, data):
        req = urllib.request.Request(url, data, HEADERS)
        try:
            response = urllib.request.urlopen(req, timeout=5)
        except OSError:
            # If we can't reach the device, assume it's off
            self._state = 'off'
            return ['off', None]

        result = response.read().split(b'\r\n')

        # First line is '00, "", 1' on success.
        # Error response starts with FE, then some binary data
        if result[0].split(b',')[0] != b'00':
            return ['error', None]

        return ['ok', result[1].decode().split(',')]

    def send_key(self, key):
        """ Send the supplied keypress to the device """
        # Sanity check it's a valid key
        if key not in KEYS:
            return ['error', None]

        # Check the player supports it
        if self._variant == PlayerVariant.UB:
            return ['error', None]

        url = 'http://%s/WAN/%s/%s_ctrl.cgi' % (self._host, 'dvdr', 'dvdr')
        data = ('cCMD_RC_%s.x=100&cCMD_RC_%s.y=100' % (key, key)).encode()

        resp = self.send_cmd(url, data)
        # If we're auto-detecting player type then assume we're an newer UB
        # variant if we got an error, and an older BD if it worked
        if self._variant == PlayerVariant.AUTO:
            if resp[0] == 'error':
                self._variant = PlayerVariant.UB
                return ['error', None]
            else:
                self._variant = PlayerVariant.BD

        return resp

    def get_status(self):
        # Check the player supports it, return a dummy response if not
        if self._variant == PlayerVariant.UB:
            return ['1', '0', '0', '00000000', '0']

        url = 'http://%s/WAN/%s/%s_ctrl.cgi' % (self._host, 'dvdr', 'dvdr')
        data = b'cCMD_GET_STATUS.x=100&cCMD_GET_STATUS.y=100'

        resp = self.send_cmd(url, data)
        if resp[0] == 'error':
            # If we got an error and we're auto-detecting player type assume
            # it's a more modern UB
            if self._variant == PlayerVariant.AUTO:
                self._variant = PlayerVariant.UB
                return ['1', '0', '0', '00000000', '0']
            else:
                return ['error']

        # If we get here and we're still auto-detecting player type we can
        # assume an older BD variant.
        if self._variant == PlayerVariant.AUTO:
            self._variant = PlayerVariant.BD

        if resp[0] == 'off':
            return ['off']

        # Response is of the form:
        #  2,0,0,248,0,1,8,2,0,00000000
        #
        # 0: 0 == standby, playing or paused / 2 == stopped or menu
        # 3: Playing time
        # 4: Total time

        return resp[1]

    def get_play_status(self):
        url = 'http://%s/WAN/%s/%s_ctrl.cgi' % (self._host, 'dvdr', 'dvdr')
        data = b'cCMD_PST.x=100&cCMD_PST.y=100'

        resp = self.send_cmd(url, data)
        if resp[0] == 'off':
            self._state = 'off'
            return ['off', 0, 0]
        elif resp[0] == 'error':
            return ['error', 0, 0]

        # Needed for title length + standby/idle status
        status = self.get_status()
        if status[0] == 'off':
            self._state = 'off'
            return ['off', 0, 0]
        elif status[0] == 'error':
            return ['error', 0, 0]

        # State response is of the form
        #  ['0', '0', '0', '00000000']
        #   0: State (0 == stopped / 1 == playing / 2 == paused)
        #   1: Playing time (-2 for no disc?)
        # 2/3: Unknown

        state = resp[1]
        if state[0] == '0':
            # Stopped is reported when in standby mode as well, so we have
            # to use the additional status query to work out which state we are
            # in.
            if status[0] == '0':
                self._state = 'standby'
            else:
                self._state = 'stopped'
        elif state[0] == '1':
            self._state = 'playing'
        elif state[0] == '2':
            self._state = 'paused'
        else:
            self._state = 'unknown'

        return [self._state, int(state[1]), int(status[4])]
