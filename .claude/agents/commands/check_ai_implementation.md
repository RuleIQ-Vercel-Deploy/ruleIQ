
**Task: Analyze and Optimize Our Google Generative AI Python SDK Implementation**

First use your mcp tool context7 to access the full documentation for `Google Gen AI Python SDK`. Read the documents comprehensivley so that you have a native understadnign how to work with and implemnt the sdk with best practive at an advanced level.

then

Leveraging your full access to the ruleIQ project codebase, perform a comprehensive analysis of our implementation of the `Google Gen AI Python SDK`.

Your primary goal is to identify opportunities for us to use the SDK to its maximum effect. Your analysis should focus on the following key areas:

1.  **Cost-Effectiveness:** Are we using the most cost-efficient models for our tasks? (e.g., Are there places we could use a faster, cheaper model like Gemini Flash instead of a more powerful one like Gemini Pro?)
2.  **Performance & Latency:** Can our implementation be optimized for speed? Are we correctly using features like streaming (`stream=True`) or batching where applicable?
3.  **Advanced Feature Utilization:** Are we missing out on powerful SDK features that could benefit our project? Please look for opportunities to implement:
    * Function Calling / Tool Use
    * Caching
    * System Instructions
    * Advanced Safety Settings
4.  **Code Quality & Best Practices:** Is our SDK implementation robust, maintainable, and aligned with Google's official best practices? Identify any deprecated methods or inefficient patterns.

Please structure your response in three distinct sections:

* **Section 1: Current State Summary**
    * Briefly summarize how the project currently uses the Google Gen AI Python SDK, including the primary models and features you've identified in the code.

* **Section 2: Optimization Analysis**
    * Detail your findings based on the four key areas (Cost, Performance, Features, and Quality). For each point, explain the potential impact of the missed opportunity.

* **Section 3: Actionable Recommendations**
    * Provide a clear, prioritized list of recommendations. For each recommendation, include:
        * **What** to change.
        * **Why** the change is beneficial.
        * **(If possible) A specific code snippet** from our project and the suggested modification.