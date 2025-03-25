🚀 **Project Setup Guide**
==========================

This project is built using **Next.js** for the frontend and **Django** (with Docker) for the backend. Follow the steps below to set up and run the project locally.

* * * * *

✅ **Requirements**
------------------

Ensure you have the following installed:

-   **Node.js** (v18+ recommended)

-   **npm** (comes with Node.js)

-   **Docker** (latest version)

-   **Make** (for running make commands)

* * * * *

 **Running the Frontend**
------------------------------

1.  **Navigate to the frontend directory:**

    ```
    cd client

    ```

2.  **Install dependencies:**

    ```
    npm install

    ```

3.  **Start the development server:**

    ```
    npm run dev

    ```

4.  The frontend will be available at:\
    👉 [http://localhost:3000](http://localhost:3000/)

* * * * *

🔥 **Running the Backend**
--------------------------

1.  **Ensure Docker is running**

2.  **From the project root, start the backend with:**

    ```
    make run

    ```

3.  The backend will be available at:\
    👉 [http://localhost:8000](http://localhost:8000/)

* * * * *

📄 **API Documentation**
------------------------

Once the backend is running, you can access the API documentation at:\
👉 <http://localhost:8000/api>

* * * * *

🛠️ **Common Commands**
-----------------------

| Command | Description |
| --- | --- |
| `npm install` | Install frontend dependencies |
| `npm run dev` | Start frontend development server |
| `make run` | Start backend using Docker |
| `make test` | Run tests |
| `make logs` | View backend logs |
| `make down` | Stop and remove all Docker containers |

* * * * *



🚀 **You're all set!**
----------------------