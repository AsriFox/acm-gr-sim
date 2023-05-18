#
# Copyright 2023 AsriFox.
#
# SPDX-License-Identifier: GPL-3.0
#

from gnuradio import blocks, dtv, gr

from textwrap import fill
from gnuradio.dvbs2rx import defs, validate

def _adjust_case(standard, frame_size, constellation):
    """Adjust string paramters to the adopted upper/lower case convention"""
    if standard is not None:
        standard = standard.upper()
    if frame_size is not None:
        frame_size = frame_size.lower()
    if constellation is not None:
        constellation = constellation.upper()
    return standard, frame_size, constellation

def translate(standard,
              frame_size,
              code,
              constellation=None,
              rolloff=None,
              pilots=None,
              vl_snr=False):
    """Translate DVB-S2/S2X/T2 parameters to the pybind11 C++ definitions

    Args:
        standard: DVB standard (DVB-S2, DVB-S2X, DVB-T2).
        frame_size: Frame size (normal, medium, short).
        code: LDPC code rate identifier (e.g., 1/4, 1/3, etc.).
        constellation: Constellation (QPSK, 8PSK, 16QAM, etc.).
        rolloff: Roll-off factor.
        pilots: Whether physical layer pilots are enabled.
        vl_snr: DVB-S2X very-low (VL) SNR mode.

    Note:
        Most blocks take the standard, frame size, and LDPC code as
        parameters. In contrast, the constellation, roll-off, and pilots
        parameters are only taken by a few blocks. Such optional parameters are
        only translated and included in the output when the corresponding
        input argument is provided.

    Returns:
        Tuple with the corresponding pybind11 C++ definitions.

    """
    standard, frame_size, constellation = _adjust_case(standard, frame_size, constellation)
    valid = validate(standard, frame_size, code, constellation, rolloff, pilots)
    if (not valid):
        raise ValueError("Invalid {} parameters".format(standard))

    t_standard = eval("dtv." + defs.standards[standard])
    t_frame_size = eval("dtv." + defs.frame_sizes[frame_size])

    # The LDPC code rate definition may depend on the chosen frame size and
    # VL-SNR mode
    code_def = defs.ldpc_codes[code]['def']
    if (isinstance(code_def, list)):
        frame_sizes = defs.ldpc_codes[code]['frame']
        vl_snr_modes = defs.ldpc_codes[code]['vl-snr']

        found = False
        for idx, d in enumerate(code_def):
            if (frame_size == frame_sizes[idx]
                    and vl_snr == vl_snr_modes[idx]):
                found = True
                break
        assert (found)  # It should be found here (_validate guarantees that)
        t_code = eval("dtv." + defs.ldpc_codes[code]['def'][idx])
    else:
        t_code = eval("dtv." + defs.ldpc_codes[code]['def'])

    # Resulting tuple with definitions
    res = (t_standard, t_frame_size, t_code)

    if constellation is not None:
        t_constellation = eval("dtv." +
                               defs.constellations[constellation]['def'])
        res += (t_constellation, )

    if rolloff is not None:
        t_rolloff = eval("dtv." + defs.rolloffs[rolloff]['def'])
        res += (t_rolloff, )

    if pilots is not None:
        t_pilots = eval("dtv." + defs.pilots[bool(pilots)])
        res += (t_pilots, )

    return res


class tx_hier(gr.hier_block2):
    def __init__(self, frame_size='normal', modcod='QPSK_1/4'):
        gr.hier_block2.__init__(self, 
            name='acm_tx_hier', 
            input_signature=gr.io_signature.makev(1, 1, [gr.sizeof_char]),
            output_signature=gr.io_signature.makev(1, 1, [gr.sizeof_gr_complex]))

        ##################################################
        # Parameters
        ##################################################
        self.frame_size = frame_size = frame_size.lower()
        self.modcod = modcod = modcod.upper()

        ##################################################
        # Variables
        ##################################################
        constellation, code_rate = modcod.split('_')
        self.constellation = constellation
        self.code_rate = code_rate
        
        tx_standard, tx_framesize, tx_code_rate, tx_constellation = translate('DVB-S2', frame_size, code_rate, constellation)
        self.tx_standard = tx_standard
        self.tx_framesize = tx_framesize
        self.tx_code_rate = tx_code_rate
        self.tx_constellation = tx_constellation

        ##################################################
        # Blocks
        ##################################################
        self.unpack_bits = blocks.unpack_k_bits_bb(8)
        self.encoder_bch = dtv.dvb_bch_bb(tx_standard, tx_framesize, tx_code_rate)
        self.encoder_ldpc = dtv.dvb_ldpc_bb(tx_standard, tx_framesize, tx_code_rate, tx_constellation)
        self.interleaver = dtv.dvbs2_interleaver_bb(tx_framesize, tx_code_rate, tx_constellation)
        self.modulator = dtv.dvbs2_modulator_bc(tx_framesize, tx_code_rate, tx_constellation, dtv.INTERPOLATION_OFF)

        ##################################################
        # Connections
        ##################################################
        self.connect(
            self,
            self.unpack_bits,
            self.encoder_bch,
            self.encoder_ldpc,
            self.interleaver,
            self.modulator,
            self)
