default:
	-killall python3.6
	python3.6 archive_service/service.py &
	python3.6 download_service/service.py &
