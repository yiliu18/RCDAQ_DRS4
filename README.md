Clean and build the project
```bash
make clean && make
```

Setup DRS4 RCDAQ server
```bash
./drs_setup.sh
```

Running DRSCL and DRSOSC will stop existing RCDAQ server, so make sure to run `drs_setup.sh` again after using them. These scripts automatically kill existing RCDAQ servers and start DRSCL/DRSOSC.
```bash
./drscl.sh
./drsosc.sh
```

Run example PMT scan
```bash
python PMT_scan.py
```

