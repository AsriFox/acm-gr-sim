project('acm-gr-sim', 'cpp', 'c')

gr_runtime = dependency('gnuradio-runtime', version: '>=3.10')
gr_analog = dependency('gnuradio-analog', version: '>=3.10')
gr_blocks = dependency('gnuradio-blocks', version: '>=3.10')
gr_volk = dependency('volk')
fmt = dependency('fmt')

sim_exe = executable(
    'acm-gr-sim',
    sources: ['main.cc', 'ber_runtime.cc'],
    dependencies: [gr_runtime, gr_analog, gr_blocks, gr_volk, fmt]
)
