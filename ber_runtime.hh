#ifndef INCLUDED_DVBS2_BER_RUNTIME_H
#define INCLUDED_DVBS2_BER_RUNTIME_H

#include "rx_hier.hh"
#include "tx_hier.hh"

#include "dvbs2_config.h"
#include <gnuradio/analog/agc_cc.h>
#include <gnuradio/analog/fastnoise_source.h>
#include <gnuradio/analog/noise_type.h>
#include <gnuradio/analog/random_uniform_source.h>
#include <gnuradio/blocks/add_blk.h>
#include <gnuradio/blocks/file_sink.h>
#include <gnuradio/blocks/file_source.h>
#include <gnuradio/blocks/null_sink.h>
#include <gnuradio/blocks/pack_k_bits_bb.h>
#include <gnuradio/blocks/rotator_cc.h>
#include <gnuradio/blocks/throttle.h>
#include <gnuradio/blocks/unpack_k_bits.h>
#include <gnuradio/blocks/unpack_k_bits_bb.h>
#include <gnuradio/fec/ber_bf.h>
#include <gnuradio/top_block.h>

class dvbs2_ber_runtime : public gr::top_block
{
    const gr::analog::noise_type_t noise_type = gr::analog::GR_GAUSSIAN;

private:
    tx_hier transmitter;
    rx_hier receiver;

    // Channel
    gr::blocks::rotator_cc::sptr doppler_freq_shift;
    gr::analog::fastnoise_source_c::sptr channel_noise;
    gr::blocks::add_cc::sptr noise_add;

    // BER Framework
    gr::blocks::file_source::sptr file_src;
    gr::blocks::unpack_k_bits_bb::sptr unpack_bits;
    gr::blocks::pack_k_bits_bb::sptr pack_bits;
    gr::fec::ber_bf::sptr ber;
    gr::blocks::throttle::sptr throttle_sym;
    gr::blocks::file_sink::sptr ber_sink;

public:
    dvbs2_ber_runtime(const char* in_file,
                      double symbol_rate,
                      double esn0_db,
                      double freq_shift,
                      gr::dvbs2acm::dvbs2_modcod_t,
                      gr::dvbs2acm::dvbs2_vlsnr_header_t,
                      int goldcode);
};

#endif /* INCLUDED_DVBS2_BER_RUNTIME_H */