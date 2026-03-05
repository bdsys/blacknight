# aws-dmz-services
Web services for operating the DMZ


### Ops
#### Perform a build with no cache
docker compose build --no-cache
#### Perform a build using cache then brings containers UP
docker compose up --build
#### Perform a build using cache then brings containers UP then runs in the background
docker compose up --build -d -- run in the background after build

#### Tag a container with "latest" tag
docker tag aws-dmz-services-server quay.cnqr.delivery/iopsnetwork/aws-dmz-services:<tag>

#### Push local "latest" to Quay remote
docker push quay.cnqr.delivery/iopsnetwork/aws-dmz-services:<tag>

#### Run on local K8S
kubectl apply -f docker-python-kubernetes.yaml
kubectl delete -f docker-python-kubernetes.yaml

#### Run Postgres DB
kubectl apply -f docker-postgres-kubernetes.yaml
kubectl delete -f docker-postgres-kubernetes.yaml

#### Check deployments to K8S
kubectl get deployments

#### Check services running on K8S
kubectl get services


#### AWS ECS copilot
copilot init --app aws-dmz-services \
  --name fastapi-demo \
  --type 'Load Balanced Web Service' \
  --dockerfile './Dockerfile' \
  --port 80 \
  --deploy |
  --tag "RoleType":"netans"


#### Example DB app POST
curl -X 'POST' \            
  'http://localhost:8000/heroes/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "bucketName": 1,
  "name": "my hero",
  "secret_name": "austing",
  "age": 12
}'

curl -X 'POST' 'http://localhost:8000/heroes/' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"bucketName": 1,"name": "my hero","secret_name": "austing","age": 12}'

#### Example DB app GET
curl -X 'GET' \
  'http://localhost:8000/heroes/' \
  -H 'accept: application/json'

curl -X 'GET' 'http://localhost:8000/heroes/' -H 'accept: application/json'

#### Example feeds service call
curl 'http://localhost:8000/feeds/?feed_name=gbaas'

#### Example ansible-runner service call
curl -X 'POST' \            
  'http://localhost:8000/ansible-runner/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "bucketName": "test-bucket",
  "key": "test/key.yaml",
  "verbosity": 3
}'

curl -X 'POST' 'http://localhost:8000/ansible-runner/' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"bucketName": "isbn-sandbox-ansible-trigger-bucket","key": "sandbox_aggregate_webfilter_add_url_fmg.yaml", "verbosity": 3}'

# manual cluster
curl 'http://manual-ansible-task-runner-nlb-7ddd25d99a6857ab.elb.us-west-2.amazonaws.com:8000/feeds/?feed_name=gbaas'


curl -X 'POST' 'http://manual-ansible-task-runner-nlb-7ddd25d99a6857ab.elb.us-west-2.amazonaws.com:8000/ansible-runner/' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"bucketName": "isbn-sandbox-ansible-trigger-bucket","key": "sandbox_aggregate_webfilter_add_url_fmg.yaml"}'

# CFN cluster
curl 'http://iops-n-LoadB-Ikym41PJoZd9-087b84bf8654c363.elb.us-west-2.amazonaws.com/feeds/?feed_name=gbaas'


curl -X 'POST' 'http://iops-n-LoadB-Ikym41PJoZd9-087b84bf8654c363.elb.us-west-2.amazonaws.com/ansible-runner/' -H 'accept: application/json' -H 'Content-Type: application/json' -d '{"bucketName": "isbn-sandbox-ansible-trigger-bucket","key": "sandbox_aggregate_webfilter_add_url_fmg.yaml"}'


# TODO
* Learn about deploying to Kraken using this demo repo: https://github.concur.com/kraken/kate/tree/main/demo
* Demo video: https://video.sap.com/media/t/1_77m8qdai/241704742
* Kraken guide: https://pages.github.concur.com/kraken/documentation/external/docs/application-developer/Release-Pipeline/
* Lifecycle guide: https://pages.github.concur.com/kraken/documentation/external/docs/application-developer/Release-Pipeline/3-lifecycle/
* Kate guide: https://pages.github.concur.com/kraken/documentation/external/docs/application-developer/Release-Pipeline/1-kate/
* Kate RPL PLZ file: https://github.concur.com/plz/tools/blob/master/approved-repos/kate.yaml
- Unsure how necessary this is...


## temporal-admin example
* Quay: https://quay.cnqr.delivery/repository/tools/temporal-admin
* namespace-repos: https://github.concur.com/namespace-repos/temporal/blob/target_tools-eks_integration/temporal-admin.yaml
* app repo: https://github.concur.com/tools/temporal-admin
* RPL PLZ: https://github.concur.com/plz/tools/blob/master/approved-repos/si-temporal/temporal-admin.yaml


# Travel-admin example
* namespace-repo: https://github.concur.com/namespace-repos/travel-admin
* RPL PLZ: https://github.concur.com/plz/travel/blob/master/approved-repos/travel-admin/compleat-admin-api.yaml
* app repo: https://github.concur.com/travel-admin/compleat-admin-api
