#ifndef DVBS2_BER_RUNTIME
#define DVBS2_BER_RUNTIME

#include <gnuradio/analog/noise_type.h>
#include <gnuradio/analog/random_uniform_source.h>
#include <gnuradio/blocks/null_sink.h>
#include <gnuradio/blocks/throttle.h>
#include <gnuradio/top_block.h>

class dvbs2_ber_runtime : public gr::top_block {
  const gr::analog::noise_type_t noise_type = gr::analog::GR_GAUSSIAN;

private:
  gr::analog::random_uniform_source_b::sptr random_src;
  gr::blocks::throttle::sptr throttle_src;
  gr::blocks::null_sink::sptr ber_sink;

public:
  dvbs2_ber_runtime(double symbol_rate = 1000);
};

#endif /* DVBS2_BER_RUNTIME */