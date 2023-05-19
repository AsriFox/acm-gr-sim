from acm_sim_fec_ber import acm_sim_fec_ber
import csv

def store_results(writer: csv.DictWriter, modcod, snr, ber, rate):
    writer.writerow({
        'modcod': modcod, 
        'snr': snr,
        'ber': ber,
        'rate': rate,
        'effrate': rate * (1.0 - ber)
    })

def print_results(modcod, snr, ber, rate):
    print()
    print(f'MODCOD: {modcod} | SNR: {snr}')
    print(f'Throughput: {rate} | BER: {ber}')
    print(f'Effective throughput: {rate * (1.0 - ber)}') 

import sys, signal
def test_case(sym_rate, esn0_db, frame_size, modcod, test_size):
    snr = None
    ber = None
    rate = None

    with acm_sim_fec_ber(sym_rate, esn0_db, frame_size, modcod, test_size) as tb:
        
        def sig_handler(sig=None, frame=None):
            print('Interrupted!')
            tb.stop()
            tb.wait()
            print_results(
                tb.get_modcod(), 
                tb.get_detected_snr(), 
                10 ** (0.1 * tb.get_ber()), 
                tb.get_rate()
            )
            global table
            table.close()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, sig_handler)
        signal.signal(signal.SIGTERM, sig_handler)

        tb.start()
        tb.wait()

        snr = tb.get_detected_snr()
        ber = 10 ** (0.1 * tb.get_ber())
        rate = tb.get_rate()

    return (modcod, snr, ber, rate)

if __name__ == '__main__':
    from argparse import ArgumentParser
    from gnuradio.eng_arg import eng_float, intx
    from gnuradio import eng_notation

    parser = ArgumentParser(description='DVB-S2 BCH/LDPC BER Simulation')
    parser.add_argument(
        "table_path", metavar="TABLE", type=str,
        help="CSV table to write results to")
    parser.add_argument(
        "-f", "--frame-size", dest="frame_size", type=str, default="normal",
        help="Set FECFRAME size [default=%(default)r]")
    parser.add_argument(
        "-r", "--sym-rate", dest="sym_rate", type=intx, default=10000000,
        help="Set symbol rate in baud [default=%(default)r]")
    parser.add_argument(
        "-t", "--test-size", dest="test_size", type=intx, default=20000000,
        help="Set test size in symbols [default=%(default)r]")
    parser.add_argument(
        "--acm", dest="acm", action='store_true',
        help="Test ACM performance [default=False]")

    options = parser.parse_args()
    table_path = options.table_path
    sym_rate = options.sym_rate
    frame_size = options.frame_size
    test_size = options.test_size
    snr_min = options.snr_min
    snr_max = options.snr_max

    table = open(table_path, mode='a', newline='')
    writer = csv.DictWriter(table, fieldnames=['modcod', 'snr', 'ber', 'rate', 'effrate'])
    writer.writeheader()

    import random
    modcods = {
        'QPSK_1/4': -2.35,
        'QPSK_1/3': -1.24,
        'QPSK_2/5': -0.3,
        'QPSK_1/2':  1.0,
        'QPSK_3/5':  2.23,
        'QPSK_2/3':  3.10,
        'QPSK_3/4':  4.03,
        'QPSK_4/5':  4.68,
        'QPSK_5/6':  5.18,
        'QPSK_8/9':  6.20,
        'QPSK_9/10': 6.42,
        '8PSK_3/5':  5.50,
        '8PSK_2/3':  6.62,
        '8PSK_3/4':  7.91,
        '8PSK_5/6':  9.35,
        '8PSK_8/9': 10.69,
        '8PSK_9/10':10.98,
    }
    if options.acm:
        avg_rate = 0.0
        n_test_runs = 400
        for _ in range(n_test_runs):
            esn0_db = random.uniform(-2, 14)
            print('SNR: ' + str(esn0_db))
            modcod = min(
                [x for x in modcods.items() if x[1] < esn0_db], 
                key=lambda x: abs(x[1] - esn0_db)
            )[0]
            print('Selected MODCOD: ' + modcod)
            results = test_case(sym_rate, esn0_db, frame_size, modcod, test_size)
            store_results(writer, *results)
            # _, _, ber, rate = results
            effrate = results[3] * (1.0 - results[2])
            print(f'Effective throughput: {effrate}')
            avg_rate += effrate

        writer.writerow({
            'modcod': 'average', 
            'snr': '-2..14',
            'ber': '',
            'rate': '',
            'effrate': avg_rate / n_test_runs
        })
        print('Average effective throughput: ' + str(avg_rate / n_test_runs))
    else:
        # Test CCM:
        for esn0_db in range(-2, 14):
            for modcod in modcods.keys():
                results = test_case(sym_rate, esn0_db, frame_size, modcod, test_size)
                store_results(writer, *results)
                print_results(*results)

    table.close()
