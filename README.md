# **Strava Challenge V2**

A web application for a Strava challenge. This project includes a python backend, a React frontend, and a MongoDB database.

---

## **Project Setup**

### **Components**
1. **Backend**: A Python Flask application (`src/main.py`) providing APIs.
2. **Frontend**: A React application served on port 5000
3. **Database**: MongoDB running in a Docker container.

---

## **Docker Setup**

This project uses Docker Compose to containerize and manage services.

### **Build and Start**
To build and start the application:
```bash
docker compose up --build
```
This command:
1. Builds the Docker images for all services.
2. Starts the containers.

Access the services at:
- Backend: [http://localhost:8080](http://localhost:8080)
- Frontend: [http://localhost:5000](http://localhost:5000)

### **Stop the Containers**
To stop all running containers:
```bash
docker compose down
```

---

## **Quick Docker Tips**

### **1. Rebuild Only One Service**
If you make changes to the backend and need to rebuild it:
```bash
docker compose build backend
```
Restart the backend service without affecting others:
```bash
docker compose up backend
```

### **2. Persistent MongoDB Data**
- MongoDB data is stored in a Docker volume (`mongo_data`).
- The data persists across container restarts.

To clear the MongoDB data:
```bash
docker compose down -v
```

### **3. Logs**
View logs for a specific service (e.g., backend):
```bash
docker compose logs backend
```

---

## **Project Initialization**

### **Database Initialization**
During the first run, the `mongo-init.js` script initializes the MongoDB database with users and collections.

---

## **How to Start Locally Without Docker**

If you prefer to run the backend and frontend locally:
1. **Start MongoDB**:
   ```bash
   docker compose up mongo
   ```

2. **Run the Backend**:
   ```
   Start the backend:
   ```bash
   python3 src/main.py
   ```

3. **Run the Frontend**:
   Navigate to the `frontend` directory and start the React development server:
   ```bash
   npm start
   ```

---

### **Port Conflicts**
Ensure the following ports are free on your host machine:
- MongoDB: `27017`
- Backend: `8080`
- Frontend: `3000`

