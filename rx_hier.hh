#ifndef INCLUDED_DVBS2_BER_RX_HIER_H
#define INCLUDED_DVBS2_BER_RX_HIER_H

#include "dvbs2_config.h"
#include <gnuradio/analog/agc_cc.h>
#include <gnuradio/dvbs2rx/bch_decoder_bb.h>
#include <gnuradio/dvbs2rx/dvb_config.h>
#include <gnuradio/dvbs2rx/dvbs2_config.h>
#include <gnuradio/dvbs2rx/ldpc_decoder_cb.h>
#include <gnuradio/dvbs2rx/plsync_cc.h>
#include <gnuradio/dvbs2rx/rotator_cc.h>
#include <gnuradio/dvbs2rx/symbol_sync_cc.h>
#include <gnuradio/hier_block2.h>

class rx_hier : public gr::hier_block2
{
private:
    gr::analog::agc_cc::sptr agc;
    gr::dvbs2rx::rotator_cc::sptr phase_rotator_rx;
    gr::dvbs2rx::symbol_sync_cc::sptr symbol_sync;
    gr::dvbs2rx::plsync_cc::sptr pl_sync;
    gr::dvbs2rx::ldpc_decoder_cb::sptr decoder_ldpc;
    gr::dvbs2rx::bch_decoder_bb::sptr decoder_bch;

public:
    rx_hier(gr::dvbs2acm::dvbs2_modcod_t, gr::dvbs2acm::dvbs2_vlsnr_header_t, int goldcode);
};

#endif /* INCLUDED_DVBS2_BER_TX_HIER_H */