#include "PMT_scan.h"
R__LOAD_LIBRARY(libPMT_scan.so)

void PMT_scan(const char * filename)
{
  if ( filename != NULL)
    {
      pfileopen(filename);
    }
}
