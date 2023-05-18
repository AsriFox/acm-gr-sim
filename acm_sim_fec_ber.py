#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: DVB-S2 FEC BER
# Description: DVB-S2 BCH/LDPC BER Simulation
# GNU Radio version: 3.10.1.1

from gnuradio import analog, blocks, dtv, fec, gr
from gnuradio import dvbs2rx
import tx_params
from math import sqrt
import threading, time

class acm_sim_fec_ber(gr.top_block):
    def __init__(self, sym_rate=1000000, esn0_db=0, frame_size='normal', modcod='QPSK_1/4', test_size=2000000):
        gr.top_block.__init__(self, 'DVB-S2 ACM Simulaion', catch_exceptions=True)

        ##################################################
        # Parameters
        ##################################################
        self.sym_rate = sym_rate
        self.esn0_db = esn0_db
        self.frame_size = frame_size = frame_size.lower()
        self.modcod = modcod = modcod.upper()
        self.test_size = test_size

        ##################################################
        # Variables
        ##################################################
        constellation, code_rate = modcod.split('_')
        self.constellation = constellation
        self.code_rate = code_rate
        self.N0 = N0 = 10 ** (-0.1 * esn0_db)
        self.ber = 0

        tx_standard, tx_framesize, tx_code_rate, tx_constellation = tx_params.translate('DVB-S2', frame_size, code_rate, constellation)
        self.tx_standard = tx_standard
        self.tx_framesize = tx_framesize
        self.tx_code_rate = tx_code_rate
        self.tx_constellation = tx_constellation

        rx_standard, rx_framesize, rx_code_rate, rx_constellation = dvbs2rx.params.translate('DVB-S2', frame_size, code_rate, constellation)
        self.rx_standard = rx_standard
        self.tx_framesize = rx_framesize
        self.rx_code_rate = rx_code_rate
        self.rx_constellation = rx_constellation


        ##################################################
        # Blocks
        ##################################################
        self.random_source = analog.random_uniform_source_b(0, 256, 0)
        self.test_limiter = blocks.head(gr.sizeof_char*1, test_size)
        self.unpack_bits = blocks.unpack_k_bits_bb(8)

        self.encoder_bch = dtv.dvb_bch_bb(tx_standard, tx_framesize, tx_code_rate)
        self.encoder_ldpc = dtv.dvb_ldpc_bb(tx_standard, tx_framesize, tx_code_rate, tx_constellation)
        self.interleaver = dtv.dvbs2_interleaver_bb(tx_framesize, tx_code_rate, tx_constellation)
        self.modulator = dtv.dvbs2_modulator_bc(tx_framesize, tx_code_rate, tx_constellation, dtv.INTERPOLATION_OFF)

        self.noise_source = analog.fastnoise_source_c(analog.GR_GAUSSIAN, sqrt(N0), 0, 8192)
        self.add_noise = blocks.add_cc()
        self.throttle = blocks.throttle(gr.sizeof_gr_complex*1, sym_rate, ignore_tags=True)

        self.decoder_ldpc = dvbs2rx.ldpc_decoder_cb(
            rx_standard, rx_framesize, rx_code_rate, rx_constellation,
            dvbs2rx.OM_MESSAGE, dvbs2rx.INFO_OFF, max_trials=25, debug_level=0)
        self.decoder_bch = dvbs2rx.bch_decoder_bb(
            rx_standard, rx_framesize, rx_code_rate,
            dvbs2rx.OM_MESSAGE, debug_level=0)

        self.pack_bits = blocks.pack_k_bits_bb(8)
        self.count_ber = fec.ber_bf(False, 100, -7.0)
        self.probe_ber = blocks.probe_signal_f()
        def _ber_probe():
            while True:
                val = self.probe_ber.level()
                try:
                    try:
                        self.doc.add_next_tick_callback(functools.partial(self.set_ber, val))
                    except AttributeError:
                        self.set_ber(val)
                except AttributeError:
                    pass
                time.sleep(1.0)
        _ber_thread = threading.Thread(target=_ber_probe)
        _ber_thread.daemon = True
        _ber_thread.start()

        self.probe_rate = blocks.probe_rate(gr.sizeof_char*1, 10.0, 0.15)
        # self.print_rate = blocks.message_debug()

        ##################################################
        # Connections
        ##################################################
        self.connect(
            (self.random_source, 0),
            (self.test_limiter, 0), 
            (self.unpack_bits, 0), 
            (self.encoder_bch, 0),
            (self.encoder_ldpc, 0),
            (self.interleaver, 0),
            (self.modulator, 0),
            (self.add_noise, 0)
        )
        self.connect((self.noise_source, 0), (self.add_noise, 1))
        self.connect(
            (self.add_noise, 0), 
            (self.throttle, 0),
            (self.decoder_ldpc, 0),
            (self.decoder_bch, 0),
            (self.pack_bits, 0),
            (self.count_ber, 1)
        )
        self.connect((self.test_limiter, 0), (self.count_ber, 0))
        self.connect((self.count_ber, 0), (self.probe_ber, 0))
        self.connect((self.unpack_bits, 0), (self.probe_rate, 0))
        # self.msg_connect((self.probe_rate, 'rate'), (self.print_rate, 'print'))

    def get_modcod(self):
        return self.modcod

    def get_detected_snr(self):
        return self.decoder_ldpc.get_snr()

    def get_ber(self):
        return self.ber

    def set_ber(self, ber):
        self.ber = ber

    def get_rate(self):
        return self.probe_rate.rate()


if __name__ == '__main__':
    from argparse import ArgumentParser
    from gnuradio.eng_arg import eng_float, intx
    from gnuradio import eng_notation

    parser = ArgumentParser(description='DVB-S2 BCH/LDPC BER Simulation')
    parser.add_argument(
        "--esn0-db", dest="esn0_db", type=eng_float, default=eng_notation.num_to_str(0.0),
        help="Set SNR (or Es/N0) in dB [default=%(default)r]")
    parser.add_argument(
        "-f", "--frame-size", dest="frame_size", type=str, default='normal',
        help="Set FECFRAME size [default=%(default)r]")
    parser.add_argument(
        "-m", "--modcod", dest="modcod", type=str, default='QPSK_1/4',
        help="Set MODCOD [default=%(default)r]")
    parser.add_argument(
        "-r", "--sym-rate", dest="sym_rate", type=intx, default=20000000,
        help="Set symbol rate in baud [default=%(default)r]")
    parser.add_argument(
        "-t", "--test-size", dest="test_size", type=intx, default=20000000,
        help="Set test size in symbols [default=%(default)r]")

    options = parser.parse_args()
    tb = acm_sim_fec_ber(
        sym_rate=options.sym_rate, 
        esn0_db=options.esn0_db, 
        frame_size=options.frame_size, 
        modcod=options.modcod,
        test_size=options.test_size)

    import sys, signal
    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()
        print()
        print('Detected SNR: ' + str(tb.get_detected_snr()))
        print('Throughput: ' + str(tb.get_rate()))
        print('BER: ' + str(tb.get_ber()))
        sys.exit(0)
    
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    tb.start()
    tb.wait()
    print()
    print('Detected SNR: ' + str(tb.get_detected_snr()))
    print('Throughput: ' + str(tb.get_rate()))
    print('BER: ' + str(tb.get_ber()))
