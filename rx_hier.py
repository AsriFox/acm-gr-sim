#
# Copyright 2023 AsriFox.
#
# SPDX-License-Identifier: GPL-3.0
#

from gnuradio import blocks, dvbs2rx, gr

class rx_hier(gr.hier_block2):
    def __init__(self, frame_size='normal', modcod='QPSK_1/4'):
        gr.hier_block2.__init__(self,
            name='acm_rx_hier',
            input_signature=gr.io_signature.makev(1, 1, [gr.sizeof_gr_complex]),
            output_signature=gr.io_signature.makev(1, 1, [gr.sizeof_char]))
        
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
        
        rx_standard, rx_framesize, rx_code_rate, rx_constellation = dvbs2rx.params.translate('DVB-S2', frame_size, code_rate, constellation)
        self.rx_standard = rx_standard
        self.rx_framesize = rx_framesize
        self.rx_code_rate = rx_code_rate
        self.rx_constellation = rx_constellation

        ##################################################
        # Blocks
        ##################################################
        self.decoder_ldpc = dvbs2rx.ldpc_decoder_cb(
            rx_standard, rx_framesize, rx_code_rate, rx_constellation,
            dvbs2rx.OM_MESSAGE, dvbs2rx.INFO_OFF, max_trials=25, debug_level=0)
        self.decoder_bch = dvbs2rx.bch_decoder_bb(
            rx_standard, rx_framesize, rx_code_rate,
            dvbs2rx.OM_MESSAGE, debug_level=0)
        self.pack_bits = blocks.pack_k_bits_bb(8)

        ##################################################
        # Connections
        ##################################################
        self.connect(
            self,
            self.decoder_ldpc,
            self.decoder_bch,
            self.pack_bits,
            self)

    def get_detected_snr(self):
        return self.decoder_ldpc.get_snr()
