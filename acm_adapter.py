#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2023 AsriFox.
#
# SPDX-License-Identifier: GPL-3.0-or-later
#

from numpy import uint8
from gnuradio import gr
import dvbs2
import pmt

class acm_adapter(gr.sync_block):
    """
    Provide stream tags for DVB-S2 VCM blocks.
    """
    def __init__(self, 
        framesize=dvbs2.FECFRAME_NORMAL, 
        rate=dvbs2.C1_4, 
        constellation=dvbs2.MOD_QPSK, 
        pilots=dvbs2.PILOTS_ON, 
        goldcode=0, 
        rolloff=dvbs2.RO_0_20):
        
        gr.sync_block.__init__(self,
            name="acm_adapter",
            in_sig=[uint8],
            out_sig=[uint8])
        
        self.framesize = framesize
        self.rate = rate
        self.constellation = constellation
        self.pilots = pilots
        
        if goldcode < 0 or goldcode > 262141:
            gr.log.warn("Gold Code must be between 0 and 262141 inclusive.")
            gr.log.warn("Gold Code set to 0.")
            goldcode = 0
        self.root_code = acm_adapter.gold_to_root(goldcode)

        if framesize == dvbs2.FECFRAME_NORMAL:
            match rate:
                case dvbs2.C1_4:
                    self.kbch = kbch = 16008
                case dvbs2.C1_3:
                    self.kbch = kbch = 21408
                case dvbs2.C2_5:
                    self.kbch = kbch = 25728
                case dvbs2.C1_2:
                    self.kbch = kbch = 32208
                case dvbs2.C3_5:
                    self.kbch = kbch = 38688
                case dvbs2.C2_3:
                    self.kbch = kbch = 43040
                case dvbs2.C3_4:
                    self.kbch = kbch = 48408
                case dvbs2.C4_5:
                    self.kbch = kbch = 51648
                case dvbs2.C5_6:
                    self.kbch = kbch = 53840
                case dvbs2.C8_9:
                    self.kbch = kbch = 57472
                case dvbs2.C9_10:
                    self.kbch = kbch = 58192
                case dvbs2.C2_9_VLSNR:
                    self.kbch = kbch = 14208
                case dvbs2.C13_45:
                    self.kbch = kbch = 18528
                case dvbs2.C9_20:
                    self.kbch = kbch = 28968
                case dvbs2.C90_180:
                    self.kbch = kbch = 32208
                case dvbs2.C96_180:
                    self.kbch = kbch = 34368
                case dvbs2.C11_20:
                    self.kbch = kbch = 35448
                case dvbs2.C100_180:
                    self.kbch = kbch = 35808
                case dvbs2.C104_180:
                    self.kbch = kbch = 37248
                case dvbs2.C26_45:
                    self.kbch = kbch = 37248
                case dvbs2.C18_30:
                    self.kbch = kbch = 38688
                case dvbs2.C28_45:
                    self.kbch = kbch = 40128
                case dvbs2.C23_36:
                    self.kbch = kbch = 41208
                case dvbs2.C116_180:
                    self.kbch = kbch = 41568
                case dvbs2.C20_30:
                    self.kbch = kbch = 43008
                case dvbs2.C124_180:
                    self.kbch = kbch = 44448
                case dvbs2.C25_36:
                    self.kbch = kbch = 44808
                case dvbs2.C128_180:
                    self.kbch = kbch = 45888
                case dvbs2.C13_18:
                    self.kbch = kbch = 46608
                case dvbs2.C132_180:
                    self.kbch = kbch = 47328
                case dvbs2.C22_30:
                    self.kbch = kbch = 47328
                case dvbs2.C135_180:
                    self.kbch = kbch = 48408
                case dvbs2.C140_180:
                    self.kbch = kbch = 50208
                case dvbs2.C7_9:
                    self.kbch = kbch = 50208
                case dvbs2.C154_180:
                    self.kbch = kbch = 55248
                case _:
                    self.kbch = kbch = 0
        elif framesize == dvbs2.FECFRAME_SHORT:
            match rate:
                case dvbs2.C1_4:
                    self.kbch = kbch = 3072
                case dvbs2.C1_3:
                    self.kbch = kbch = 5232
                case dvbs2.C2_5:
                    self.kbch = kbch = 6312
                case dvbs2.C1_2:
                    self.kbch = kbch = 7032
                case dvbs2.C3_5:
                    self.kbch = kbch = 9552
                case dvbs2.C2_3:
                    self.kbch = kbch = 10632
                case dvbs2.C3_4:
                    self.kbch = kbch = 11712
                case dvbs2.C4_5:
                    self.kbch = kbch = 12432
                case dvbs2.C5_6:
                    self.kbch = kbch = 13152
                case dvbs2.C8_9:
                    self.kbch = kbch = 14232
                case dvbs2.C11_45:
                    self.kbch = kbch = 3792
                case dvbs2.C4_15:
                    self.kbch = kbch = 4152
                case dvbs2.C14_45:
                    self.kbch = kbch = 4872
                case dvbs2.C7_15:
                    self.kbch = kbch = 7392
                case dvbs2.C8_15:
                    self.kbch = kbch = 8472
                case dvbs2.C26_45:
                    self.kbch = kbch = 9192
                case dvbs2.C32_45:
                    self.kbch = kbch = 11352
                case dvbs2.C1_5_VLSNR_SF2:
                    self.kbch = kbch = 2512
                case dvbs2.C11_45_VLSNR_SF2:
                    self.kbch = kbch = 3792
                case dvbs2.C1_5_VLSNR:
                    self.kbch = kbch = 3072
                case dvbs2.C4_15_VLSNR:
                    self.kbch = kbch = 4152
                case dvbs2.C1_3_VLSNR:
                    self.kbch = kbch = 5232
                case _:
                    self.kbch = kbch = 0
        else:
            match rate:
                case dvbs2.C1_5_MEDIUM:
                    self.kbch = kbch = 5660
                case dvbs2.C11_45_MEDIUM:
                    self.kbch = kbch = 7740
                case dvbs2.C1_3_MEDIUM:
                    self.kbch = kbch = 10620
                case _:
                    self.kbch = kbch = 0

        self.set_output_multiple(kbch)

    def gold_to_root(goldcode: int):
        x = 1
        for g in range(goldcode):
            x = (((x ^ (x >> 7)) & 1) << 17) | (x >> 1)
        return x

    def work(self, input_items, output_items):
        in0 = input_items[0]
        out = output_items[0]
        
        tagoffset = self.nitems_written(0);
        tagmodcod = (int(self.root_code) << 32) | (int(self.pilots) << 24) | (int(self.constellation) << 16) | (int(self.rate) << 8) | (int(self.framesize) << 1) | int(0)
        key = pmt.string_to_symbol("modcod")
        value = pmt.from_uint64(tagmodcod)
        self.add_item_tag(0, tagoffset, key, value)

        out[:] = in0
        return len(output_items[0])
