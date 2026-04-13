# Databricks notebook source
# MAGIC %md
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">

# COMMAND ----------

# MAGIC %md
# MAGIC # Lecture - Unity Catalog SQL Functions as Agent Tools on Databricks
# MAGIC
# MAGIC ## Overview
# MAGIC
# MAGIC Imagine an AI agent that can instantly answer questions like "What's the average home price in the Mission district?" or "Show me sales trends for our top-performing products" by automatically discovering and executing the right data operations. This is the power of Unity Catalog SQL Functions as Agent Tools.
# MAGIC
# MAGIC Building on the foundational concepts of AI agents and tools covered in the [previous lecture]($./0 Lecture - Foundations of Agents), this session focuses on one of the most practical implementations: using Unity Catalog SQL Functions as intelligent, discoverable tools that AI agents can automatically select and execute based on natural language queries.
# MAGIC
# MAGIC Unlike traditional SQL functions that require manual programming, Unity Catalog SQL Functions as Agent Tools are designed to be self-describing and contextually aware, enabling AI agents to understand when and how to use them based purely on user intent and comprehensive metadata.
# MAGIC
# MAGIC This lecture establishes the technical foundation and best practices needed for the hands-on demonstration that follows, where you'll build and test Unity Catalog SQL Functions as Agent Tools using [AI Playground](https://docs.databricks.com/aws/en/generative-ai/agent-framework/ai-playground-agent).
# MAGIC
# MAGIC ### Learning Objectives
# MAGIC
# MAGIC _By the end of this lecture, you will be able to:_
# MAGIC
# MAGIC - Design SQL functions specifically optimized for AI agent discovery and execution
# MAGIC - Explain the key architectural differences between traditional SQL functions and agent tools in Unity Catalog
# MAGIC - Identify best practices for documentation and metadata that enable effective agent-tool interaction
# MAGIC - Evaluate when Unity Catalog SQL Functions are the appropriate tool choice versus other agent tool types
# MAGIC - ** to build and test agent tools using AI Playground in the upcoming demonstration

# COMMAND ----------

# MAGIC %md
# MAGIC ## A. Understanding Unity Catalog SQL Functions as Agent Tools
# MAGIC
# MAGIC Before getting started, it's important to keep in mind what UC functions are. Unity Catalog tools are really just Unity Catalog user-defined functions (UDFs) under the hood. When you define a Unity Catalog tool, you're registering a function in Unity Catalog. To learn more about Unity Catalog UDFs, see [this documentation](https://docs.databricks.com/aws/en/udf/unity-catalog).
# MAGIC
# MAGIC > **What's a UDF?** 
# MAGIC > User-defined functions (UDFs) in Unity Catalog extend SQL and Python capabilities within Databricks. They allow custom functions to be defined, used, and securely shared and governed across computing environments.

# COMMAND ----------

# MAGIC %md
# MAGIC ### A1. What Are Unity Catalog SQL Functions as Agent Tools?
# MAGIC
# MAGIC **Unity Catalog SQL Functions as Agent Tools** are Unity Catalog functions written in SQL that can be dynamically discovered, selected, and executed by AI agents to perform data operations. Unlike traditional SQL functions that require manual programming to call, Unity Catalog SQL Functions as Agent Tools are designed to be:
# MAGIC
# MAGIC - **Self-describing** through comprehensive metadata and documentation
# MAGIC - **Contextually appropriate** for specific business or analytical tasks
# MAGIC - **Governable** through Unity Catalog's security and access control mechanisms
# MAGIC
# MAGIC Unity Catalog SQL Functions as Agent Tools bridge the gap between natural language queries from users and structured data operations, allowing agents to translate requests like "What's the average price in the Mission district?" into executable SQL functions, where the idea is that the agent understands to extract particular phrases like "Mission" and "average price" if those are relevant to a SQL function assigned to the agent. We will discuss proper best practices for prototyping UC functions in the demo that follows this lecture.

# COMMAND ----------

# MAGIC %md
# MAGIC ### A2. Unity Catalog SQL Functions as Agent Tools vs. Traditional SQL Functions
# MAGIC
# MAGIC Understanding the distinction between Unity Catalog SQL Functions as Agent Tools and traditional SQL functions is crucial for effective implementation:
# MAGIC
# MAGIC - **Traditional SQL Functions**
# MAGIC     - Designed for direct programmatic use by developers
# MAGIC     - Limited or minimal documentation requirements
# MAGIC     - Called explicitly with known parameters
# MAGIC     - Focus on computational efficiency and performance
# MAGIC
# MAGIC - **Unity Catalog SQL Functions as Agent Tools**
# MAGIC     - Designed for dynamic discovery and use by AI agents
# MAGIC     - Rich metadata and comprehensive documentation required
# MAGIC     - Parameters and usage inferred from natural language queries
# MAGIC     - Focus on clarity, interpretability, and agent usability
# MAGIC     - Include business context and usage examples
# MAGIC
# MAGIC - **Key Difference**: Unity Catalog SQL Functions as Agent Tools must be "AI-readable" - they need sufficient metadata for an LLM to understand when and how to use them based on user intent.
# MAGIC
# MAGIC ![sql-fun-vs-agent-tool.png](./Includes/images/sql-fun-vs-agent-tool.png "sql-fun-vs-agent-tool.png")

# COMMAND ----------

# MAGIC %md
# MAGIC ### A3. The Role of Unity Catalog SQL Functions as Agent Tools in Agent Architectures
# MAGIC
# MAGIC Unity Catalog SQL Functions as Agent Tools serve a specific and important role in the broader agent architecture:
# MAGIC
# MAGIC 1. **Data Access Layer**
# MAGIC     - Provide structured access to enterprise data through Unity Catalog
# MAGIC     - Enable real-time querying of current data states
# MAGIC     - Maintain data governance and security policies
# MAGIC 1. **Business Logic Implementation**
# MAGIC     - Encapsulate domain-specific calculations and aggregations
# MAGIC     - Implement consistent business rules across agent interactions
# MAGIC     - Provide standardized analytical operations
# MAGIC 1. **Governance and Compliance**
# MAGIC     - Security is enforced via UC privileges, masking policies, and dynamic views over govered assets. 
# MAGIC     - UC UDFs can be securly shared and govered across computing environemnts
# MAGIC     - Agent tools inherit UC governance

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. Architecture of Unity Catalog SQL Functions as Agent Tools

# COMMAND ----------

# MAGIC %md
# MAGIC ### B1. Unity Catalog Integration
# MAGIC
# MAGIC Unity Catalog SQL Functions as Agent Tools are built on Unity Catalog's function registry, which provides the foundation for enterprise-grade tool management:
# MAGIC
# MAGIC - **Three-Level Namespace**
# MAGIC     - **Catalog**: Top-level container for organizing functions by domain or business unit
# MAGIC     - **Schema**: Secondary grouping for related functions and data assets
# MAGIC     - **Function**: Individual SQL functions that serve as agent tools
# MAGIC
# MAGIC - **Metadata Management**
# MAGIC     - Function signatures with parameter types and descriptions
# MAGIC     - Comprehensive documentation and usage examples
# MAGIC     - Documented versioning via COMMENT/docstring and auti via system logs
# MAGIC
# MAGIC - **Security and Access Control**
# MAGIC     - Fine-grained permissions using ANSI SQL GRANT statements
# MAGIC     - Integration with workspace identity and access management
# MAGIC     - Secure execution environments for function calls
# MAGIC     - Audit logging for function usage and access patterns

# COMMAND ----------

# MAGIC %md
# MAGIC ### B2. Function Registration Methods
# MAGIC
# MAGIC Unity Catalog provides a couple approaches for registering SQL functions as agent tools.
# MAGIC
# MAGIC #### **Direct SQL Registration**
# MAGIC Using [`CREATE OR REPLACE FUNCTION` statements](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-syntax-ddl-create-sql-function):
# MAGIC - Immediate registration and availability
# MAGIC - Full control over function definition and metadata
# MAGIC - Integration with existing SQL development workflows
# MAGIC - Support for complex SQL logic and business rules
# MAGIC
# MAGIC #### **Programmatic Registration**
# MAGIC Using the [`DatabricksFunctionClient()`](https://docs.unitycatalog.io/ai/client/#databricks-function-client):
# MAGIC - Automated function creation and management
# MAGIC - Integration with CI/CD pipelines and deployment workflows
# MAGIC - Batch operations for managing multiple functions
# MAGIC - Dynamic function generation based on data schemas
# MAGIC - Supports serverless (production) and local (dev) modes, though local mode does [not support SQL-based functions](https://docs.databricks.com/aws/en/generative-ai/agent-framework/create-custom-tool)
# MAGIC
# MAGIC Both methods ensure that functions are properly documented, versioned, and accessible to AI agents while maintaining governance standards.

# COMMAND ----------

# MAGIC %md
# MAGIC ### B3. (Optional) Execution Environment Considerations
# MAGIC To read more about technical considerations (serverless vs local mode) for UC Python functions, please see [this documentation](https://docs.databricks.com/aws/en/generative-ai/agent-framework/create-custom-tool#running-functions-using-serverless-or-local-mode). 

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Best Practices When Designing SQL Tools

# COMMAND ----------

# MAGIC %md
# MAGIC ### C1. Function Documentation and Metadata
# MAGIC
# MAGIC Effective Unity Catalog SQL Functions as Agent Tools require comprehensive documentation that enables AI agents to understand their purpose and usage. We break this down into three essential documentation layers as follows: 
# MAGIC
# MAGIC #### Function-Level Documentation
# MAGIC - Clear, concise description of the function's business purpose
# MAGIC - Explanation of what the function calculates or retrieves
# MAGIC - Context about when and why the function should be used
# MAGIC - Examples of typical use cases and scenarios
# MAGIC
# MAGIC #### Parameter-Level Documentation
# MAGIC - Descriptive parameter names that indicate their purpose
# MAGIC - Data type specifications with appropriate constraints
# MAGIC - Clear descriptions of expected values and formats
# MAGIC - Examples of valid parameter values
# MAGIC
# MAGIC #### Return-Value-Level Documentation
# MAGIC - Clear specification of return data types
# MAGIC - Description of what the returned value represents
# MAGIC - Explanation of units, formats, or special meanings
# MAGIC - Handling of edge cases and null values
# MAGIC
# MAGIC #### UI Validation
# MAGIC Once your function has been registered to Unity Catalog, you can validate the meta information the LLM will consume for context and query filtering for specific keywords. 
# MAGIC
# MAGIC ![Screenshot 2025-11-18 at 3.34.34 PM.png](./Includes/images/sql-func-validation.png "Screenshot 2025-11-18 at 3.34.34 PM.png")
# MAGIC
# MAGIC <p align="center"><em>An example of a SQL UC function that has been registered with LLM-friendly notes for context and usage. </em></p>

# COMMAND ----------

# MAGIC %md
# MAGIC ### C2. Function Design Principles
# MAGIC
# MAGIC Unity Catalog SQL Functions as Agent Tools should follow specific design principles to maximize their effectiveness with AI agents. Here are some core principles you should keep in mind when building production-ready tools: 
# MAGIC
# MAGIC - **Single Responsibility**: Each function should perform one specific, well-defined task. Avoid combining multiple unrelated operations in a single function. 
# MAGIC
# MAGIC - **Predictable Behavior**: Functions should be deterministic when possible and handle edge cases gracefully with appropriate error messages. 
# MAGIC     - _Error handling and validation:_ design functions and processes to include input validate and data quality checks. 
# MAGIC
# MAGIC - **Intuitive Parameters**: Use parameter names that match natural language and minimize the number of required parameters.
# MAGIC
# MAGIC - **Business Context**: Align function names with business terminology and concepts that include domain-specific knowledge in function logic. 

# COMMAND ----------

# MAGIC %md
# MAGIC ## D. Integration with AI Playground and Agent Frameworks

# COMMAND ----------

# MAGIC %md
# MAGIC ### D1. AI Playground Integration
# MAGIC
# MAGIC AI Playground provides a no-code interface for testing and prototyping Unity Catalog SQL Functions as Agent Tools:
# MAGIC
# MAGIC #### Tool Discovery
# MAGIC - Automatic discovery of UC functions available to the current user when selecting a tool with an appropriate LLM like Claude 4
# MAGIC - Searchable interface for finding relevant tools
# MAGIC - Metadata display for understanding tool capabilities
# MAGIC - Permission-aware tool listing based on access controls
# MAGIC
# MAGIC #### Dynamic Tool Selection
# MAGIC - AI-powered matching of user queries to appropriate tools
# MAGIC - Intelligent parameter extraction from natural language
# MAGIC - Multi-tool orchestration for complex queries
# MAGIC - Real-time tool execution and result integration
# MAGIC
# MAGIC #### Testing and Validation
# MAGIC - Interactive testing of tool functionality
# MAGIC - Inspection of tool execution and parameter passing
# MAGIC - Debugging support for tool behavior and results
# MAGIC - Performance monitoring and optimization insights![Screenshot 2025-11-18 at 3.40.46 PM.png](./Includes/images/ai-playground-tools.png "Screenshot 2025-11-18 at 3.40.46 PM.png")
# MAGIC
# MAGIC <p align="center"><em> In the AI Playgound, some models have the ability to add tools, like GPT-5.1 for example. </em></p>

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusion
# MAGIC
# MAGIC Unity Catalog SQL Functions as Agent Tools transform how AI agents interact with enterprise data by providing a governed, discoverable, and self-describing interface to your data operations. The key differentiators (comprehensive metadata, business-context documentation, and Unity Catalog's security model) enable agents to make intelligent decisions about when and how to use these tools. As you move into the demonstration, consider what types of business questions your organization's stakeholders ask most frequently—these often make the best candidates for Unity Catalog SQL Functions as Agent Tools.
# MAGIC
# MAGIC ## Next Steps
# MAGIC Continue to the [next demonstration]($./2 Demo - Building SQL Agent Tools with AI Playground) where you will build SQL functions, register them in Unity Catalog, and test them using AI Playground to create an interactive agent that can answer questions about data.

# COMMAND ----------

# MAGIC %md
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> |
# MAGIC <a href="https://help.databricks.com/" target="blank">Terms of Use</a> |
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>