## 🧠 AI-Powered Personal Mentor - GenAI Project

Welcome to the **AI-Powered Personal Mentor**, a web-based GenAI agent that helps users ace their job interviews. This project was created as part of the Kalvium course on Developing AI Agents using GenAI.

-----

### 💡 Project Overview

The AI-Powered Personal Mentor acts as an all-in-one interview coach. It takes a user's question or code snippet and provides tailored, intelligent responses. It uses Generative AI techniques to reason about complex problems, retrieve relevant context, format output for a clean UI, and call functions to execute code or log results.

-----

### 🚀 Features & Concepts Implemented

✅ **1. Prompting**

The agent prompts the user in a natural, conversational way.
It uses structured prompts (RFTC) in the backend to ensure a supportive tone, a consistent output format, and a clear understanding of the interview context.

✅ **2. Retrieval-Augmented Generation (RAG)**

Instead of relying solely on its internal knowledge, the bot can retrieve context from a database of common interview questions and optimal answers (both technical and behavioral). This ensures answers are specific and accurate. For example, if a user asks about a specific algorithm, the bot retrieves the problem description and a detailed explanation from the database to inform its response.

✅ **3. Structured Output**

The agent formats its response as structured JSON to be easily parsed and displayed by the MERN frontend.

Example for a coding problem:

```json
{
  "problem_title": "Two Sum",
  "difficulty": "Easy",
  "description": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.",
  "expected_complexity": {
    "time": "O(n)",
    "space": "O(n)"
  }
}
```

✅ **4. Function Calling**

The agent can use function calling to trigger post-processing actions on the backend, such as:

  * Executing a user's code in a sandboxed environment (`run_code(code, language)`).
  * Saving a user's mock interview results to a database (`save_results(user_id, results)`).

-----

### 🧪 Tech Stack

  * **Language:** Python for the core GenAI logic (e.g., as a microservice called by the Node.js backend).
  * **Web Stack:** MERN (MongoDB, Express.js, React, Node.js) for the full-stack web application.
  * **LLM Integration:** Google Studio API for prompting and generation.
  * **Planned Additions:** Authentication, user dashboards, and progress tracking.

-----

### 🤖 System Prompt

You are a supportive and knowledgeable technical interview coach. Your job is to help users prepare for their interviews by providing clear explanations for technical questions, generating code snippets, and giving constructive feedback. Always respond in a clear, encouraging, and helpful tone.

-----

### 👤 User Prompt Example

I need to write a function in Python for `reverse a linked list`.

-----

### 🧠 Prompt Design Using RFTC

  * **Role:** Technical interview coach.
  * **Format:** Clear, readable text (or structured JSON when appropriate).
  * **Tone:** Encouraging, informative, and professional.
  * **Context:** The user's query about a specific coding problem or technical concept.

-----

### 🧠 Zero-Shot Prompting – ExplainConcept

Provide a clear explanation for a technical concept.

```
Explain the difference between a `stack` and a `queue` data structure.
```

**❓ Why is this Zero-Shot?**
No examples are given to the model. It's expected to complete the task based solely on its instruction and knowledge. This tests the LLM's ability to provide a general explanation.

-----

### 📄 One-Shot Prompt Used

The user wants to see how a function should be documented in a specific style.

````
Example Input: "Write a function `sum_array` that takes a list of numbers and returns their sum."
Example Output:
```python
def sum_array(numbers: list[int]) -> int:
    """
    Calculates the sum of all elements in a list of integers.

    Args:
        numbers: A list of integers.

    Returns:
        The sum of the integers in the list.
    """
    return sum(numbers)
````

Now, write a Python function `find_max` that finds the maximum value in a list of numbers, following the same documentation style.

```

***

### 📄 Multi-Shot Prompt

This prompt includes 3 input/output examples showing how to provide feedback on a behavioral question.

### Example 1:
**Input:** "Tell me about a time you failed."
**Output:** *(structured JSON feedback on how to structure a STAR response)*

### Example 2:
**Input:** "Describe a conflict you had with a teammate."
**Output:** *(structured JSON feedback on empathy and resolution)*

### Example 3:
**Input:** "Why should we hire you?"
**Output:** *(structured JSON feedback on highlighting unique skills)*

### New User Input:
"What is your greatest weakness?"
The model should now follow the format, tone, and structure from the above examples and generate a similar feedback response.

**❓ Why is this Multi-Shot?**
The model is given **multiple examples** of the expected behavior before being asked to respond. This helps it learn a specific feedback format, tone, and logical flow more accurately.

***

### 📄 Dynamic Prompt Example

Suppose the user types:
> "Write me code for a binary search tree in **C++**."
The prompt generated **at runtime** would be:
> You are a technical interview coach. The user wants to see code for a binary search tree. Your task is to write a well-commented, functional **C++** code snippet.
>
> You must also provide a brief explanation of the code's time and space complexity.
>
> Respond in Markdown format, with the code block clearly labeled as **cpp**.

If the user input was:
> "Write me code for a binary search tree in **Java**."
The dynamically generated prompt would be identical, but the language specified would be **Java**.

**❓ Why is this Dynamic Prompting?**
The prompt is **not static** — it is **constructed on the fly** based on the user's input, specifically the programming language they requested. This allows for highly personalized, context-aware responses.

***

### 🧠 Chain of Thought Prompting – DebugMyCode

**📄 Prompt Design**
The user will give you a code snippet and a problem description. First, identify the user's intent (e.g., debug, optimize). Then, think step-by-step to analyze the code for errors or inefficiencies. Finally, provide a clear explanation of the issue and a corrected version of the code.

**👤 User Input**
"My Python function to find the factorial of a number is not working. The function is: `def factorial(n):\n\tif n == 0:\n\t\treturn 1\n\telse:\n\t\treturn n * factorial(n-1)`"

**🧠 Why is this Chain of Thought Prompting?**
This prompt **forces the model to think step-by-step**. It has to first identify the user's intent (debugging), then analyze the code's logic, and only then generate the final explanation and corrected code. This helps improve both the **accuracy** and **relevance** of the debugging response.
```