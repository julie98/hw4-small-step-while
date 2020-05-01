all:
	echo "#!/usr/bin/env bash" > while-ss
	echo "python3 interpreter.py \x241" >> while-ss  # escape dollar sign \x24
	chmod +x while-ss

clean:
	rm while-ss
