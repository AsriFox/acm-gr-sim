#include "modcod.hh"
#include "tx_hier.hh"
#include <gnuradio/filter/firdes.h>

using namespace gr::dtv;

tx_hier::tx_hier(gr::dvbs2acm::dvbs2_modcod_t modcod,
                 gr::dvbs2acm::dvbs2_vlsnr_header_t vlsnr_header,
                 int goldcode)
{
    const auto standard = gr::dtv::STANDARD_DVBS2;
    auto framesize = (dvbs2_framesize_t)modcod_framesize(modcod);
    auto rate = (dvbs2_code_rate_t)modcod_rate(modcod);
    auto interpolation = gr::dtv::INTERPOLATION_OFF;
    auto pilots = gr::dtv::PILOTS_ON;
}