#include <mutex>
// #include <chrono>
// #include <thread>
#include <iostream>

#include "PMT_scan.h"
#include <pmonitor/pmonitor.h>

#include <TFile.h>
#include <TH1.h>


int constexpr DRS4_CHANNEL = 3;
int constexpr DRS4_PACKET_ID = 1001;

// TH1F *waveform_histogram = nullptr;
TH1F *peak_histogram = nullptr;

int constexpr WAVEFORM_SIZE = 1024;
int constexpr PEAK_BINS = 4000;
float constexpr MIN_VOLTAGE = -2000;
float constexpr MAX_VOLTAGE = 2000;

size_t events_to_process = 0;
std::mutex events_to_process_mutex;

bool init_done = 0;

int pinit() {

  if (init_done)
    return 1;
  init_done = true;

  std::cout << "\n\x1B[35mReading DRS4 data from channel " << DRS4_CHANNEL << " (labeled \"CH" << DRS4_CHANNEL + 1 << "\" on DRS4).\n";
  std::cout << "Make sure to use the correct channel on the DRS4 board!\x1B[0m\n\n";

  // if (waveform_histogram)
  //   std::cerr << "\x1b[33mWarning: waveform_histogram already exists!\x1b[0m" << std::endl;
  // waveform_histogram = new TH1F("waveform_histogram", "waveform_histogram; sample; voltage [mV]", WAVEFORM_SIZE, 0, WAVEFORM_SIZE);

  if (peak_histogram)
    std::cerr << "\x1b[33mWarning: maxADC_histogram already exists!\x1b[0m" << std::endl;
  peak_histogram = new TH1F("peak_histogram", "peak_histogram; sample, peak voltage [mV]", PEAK_BINS, MIN_VOLTAGE, MAX_VOLTAGE);

  return 0;
}

int set_events_to_process(size_t n) {
  if (!init_done) {
    std::cerr << "\x1b[31mError: pinit() not called before set_events_to_process()!\x1b[0m" << std::endl;
    return -1;
  }

  if (!peak_histogram) {
    std::cerr << "\x1b[31mError: peak_histogram not initialized!\x1b[0m" << std::endl;
    return -1;
  }

  peak_histogram->Reset();

  std::lock_guard<std::mutex> lock(events_to_process_mutex);
  events_to_process = n;
  return 0;
}

int process_event(Event *e) {
  if (!init_done) {
    std::cerr << "\x1b[31mError: pinit() not called before process_event()!\x1b[0m" << std::endl;
    return -1;
  }

  // if (!waveform_histogram) {
  //   std::cerr << "\x1b[31mError: waveform_histogram not initialized!\x1b[0m" << std::endl;
  //   return -1;
  // }

  if (!peak_histogram) {
    std::cerr << "\x1b[31mError: peak_histogram not initialized!\x1b[0m" << std::endl;
    return -1;
  }

  {
    std::lock_guard<std::mutex> lock(events_to_process_mutex);
    if (events_to_process <= 0)
      return 0; 
  }

  Packet *p = e->getPacket(DRS4_PACKET_ID);
  if (!p) {
    // std::cerr << "\x1b[33mWarning: No packet with ID " << DRS4_PACKET_ID << " in event!\x1b[0m" << std::endl;
    return 0; // No packet found, nothing to process
  }

  {
    std::lock_guard<std::mutex> lock(events_to_process_mutex);
      events_to_process--;
  }

  // std::cout << "Got event: ";
  float peak_value = -1;
  for (int i = 0; i < WAVEFORM_SIZE; i++) {
    int value = p->rValue(i, DRS4_CHANNEL);
    // waveform_histogram->SetBinContent(i + 1, value);
    // std::cout << std::setw(5) << std::fixed << std::setprecision(0) << value;
    if (value > peak_value)
      peak_value = value;
  }

  // std::cout << std::endl;
  // std::cout << "Peak value: " << peak_value << std::endl;

  peak_histogram->Fill(peak_value);

  delete p;

  // std::this_thread::sleep_for(std::chrono::milliseconds(10));

  return 0; // Event processed successfully
}
