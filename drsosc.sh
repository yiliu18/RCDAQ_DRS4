sudo chmod -R 777 /dev/bus/usb/

# end and close any existing rcdaq session, required for drsosc
if rcdaq_client daq_status > /dev/null 2>&1 ; then
    echo -en "Ending existing rcdaq session ... "
    rcdaq_client daq_end > /dev/null 2>&1 # end run
    echo -n "waiting for 0.5s ... "
    sleep 0.5
    rcdaq_client daq_shutdown > /dev/null 2>&1 # shutdown server
    echo -n "waiting for 2s ... "
    sleep 2
    echo -e "done."
fi

drsosc