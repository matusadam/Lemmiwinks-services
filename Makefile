default:
	-killall python3.6
	python3.6 app_test.py &
	python3.6 app_downloader.py &
