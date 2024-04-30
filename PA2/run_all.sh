# The code is subject to Purdue University copyright policies.
# DO NOT SHARE, DISTRIBUTE, OR POST ONLINE
#

#!/bin/bash

echo python network.py 01.json DV
python network.py 01.json DV
echo python network.py 02.json DV
python network.py 02.json DV
echo python network.py 03.json DV
python network.py 03.json DV

echo python network.py 01.json LS
python network.py 01.json LS
echo python network.py 02.json LS
python network.py 02.json LS
echo python network.py 03.json LS
python network.py 03.json LS
