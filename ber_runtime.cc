#include "ber_runtime.hh"
#include <chrono>
#include <cmath>
#include <string>

using namespace gr::dtv;
using namespace gr::dvbs2rx;

dvbs2_ber_runtime::dvbs2_ber_runtime(const char* in_file,
                                     double symbol_rate,
                                     double esn0_db,
                                     double freq_shift,
                                     gr::dvbs2acm::dvbs2_modcod_t modcod,
                                     gr::dvbs2acm::dvbs2_vlsnr_header_t vlsnr_header,
                                     int goldcode)
    : gr::top_block("DVB-S2 Tx/Rx Simulation")
{
    // Parameters
    const auto standard = gr::dvbs2rx::STANDARD_DVBS2;
    const auto standard1 = gr::dtv::STANDARD_DVBS2;
    auto framesize1 = (gr::dtv::dvb_framesize_t)framesize;
    auto rate1 = (gr::dtv::dvb_code_rate_t)rate;
    auto constellation1 = (gr::dtv::dvb_constellation_t)constellation;
    auto interpolation = gr::dvbs2rx::INTERPOLATION_OFF;
    auto interpolation1 = gr::dtv::INTERPOLATION_OFF;
    auto pilots = gr::dvbs2rx::PILOTS_ON;
    auto pilots1 = gr::dtv::PILOTS_ON;

    auto agc_gain = 1.0;
    auto agc_rate = 1e-5;
    auto agc_ref = 1.0;
    auto pl_freq_est_period = 20;
    auto rrc_delay = 25;
    auto rrc_nfilts = 128;
    auto sps = 2.0;
    auto sym_sync_damping = 1.0;
    auto sym_sync_loop_bw = 0.0045;
    auto max_trials = 25;

    // auto EsN0 = pow(10, esn0_db / 10);
    auto N0 = pow(10, esn0_db / -10);
    auto samp_rate = symbol_rate * sps;
    auto n_rrc_taps = (int)(2 * rrc_delay * sps) + 1;

    float ro_factor;
    switch (rolloff) {
    case gr::dvbs2rx::RO_0_35:
        ro_factor = 0.35;
        break;
    case gr::dvbs2rx::RO_0_25:
        ro_factor = 0.25;
        break;
    case gr::dvbs2rx::RO_0_20:
        ro_factor = 0.20;
        break;
    case gr::dvbs2rx::RO_0_15:
        ro_factor = 0.15;
        break;
    case gr::dvbs2rx::RO_0_10:
        ro_factor = 0.10;
        break;
    case gr::dvbs2rx::RO_0_05:
        ro_factor = 0.05;
        break;
    case gr::dvbs2rx::RO_RESERVED:
        ro_factor = 0.00;
        break;
    }

    // Make transmitter blocks
    encoder_bch = dvb_bch_bb::make(standard1, framesize1, rate1);
    encoder_ldpc = dvb_ldpc_bb::make(standard1, framesize1, rate1, constellation1);
    interleaver = dvbs2_interleaver_bb::make(framesize1, rate1, constellation1);
    modulator = dvbs2_modulator_bc::make(framesize1, rate1, constellation1, interpolation1);
    pl_framer = dvbs2_physical_cc::make(framesize1, rate1, constellation1, pilots1, goldcode);

    // Make receiver blocks
    agc = gr::analog::agc_cc::make(agc_rate, agc_ref, agc_gain);
    phase_rotator_rx = gr::dvbs2rx::rotator_cc::make();
    symbol_sync = symbol_sync_cc::make(
        sps, sym_sync_loop_bw, sym_sync_damping, ro_factor, rrc_delay, rrc_nfilts, 0);
    pl_sync = plsync_cc::make(
        goldcode, pl_freq_est_period, sps, 0, true, true, 0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF);
    decoder_ldpc = ldpc_decoder_cb::make(standard,
                                         framesize,
                                         rate,
                                         constellation,
                                         gr::dvbs2rx::OM_MESSAGE,
                                         gr::dvbs2rx::INFO_OFF,
                                         max_trials);
    decoder_bch = bch_decoder_bb::make(standard, framesize, rate, gr::dvbs2rx::OM_MESSAGE);

    // Make channel blocks
    auto taps =
        gr::filter::firdes::root_raised_cosine(sps, samp_rate, symbol_rate, ro_factor, n_rrc_taps);
    fir_filter = gr::filter::interp_fir_filter_ccf::make((int)(sps / 2), taps);
    doppler_freq_shift = gr::blocks::rotator_cc::make(2.0 * M_PI * freq_shift / samp_rate);
    channel_noise = gr::analog::fastnoise_source_c::make(noise_type, sqrt(N0 * sps));
    noise_add = gr::blocks::add_cc::make();

    // Make framework blocks
    file_src = gr::blocks::file_source::make(sizeof(unsigned char), in_file);
    throttle_sym = gr::blocks::throttle::make(1, samp_rate);
    unpack_bits = gr::blocks::unpack_k_bits_bb::make(8);
    pack_bits = gr::blocks::pack_k_bits_bb::make(8);
    ber = gr::fec::ber_bf::make();
    ber_sink = gr::blocks::file_sink::make(sizeof(unsigned char), "/dev/stdout", true);

    // Connect all blocks and build a flowgraph
    connect(file_src, 0, ber, 0);
    connect(file_src, 0, unpack_bits, 0);
    connect(unpack_bits, 0, encoder_bch, 0);
    connect(encoder_bch, 0, encoder_ldpc, 0);
    connect(encoder_ldpc, 0, interleaver, 0);
    connect(interleaver, 0, modulator, 0);
    connect(modulator, 0, pl_framer, 0);
    connect(pl_framer, 0, fir_filter, 0);
    connect(fir_filter, 0, doppler_freq_shift, 0);
    connect(doppler_freq_shift, 0, noise_add, 0);
    connect(channel_noise, 0, noise_add, 1);
    connect(noise_add, 0, throttle_sym, 0);
    connect(throttle_sym, 0, agc, 0);
    connect(agc, 0, phase_rotator_rx, 0);
    connect(phase_rotator_rx, 0, symbol_sync, 0);
    connect(symbol_sync, 0, pl_sync, 0);
    msg_connect(pl_sync, "rotator_phase_inc", phase_rotator_rx, "cmd");
    connect(pl_sync, 0, decoder_ldpc, 0);
    connect(decoder_ldpc, 0, decoder_bch, 0);
    connect(decoder_bch, 0, pack_bits, 0);
    connect(pack_bits, 0, ber, 1);
    connect(ber, 0, ber_sink, 0);
}