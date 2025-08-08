AI-Powered Personal Mentor 🚀
Project Overview
The AI-Powered Personal Mentor is a MERN (MongoDB, Express.js, React, Node.js) stack web application designed to be your comprehensive guide for interview preparation. This project simplifies the daunting process of getting ready for a job interview by providing intelligent, interactive assistance for a wide range of questions and challenges.

Our application leverages the power of Generative AI to offer more than just static practice questions. It acts as a personal mentor, helping users with technical concepts, behavioral questions, coding challenges, and providing personalized feedback to help them master their skills and boost their confidence.

Technologies Used
This project is built using a modern full-stack approach combined with advanced Generative AI capabilities.

MERN Stack
M - MongoDB: A flexible NoSQL database to store user data, a repository of interview questions, and a vector database for efficient semantic search.

E - Express.js: The backend framework to build a robust API, handle routing, and serve as the bridge between the React frontend and the Generative AI model.

R - React: The frontend library for building a dynamic, component-based user interface, including a conversational chat window and a code editor for technical interviews.

N - Node.js: The JavaScript runtime environment that powers the backend.

Generative AI
LLM Integration: We will integrate with a Large Language Model (LLM) through an API to power the core functionality of the AI mentor.

Key Concepts: This project is specifically designed to demonstrate proficiency with a variety of GenAI concepts, including:

Prompting Techniques: Zero-shot, One-shot, Multi-shot, and Chain of Thought.

Control Parameters: Temperature, Top K, and Top P for fine-tuning output.

Tooling: Function calling, Structured output, and Stop sequences.

Core Mechanics: Tokens, Tokenization, and Embeddings.

Key Features
Interactive Q&A: Practice answering a wide range of technical and behavioral interview questions with real-time AI feedback.

Code Generation & Explanation: Get help generating and understanding code snippets for common coding challenges.

Mock Interview Simulation: Simulate a live interview experience where the AI asks questions and evaluates your responses.

Personalized Feedback: Receive personalized, actionable advice on your performance, including areas for improvement and key strengths.

Semantic Search: Find similar interview questions or related topics using natural language queries, powered by vector embeddings.

Progress Tracking: The application will track your progress through different topics and mock interviews, helping you stay organized.

How to Run the Project
Clone the repository:
git clone [your-repo-url]
cd personal-mentor

Install dependencies for both frontend and backend:
npm install
cd client && npm install

Set up environment variables:

Create a .env file in the root directory.

Add your MongoDB connection string and your AI API key.
MONGO_URI=your_mongo_db_connection_string
AI_API_KEY=your_genai_api_key

Run the application:

Start the backend server: npm run server

Start the React frontend: npm run client

The application will be accessible at http://localhost:3000.

Getting Started with Development
This project is an excellent opportunity to learn full-stack development with an emphasis on modern AI integration. We encourage you to explore the code, contribute, and use the project to master the interview preparation and GenAI concepts.