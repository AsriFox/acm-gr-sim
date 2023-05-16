#include "ber_runtime.hh"
#include <csignal>
#include <exception>
#include <iostream>
#include <stdexcept>

namespace {
volatile std::sig_atomic_t quit = 0;

void handler(int signal) { quit = 1; }
} // namespace

int main(int argc, char **argv) {
  try {
    dvbs2_ber_runtime top_block(2000000);
    std::cout << "Start" << std::endl;
    top_block.start();

    signal(SIGTERM, handler);
    signal(SIGINT, handler);
    for (; !quit;)
      ;
    std::cout << "End" << std::endl;
    top_block.stop();
    top_block.wait();
  } catch (std::exception &ex) {
    std::cout << ex.what() << std::endl;
  }
  return 0;
}