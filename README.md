# blacknight
Sleep tracker

### Python learning notes
python -m venv .blacknight
source .venv/bin/activate
pip install --upgrade pip
# Cool trick for creating a gitignore in .venv/ to ignore it
echo "*" > .venv/.gitignore


# Docker
See README.Docker.md and README.ads.md

# FastAPI
http://localhost:8000
http://localhost:8000/docs
http://localhost:8000/redoc

## Start FastAPI locally
fastapi dev app.py

### Kind, K8S and Istio links
https://kind.sigs.k8s.io/docs/user/quick-start/
https://istio.io/latest/docs/setup/platform-setup/kind/
https://kind.sigs.k8s.io/docs/user/loadbalancer/


### K8S port forward 
kubectl port-forward --address 0.0.0.0 pod/mypod 8888:5000
kubectl get pod -o wide --all-namespaces
kubectl get pod -o=custom-columns=NODE:.spec.nodeName,NAME:.metadata.name --all-namespaces
kubectl proxy --address='0.0.0.0' --accept-hosts='^*$'
nohup kubectl proxy --address='0.0.0.0' --accept-hosts='^*$' &

