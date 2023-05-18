from acm_sim_fec_ber import acm_sim_fec_ber
import csv

class test_suite():
    def __init__(self, table_path: str, sym_rate=1000000, frame_size='normal', test_size=2000000):
        self.sym_rate = sym_rate
        self.frame_size = frame_size
        self.test_size = test_size
        self.table_path = table_path
        self.columns = ['modcod', 'snr', 'ber', 'rate', 'effrate']
        self.table = open(table_path, mode='a', newline='')
        self.writer = csv.DictWriter(self.table, fieldnames=self.columns)
        self.writer.writeheader()

    def __del__(self):
        self.table.close()

    def test_case(self, esn0_db, modcod):
        self.tb = acm_sim_fec_ber(
            sym_rate=self.sym_rate, 
            esn0_db=esn0_db, 
            frame_size=self.frame_size, 
            modcod=modcod, 
            test_size=self.test_size)
        self.tb.start()

    def stop(self):
        if self.tb is not None:
            self.tb.stop()
    
    def wait(self):
        if self.tb is not None:
            self.tb.wait()

    def print_results(self):
        if self.tb is not None:
            ber = 10 ** (0.1 * self.tb.get_ber())
            rate = self.tb.get_rate()
            print()
            print('Detected SNR: ' + str(self.tb.get_detected_snr()))
            print('Throughput: ' + str(rate))
            print('BER: ' + str(ber))
            print('Effective throughput: ' + str(rate * (1.0 - ber)))

    def store_results(self):
        if self.tb is not None:
            ber = 10 ** (0.1 * self.tb.get_ber())
            rate = self.tb.get_rate()
            self.writer.writerow({
                'modcod': self.tb.get_modcod(), 
                'snr': self.tb.get_detected_snr(),
                'ber': ber,
                'rate': rate,
                'effrate': rate * (1.0 - ber)
            })

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
    ts = test_suite(
        options.table_path,
        sym_rate=options.sym_rate,
        frame_size=options.frame_size,
        test_size=options.test_size)
    
    import sys, signal
    def sig_handler(sig=None, frame=None):
        global ts
        print('Interrupted!')
        ts.stop()
        ts.wait()
        ts.print_results()
        del ts
        sys.exit(0)

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    import random
    modcods = {
        # 'QPSK_1/4': -2.35,
        # 'QPSK_1/3': -1.24,
        # 'QPSK_2/5': -0.3,
        # 'QPSK_1/2':  1.0,
        # 'QPSK_3/5':  2.23,
        # 'QPSK_2/3':  3.10,
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
        n_test_runs = 20
        for _ in range(n_test_runs):
            esn0_db = (random.random() * 13.0) - 2.0
            print('SNR: ' + str(esn0_db))
            modcod = min(modcods.items(), key=lambda x: abs(x[1] - esn0_db))[0]
            print('Selected MODCOD: ' + modcod)
            ts.test_case(esn0_db, modcod)
            ts.wait()
            ts.store_results()
            ber = 10 ** (0.1 * ts.tb.get_ber())
            rate = ts.tb.get_rate()
            effrate = rate * (1.0 - ber)
            print('Effective throughput: ' + str(effrate))
            avg_rate += effrate
        print('Average effective throughput: ' + str(avg_rate / n_test_runs))
    else:
        # Test CCM:
        for esn0_db in range(5, 11):
            for modcod in modcods.keys():
                ts.test_case(esn0_db, modcod)
                ts.wait()
                ts.store_results()
                ts.print_results()
    del ts
