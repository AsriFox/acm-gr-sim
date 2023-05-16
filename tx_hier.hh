#ifndef INCLUDED_DVBS2_BER_TX_HIER_H
#define INCLUDED_DVBS2_BER_TX_HIER_H

#include "dvbs2_config.h"
#include <gnuradio/dtv/dvb_bch_bb.h>
#include <gnuradio/dtv/dvb_ldpc_bb.h>
#include <gnuradio/dtv/dvbs2_interleaver_bb.h>
#include <gnuradio/dtv/dvbs2_modulator_bc.h>
#include <gnuradio/dtv/dvbs2_physical_cc.h>
#include <gnuradio/filter/interp_fir_filter.h>
#include <gnuradio/hier_block2.h>

class tx_hier : public gr::hier_block2
{
private:
    gr::dtv::dvb_bch_bb::sptr encoder_bch;
    gr::dtv::dvb_ldpc_bb::sptr encoder_ldpc;
    gr::dtv::dvbs2_interleaver_bb::sptr interleaver;
    gr::dtv::dvbs2_modulator_bc::sptr modulator;
    gr::dtv::dvbs2_physical_cc::sptr pl_framer;
    gr::filter::interp_fir_filter_ccf::sptr fir_filter;

public:
    tx_hier(gr::dvbs2acm::dvbs2_modcod_t, gr::dvbs2acm::dvbs2_vlsnr_header_t, int goldcode);
};

#endif /* INCLUDED_DVBS2_BER_TX_HIER_H */