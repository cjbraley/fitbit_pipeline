help:
	@echo "  make infra-init 				Create project infrastructure"
	@echo "  make infra-run command=apply   Run init / plan / apply / destroy in Terraform using Docker"
	@echo "  make redshift-init  			Creates schema and tables in Redshift"
	@echo "  make prefect-start  			Start Prefect Orion"
	@echo "  make prefect-deploy  			Deploy the flow in Orion"
	@echo "  make prefect-worker          	Start the prefect worker"
	@echo "  make backfill        			Run the backfill script. First set dates in file"


install:
	python -m venv venv && source venv/bin/activate && pip3 install -r requirements.txt

infra-init:
	docker run --rm -it -v $(shell pwd)/terraform:/data -w /data --env-file .env hashicorp/terraform init
	docker run --rm -it -v $(shell pwd)/terraform:/data -w /data --env-file .env hashicorp/terraform apply
	python redshift/init.py

infra-run:
	docker run --rm -it -v $(shell pwd)/terraform:/data -w /data --env-file .env hashicorp/terraform $(command)

redshift-init:
	python redshift/init.py 

prefect-start:
	prefect config set PREFECT_API_URL="http://127.0.0.1:4200/api"
	prefect orion start

prefect-deploy:
	python prefect_deploy.py

prefect-worker:
	prefect agent start -p default-agent-pool

backfill:
	python prefect_backfill.py
