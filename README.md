# Dayfold - Pinterest Clone (Algorithms Project)

Dayfold is an image-sharing platform inspired by Pinterest, developed as part of an algorithms course. The primary objective is to apply complex data structures and algorithms for recommendations, community management, and friend suggestions.

## 🚀 Key Features

- **Content Management**: Create "Pins", organize them into Boards, and categorize them.
- **Social Interactions**: Follow system between users and "Like" functionality on pins.
- **Graph Visualization**: Integration with Neo4j to visualize relationships between users and content.
- **Algorithm Dashboard**: Real-time visualization of the results from various implemented algorithms.

## 🧠 Implemented Algorithms

The core of this project leverages graph theory algorithms to enhance the user experience:

### 1. Friend Suggestions (BFS)
Uses a **Breadth-First Search** (BFS) to find "friends of friends" that the user is not yet following. The algorithm explores the social graph to suggest relevant connections based on structural proximity.

### 2. Community Detection (Louvain)
Implementation of the **Louvain method** to partition users into communities based on their interests and interactions. This allows for dynamic naming of groups (e.g., "Tech Squad", "Design Lovers") and provides insights into the overall network structure.

### 3. Feed Recommendation (Personalized PageRank - PPR)
An advanced recommendation system using **Personalized PageRank**. By setting the current user as the "teleportation source," the algorithm propagates importance through the graph (users -> boards -> pins) to surface the most relevant content based on their specific tastes.

### 4. Category Hierarchy (Tree)
Manages pin categories via a **Tree** structure, allowing for hierarchical navigation and filtered searches by parent/child themes.

---

## 🛠 Tech Stack

- **Frontend**: React.js, Tailwind CSS (Modern and responsive design).
- **Backend**: FastAPI (Python 3.10+), Asynchronous and high-performance.
- **Databases**:
  - **PostgreSQL**: Relational data (Users, Pins, Likes).
  - **Neo4j**: Graph database for algorithmic computations.
- **Containerization**: Docker & Docker Compose.

---

## 📦 Installation and Setup

The project is fully containerized for easy deployment.

### Prerequisites
- Docker
- Docker Compose

### Running the Application
1. Clone the repository.
2. Start the infrastructure:
   ```bash
   docker-compose up --build
   ```
3. The application will be accessible at:
   - **Frontend**: `http://localhost:3000`
   - **Backend API**: `http://localhost:8000`
   - **Neo4j Browser**: `http://localhost:7474` (login: `neo4j` / `password123`)

### Test Data (Seed)
A `seed` service is included in the `docker-compose.yml`. It automatically populates the database with approximately 50 users, numerous boards, and over 100 pins upon the first launch.

---

## 📂 Project Structure

```text
├── app/                # FastAPI Backend
│   ├── algorithms/     # Implementations (BFS, Louvain, PPR, Trees)
│   ├── routers/        # API Endpoints
│   ├── models.py       # SQLAlchemy / Pydantic schemas
│   └── main.py         # Entry point
├── frontend/           # React Application
│   └── src/components/ # UI Components (Feed, Profile, Search...)
├── louvain/            # Louvain experimental scripts
├── init.sql            # PostgreSQL initialization
└── docker-compose.yml  # Service orchestration
```