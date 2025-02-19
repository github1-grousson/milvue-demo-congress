SHELL := /bin/bash

# Variables
IMAGE_NAME = milvue-admin-tool
DOCKERHUB_USER = wilfriedmv

build:
	@if [ ! -f VERSION ]; then echo "1.0" > VERSION; fi; \
	current_version=$$(cat VERSION); \
	echo "Building docker image '$(DOCKERHUB_USER)/$(IMAGE_NAME)' with version $$current_version"; \
	docker build -t $(DOCKERHUB_USER)/$(IMAGE_NAME):$$current_version .; \
	docker tag $(DOCKERHUB_USER)/$(IMAGE_NAME):$$current_version $(DOCKERHUB_USER)/$(IMAGE_NAME):latest; \
	echo $$current_version > .LAST_VERSION; \
	next_version=$$(echo $$current_version | awk -F. '{printf "%d.%d", $$1, $$2+1}'); \
	echo $$next_version > VERSION; \
	echo "Next version will be $$next_version"

push:
	@if [ ! -f .LAST_VERSION ]; then \
		echo "No built image version found. Please run 'make build' first."; \
		exit 1; \
	fi; \
	version=$$(cat .LAST_VERSION); \
	echo "Pushing docker image with version $$version"; \
	docker push $(DOCKERHUB_USER)/$(IMAGE_NAME):$$version; \
	echo "Pushing docker image with tag 'latest'"; \
	docker push $(DOCKERHUB_USER)/$(IMAGE_NAME):latest
