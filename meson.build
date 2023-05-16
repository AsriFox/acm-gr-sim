project('acm-gr-sim', 'cpp', 'c')

gr_runtime = dependency('gnuradio-runtime', version: '>=3.10')
gr_analog = dependency('gnuradio-analog', version: '>=3.10')
gr_blocks = dependency('gnuradio-blocks', version: '>=3.10')
gr_dtv = dependency('gnuradio-dtv', version: '>=3.10')
gr_fec = dependency('gnuradio-fec', version: '>=3.10')
gr_filter = dependency('gnuradio-filter', version: '>=3.10')
gr_volk = dependency('volk')
fmt = dependency('fmt')

cpp = meson.get_compiler('cpp')
gr_dvbs2rx = cpp.find_library('gnuradio-dvbs2rx', required: true)

sim_exe = executable(
    'acm-gr-sim',
    sources: ['main.cc', 'ber_runtime.cc'],
    dependencies: [
        gr_runtime, gr_analog, gr_blocks, 
        gr_dtv, gr_fec, gr_filter, 
        gr_dvbs2rx, 
        gr_volk, fmt
    ]
)
