#include "ber_runtime.hh"
#include <chrono>
#include <cmath>

dvbs2_ber_runtime::dvbs2_ber_runtime(double symbol_rate)
    : gr::top_block("gr_dvbs2_ber") {
  int seed = std::chrono::system_clock::now().time_since_epoch().count();
  random_src = gr::analog::random_uniform_source_b::make(0, UINT8_MAX, seed);
  throttle_src = gr::blocks::throttle::make(1, symbol_rate / 8);
  ber_sink = gr::blocks::null_sink::make(sizeof(unsigned char));

  connect(random_src, 0, throttle_src, 0);
  connect(throttle_src, 0, ber_sink, 0);
}