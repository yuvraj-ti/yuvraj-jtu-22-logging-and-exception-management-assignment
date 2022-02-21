all: deploy

check-environment-variables:
ifndef SAM_BUCKET_NAME
	$(error SAM_BUCKET_NAME is not set)
endif

deploy: check-environment-variables
	sam package --s3-bucket ${SAM_BUCKET_NAME} --output-template-file packaged.yaml
	sam deploy \
	--template-file packaged.yaml \
	--stack-name stateflow-resources \
	--capabilities CAPABILITY_IAM

destroy:
	aws cloudformation delete-stack --stack-name stateflow-resources