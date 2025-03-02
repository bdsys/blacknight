echo "Starting up dev server..."
echo "Pulling changes from git..."
git checkout dev1
git pull origin dev1
echo "Starting API service in a detached container..."
docker compose up --build -d
echo "Done!"

