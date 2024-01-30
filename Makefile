IMAGE = sim:latest
CONTAINER = sim

all :
	@echo "Usage: make [ env | exit | update]"

env :
	@. env/bin/activate

exit :
	@deactivate

update :
	@git pull origin main

build:
	docker build $(if $(RE), --no-cache,) -t $(IMAGE) .

run:
	docker run --rm -d -p 6080:80 --security-opt seccomp=unconfined --shm-size=512m -v ./:/home/ubuntu/Documents/Car --name $(CONTAINER) $(IMAGE)

stop:
	docker stop $(CONTAINER)

open:
	open "http:127.0.0.1:6080"

.PHONY : all env exit update
