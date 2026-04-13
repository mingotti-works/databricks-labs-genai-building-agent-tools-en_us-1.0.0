# Databricks notebook source
# MAGIC %md
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">

# COMMAND ----------

# MAGIC %md
# MAGIC # Lecture - Unity Catalog Python Functions as Agent Tools on Databricks
# MAGIC
# MAGIC ## Overview
# MAGIC
# MAGIC Building on the SQL agent tools concepts from the [previous lecture]($./1 Lecture - SQL Agent Tools on Databricks), this session focuses on Unity Catalog Python-based functions as agent tools within the Databricks platform. While SQL agent tools excel at data querying and analysis, Unity Catalog Python-based functions as agent tools provide the flexibility to implement complex business logic, integrate with external APIs, and perform advanced computations that extend beyond SQL's capabilities.
# MAGIC
# MAGIC Unity Catalog Python-based functions as agent tools leverage Unity Catalog's function registry to create sophisticated tools that can execute custom Python code, handle complex data transformations, and integrate with external systems. Unlike SQL functions, Python functions offer greater flexibility in execution environments and debugging capabilities while maintaining the same governance and security standards.
# MAGIC
# MAGIC This lecture establishes the technical foundation for building production-ready Unity Catalog Python-based functions as agent tools that complement your SQL-based tools in comprehensive agent architectures.
# MAGIC
# MAGIC ### Learning Objectives
# MAGIC
# MAGIC _By the end of this lecture, you will be able to:_
# MAGIC
# MAGIC - Understand the differences between Unity Catalog Python-based functions and SQL agent tools and when to use each
# MAGIC - Implement Python functions with proper type hints and Google-style documentation for agent consumption
# MAGIC - Apply best practices for error handling, dependency management, and function design
# MAGIC - Register and test Unity Catalog Python-based functions using DatabricksFunctionClient
# MAGIC - Integrate Unity Catalog Python-based functions with AI Playground and agent frameworks using UCFunctionToolkit

# COMMAND ----------

# MAGIC %md
# MAGIC ## A. Understanding Unity Catalog Python-Based Functions as Agent Tools
# MAGIC Before getting started, it's important to keep in mind what UC functions are. Unity Catalog tools are really just Unity Catalog user-defined functions (UDFs) under the hood. When you define a Unity Catalog tool, you're registering a function in Unity Catalog. To learn more about Unity Catalog UDFs, see [this documentation](https://docs.databricks.com/aws/en/udf/unity-catalog). _Python UDFs registered as functions in Unity Catalog differ in scope and support from PySpark UDFs scoped to a notebook or SparkSession. See User-defined scalar functions - Python._
# MAGIC
# MAGIC ![python-function-diagram.png](./Includes/images/python-function-diagram.png "python-function-diagram.png")
# MAGIC <p align="center"><em> Similar to how SQL tools are used, the agent its brain to help reason and plan execution of UC Python tools. </em></p>

# COMMAND ----------

# MAGIC %md
# MAGIC ### A1. Python Tools vs SQL Tools
# MAGIC
# MAGIC While both Unity Catalog Python-based functions as agent tools and SQL agent tools serve as Unity Catalog functions that can be dynamically discovered by AI agents, they have distinct characteristics and use cases:
# MAGIC
# MAGIC **Unity Catalog Python-Based Functions as Agent Tools**
# MAGIC - Execute custom Python logic and complex computations
# MAGIC - Support integration with external APIs and libraries
# MAGIC - Offer flexible execution modes (serverless and local)
# MAGIC - Require explicit type hints and Google-style docstrings
# MAGIC - Support advanced error handling and debugging capabilities
# MAGIC
# MAGIC **SQL Tools**
# MAGIC - Optimized for data querying and analytical operations
# MAGIC - Limited to SQL syntax and built-in functions
# MAGIC - Execute only in serverless mode
# MAGIC - Require minimal documentation compared to Python functions
# MAGIC - Provide automatic query optimization and caching
# MAGIC
# MAGIC **Key Difference**: Unity Catalog Python-based functions as agent tools excel at implementing business logic and external integrations, while SQL tools are optimized for data access and analytical computations.
# MAGIC
# MAGIC **Combining Tools**: The combination of SQL and Python agent tools creates a powerful toolkit where SQL handles data querying and analysis while Python functions manage business logic, external integrations, and complex computations.

# COMMAND ----------

# MAGIC %md
# MAGIC ### A2. Registration and Documentation Requirements
# MAGIC
# MAGIC Unity Catalog Python-based functions as agent tools have specific requirements that differ from SQL functions:
# MAGIC
# MAGIC **Type Hints**
# MAGIC - All function parameters must have explicit type annotations
# MAGIC - Return types must be clearly specified
# MAGIC - Only Spark-supported data types are allowed
# MAGIC - Variable arguments (`*args`, `**kwargs`) are not supported
# MAGIC
# MAGIC **Google-Style Docstrings**
# MAGIC - Comprehensive function descriptions explaining business purpose
# MAGIC - Detailed parameter documentation with types and descriptions
# MAGIC - Clear return value specifications
# MAGIC - Usage examples and context for agent understanding
# MAGIC
# MAGIC **Dependency Management**
# MAGIC - All imports must be inside the function body
# MAGIC - Global module imports are not resolved during execution
# MAGIC - Functions must be self-contained with internal dependencies
# MAGIC
# MAGIC
# MAGIC ![python-tool-ui.png](./Includes/images/python-tool-ui.png "python-tool-ui.png")
# MAGIC <p align="center"><em> Users can validate their function has been successfully registered to UC using the UI. Above is an example of a simple function that adds two numbers. </em></p>

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. Registering Python Tools

# COMMAND ----------

# MAGIC %md
# MAGIC ### B1. `DatabricksFunctionClient` Integration
# MAGIC
# MAGIC Unity Catalog Python-based functions as agent tools are created and managed using the `DatabricksFunctionClient`, which provides a specialized interface for Unity Catalog function operations:
# MAGIC
# MAGIC **Function Registration**
# MAGIC - `create_python_function()` API accepts Python callables directly
# MAGIC - Automatic extraction of type hints and docstring metadata
# MAGIC - Integration with Unity Catalog's three-level namespace (`catalog.schema.function`)
# MAGIC - Support for function versioning and replacement
# MAGIC
# MAGIC **Execution Management**
# MAGIC - `execute_function()` API for testing and validation
# MAGIC - Configurable execution modes (serverless vs local)
# MAGIC - Parameter validation and type checking
# MAGIC - Definition caching and performance optimization
# MAGIC
# MAGIC **Security and Governance**
# MAGIC - Inherits Unity Catalog access controls and permissions
# MAGIC - Catalog-level operations logged
# MAGIC - Integration with workspace identity management

# COMMAND ----------

# MAGIC %md
# MAGIC ### B2. `UCFunctionToolkit` Integration
# MAGIC
# MAGIC The `UCFunctionToolkit` serves as the bridge between Unity Catalog functions and agent frameworks (see [this documentation](https://docs.databricks.com/aws/en/generative-ai/agent-framework/unity-catalog-tool-integration) for supported types). Just like when building SQL-based tools, use MLflow autologging with supported frameworks to automiatcally trace tool calls and agent execution.
# MAGIC
# MAGIC **Framework Compatibility**
# MAGIC - LangChain integration for agent orchestration
# MAGIC - Support for LlamaIndex, OpenAI, and Anthropic frameworks
# MAGIC - Standardized tool interfaces across different libraries
# MAGIC - Automatic tracing and monitoring capabilities
# MAGIC
# MAGIC **Tool Wrapping**
# MAGIC - Converts Unity Catalog functions into framework-compatible tools
# MAGIC - Handles parameter extraction from natural language queries
# MAGIC - Manages execution context and error handling
# MAGIC - Provides consistent tool behavior across frameworks
# MAGIC
# MAGIC **Performance Features**
# MAGIC - Function definition caching for improved performance
# MAGIC - Integration with MLflow for experiment tracking

# COMMAND ----------

# MAGIC %md
# MAGIC ### B3. (Optional) Execution Environment Considerations
# MAGIC To read more about technical considerations (serverless vs local mode) for UC Python functions, please see [this documentation](https://docs.databricks.com/aws/en/generative-ai/agent-framework/create-custom-tool#running-functions-using-serverless-or-local-mode). 

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Best Practices When Designing Python Tools
# MAGIC
# MAGIC Here we echo some items that were mentioned previously, but with explicit examples that will be useful when completing the demonstration that follows this lecture. In particular, we will look at
# MAGIC 1. Function structure and documentation
# MAGIC 1. Dependency management and Imports
# MAGIC 1. Error handling and validation

# COMMAND ----------

# MAGIC %md
# MAGIC ### C1. Function Structure and Documentation
# MAGIC
# MAGIC Effective Unity Catalog Python-based functions as agent tools require comprehensive structure and documentation that enables AI agents to understand their capabilities:
# MAGIC
# MAGIC **Function Signature Design**
# MAGIC - Use descriptive parameter names that match business terminology
# MAGIC - Implement explicit type hints for all parameters and return values
# MAGIC - Avoid complex nested types that may confuse agent reasoning
# MAGIC - Provide sensible parameter defaults where appropriate
# MAGIC
# MAGIC **Google-Style Docstring Requirements**
# MAGIC ```python
# MAGIC def calculate_customer_lifetime_value(customer_id: str, months: int = 12) -> float:
# MAGIC     """
# MAGIC     Calculates the projected lifetime value for a specific customer.
# MAGIC     
# MAGIC     Args:
# MAGIC         customer_id (str): Unique identifier for the customer
# MAGIC         months (int): Number of months to project (default: 12)
# MAGIC     
# MAGIC     Returns:
# MAGIC         float: Projected customer lifetime value in dollars
# MAGIC     """
# MAGIC ```
# MAGIC
# MAGIC **Business Context Integration**
# MAGIC - Include domain-specific knowledge in function logic
# MAGIC - Align function names with business processes and terminology
# MAGIC - Provide functions that answer common business questions
# MAGIC - Consider typical user workflows and use cases

# COMMAND ----------

# MAGIC %md
# MAGIC ### C2. Dependency Management and Imports
# MAGIC
# MAGIC Unity Catalog Python-based functions as agent tools have specific requirements for handling dependencies and imports:
# MAGIC
# MAGIC **Internal Import Requirements**
# MAGIC ```python
# MAGIC def process_customer_data(customer_id: str) -> dict:
# MAGIC     """Process customer data with external API integration."""
# MAGIC     # All imports must be inside the function
# MAGIC     import requests
# MAGIC     import json
# MAGIC     from datetime import datetime
# MAGIC     
# MAGIC     # Function logic here
# MAGIC     return result
# MAGIC ```
# MAGIC
# MAGIC **Library Compatibility**
# MAGIC - Use libraries available in the Databricks runtime environment
# MAGIC - Consider version differences between local and serverless execution
# MAGIC - Test functions in both execution modes when applicable
# MAGIC - Handle missing libraries gracefully with appropriate error messages
# MAGIC
# MAGIC **Performance Considerations**
# MAGIC - Minimize import overhead by importing only required modules
# MAGIC - Cache expensive computations within function scope
# MAGIC - Implement appropriate timeout handling for external API calls
# MAGIC - Consider memory usage for large data processing operations

# COMMAND ----------

# MAGIC %md
# MAGIC ### C3. Error Handling and Validation
# MAGIC
# MAGIC Robust Unity Catalog Python-based functions as agent tools implement comprehensive error handling and input validation:
# MAGIC
# MAGIC **Input Validation Patterns**
# MAGIC ```python
# MAGIC def validate_and_process(customer_id: str, amount: float) -> dict:
# MAGIC     """Validate inputs and process customer transaction."""
# MAGIC     if not customer_id or not customer_id.strip():
# MAGIC         raise ValueError("Customer ID cannot be empty")
# MAGIC     
# MAGIC     if amount <= 0:
# MAGIC         raise ValueError("Amount must be positive")
# MAGIC     
# MAGIC     # Processing logic here
# MAGIC ```
# MAGIC
# MAGIC **Exception Management**
# MAGIC - Use specific exception types for different error conditions
# MAGIC - Provide clear, actionable error messages for debugging
# MAGIC - Handle external API failures gracefully with fallback logic
# MAGIC - Log errors appropriately without exposing sensitive information
# MAGIC
# MAGIC **Resource Management**
# MAGIC - Implement proper cleanup for external connections
# MAGIC - Handle timeout scenarios for long-running operations
# MAGIC - Manage memory usage for large data processing
# MAGIC - Provide progress indicators for lengthy computations

# COMMAND ----------

# MAGIC %md
# MAGIC ## D. Production Deployment Considerations
# MAGIC
# MAGIC Moving Unity Catalog Python-based functions as agent tools from development to production requires careful consideration of execution environment differences:
# MAGIC
# MAGIC **Serverless Mode Requirements**
# MAGIC - Serverless generic compute must be enabled in the workspace
# MAGIC - Functions execute in isolated, managed compute environments
# MAGIC - Automatic scaling based on agent tool usage patterns
# MAGIC - Integration with Unity Catalog governance and security policies
# MAGIC
# MAGIC **Security and Compliance**
# MAGIC - Validate that functions don't expose sensitive information
# MAGIC - Implement proper access controls for external system integration
# MAGIC - Ensure compliance with data governance policies
# MAGIC
# MAGIC **Integration Testing Prior to Production Deployement with AI Playground**
# MAGIC - Similar to testing SQL functions in the AI playground, you can also test Python functions registered to Unity Catalog as well for interactive testing and agent workflow validation. 
# MAGIC

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusion
# MAGIC
# MAGIC Unity Catalog Python-based functions as agent tools provide powerful capabilities for extending AI agents beyond the limitations of SQL-based operations. By understanding the architecture, development workflows, and best practices covered in this lecture, you can build sophisticated agent tools that implement complex business logic, integrate with external systems, and provide flexible execution environments for both development and production use.
# MAGIC
# MAGIC ## Next Steps
# MAGIC Continue to the [next demonstration]($./4 Demo - Building Python Agent Tools with AI Playground) where you'll create Python functions with proper type hints and documentation, register them in Unity Catalog, and test them using AI Playground to create agents with advanced computational capabilities.

# COMMAND ----------

# MAGIC %md
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> |
# MAGIC <a href="https://help.databricks.com/" target="blank">Terms of Use</a> |
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>