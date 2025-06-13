#ifndef __PMT_SCAN_H__
#define __PMT_SCAN_H__

#include <pmonitor/pmonitor.h>
#include <Event/Event.h>
#include <Event/EventTypes.h>

int process_event(Event *e); //++CINT
int set_events_to_process(size_t n);

#endif /* __PMT_SCAN_H__ */
