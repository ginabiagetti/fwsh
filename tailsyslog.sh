tail -f /var/log/syslog | \
	./colortail.sh \
	red '--- .* ---' \
	cyan 'SPT=[0-9]* DPT=[0-9]* ' \
	green 'SRC=[0-9a-f\.\:]* DST=[a-f0-9\.\:]*' \
	|grep -v 'xt_physdev: using --physdev-out in the OUTPUT, FORWARD and POSTROUTING chains for non-bridged traffic is not supported anymore.'
