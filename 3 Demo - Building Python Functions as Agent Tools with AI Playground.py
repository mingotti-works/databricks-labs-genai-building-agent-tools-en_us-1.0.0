# Databricks notebook source
# MAGIC %md
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # Demo - Building Python Functions as Agent Tools with AI Playground
# MAGIC ## Overview
# MAGIC
# MAGIC This demonstration focuses on how to create Unity Catalog (UC) Python-based functions that can be leveraged as tools by AI agents/provided as tools to AI agents. 
# MAGIC
# MAGIC Modern AI applications require agents that can interact with data and perform complex analytical tasks. By leveraging Unity Catalog's function registry with Python functions, you can create robust, scalable solutions that combine the governance and security of UC with the computational power of Python for AI agents. 
# MAGIC
# MAGIC Python functions enable advanced data processing, statistical analysis, and integration with external libraries that would be difficult or impossible with SQL alone. In this demo, you'll learn how to build a practical Python-based tool that extracts and analyzes Airbnb listing information, register it in Unity Catalog, and deploy it as an agent tool in AI Playground.
# MAGIC
# MAGIC ### Learning Objectives
# MAGIC
# MAGIC _By the end of this demo, you will be able to:_
# MAGIC
# MAGIC 1. Create and register Python functions in Unity Catalog for agent use cases using both Python syntax and `DatabricksFunctionClient()`
# MAGIC 2. Perform initial testing of your UC Python functions at the notebook level
# MAGIC 3. Understand how to equip Python functions with proper context and documentation for AI agent use cases
# MAGIC 4. Test your UC Python functions using AI Playground
# MAGIC 5. Identify when a Python tool has been used and understand how the agent utilized the tool in AI Playground
# MAGIC
# MAGIC **Note:** This demonstration focuses on building UC Python functions and implementing best practices for agent tools that can be tested and deployed using AI Playground. _It does not cover more advanced frameworks like DSPy or LangChain._

# COMMAND ----------

# MAGIC %md
# MAGIC ## A. Classroom Setup
# MAGIC
# MAGIC Run the following cell to configure your working environment for this notebook.

# COMMAND ----------

# MAGIC %md
# MAGIC ### A1. Compute Requirements
# MAGIC
# MAGIC **🚨 REQUIRED - SELECT SERVERLESS COMPUTE**
# MAGIC
# MAGIC This course has been configured to run on Serverless compute. While classic compute may also work, testing has been performed on serverless
# MAGIC
# MAGIC This demo was tested using version 4 of Serverless compute. To ensure that you are using the correct version of Serverless, please navigate to the **Environment** button on the right and open it (see screenshot below). 
# MAGIC
# MAGIC ![optional alt text](./Includes/images/serverless-version.png)

# COMMAND ----------

# MAGIC %md
# MAGIC ### A2. Installed Dependencies
# MAGIC
# MAGIC As part of the workspace setup, some Python libraries have been installed. For completeness, we will go over the key package:
# MAGIC
# MAGIC 1. `unitycatalog-ai[databricks]`: This package provides infrastructure and tooling for creating and managing UC functions (both SQL and Python UDFs) that can be used as tools by agents.
# MAGIC
# MAGIC This demonstration uses AI Playground to test our functions, which provides a no-code interface for prototyping tool-calling agents. See the [Unity Catalog Tool Integration documentation](https://docs.databricks.com/aws/en/generative-ai/agent-framework/unity-catalog-tool-integration) for more details for advanced framework integration.

# COMMAND ----------

# MAGIC %run ./Includes/Classroom-Setup-Common

# COMMAND ----------

# MAGIC %md
# MAGIC **🚨 NOTE:** You will need to update the following cell to your catalog name. The schema name will be created automatically for you based on the course name.
# MAGIC
# MAGIC **🚨 NOTE:** If you are using **Vocareum**, your catalog has already been configured for you and is of the form **labuserXXX_XXX**, which matches your Vocareum username. You should set this as your catalog name.
# MAGIC > Example: catalog_name = "labuser31415926_5358979323"
# MAGIC
# MAGIC The catalog and schema variables are used throughout this notebook when referencing Unity Catalog assets.

# COMMAND ----------

# Used when needing to pass catalog/schema name with Python
catalog_name = "labuser14506312_1775100548"
schema_name = "genai_agent_tools"
dev_lab_setup(catalog_name, schema_name) # Store the catalog and schema as catalog_name and schema_name

# COMMAND ----------

# MAGIC %md
# MAGIC ### A3. Our Data
# MAGIC This demonstration relies on the Airbnb dataset from Databricks Marketplace. Note that you may already have access to the Airbnb dataset.
# MAGIC #### Vocareum: You have access
# MAGIC If you launched this demo in a Vocareum environemnt, you will automatically have access to the Delta share. It is called `dbacademy_airbnb_sample_data`. For Vocareum users, you will set 
# MAGIC >`databricks_share_name=dbacademy_airbnb_sample_data`. 
# MAGIC #### Non-Vocareum: Check if you have access
# MAGIC Check in the **Catalog Explorer** by searching for `databricks_airbnb_sample_data`. Provided you have the proper level of permisisons on this delta share, you can update the next cell to read 
# MAGIC >`databricks_share_name=databricks_airbnb_sample_data`. 
# MAGIC
# MAGIC ##### I don't have access/can't see the dataset
# MAGIC If you don't have access or can't see the dataset in your **Catalog Explorer**, the next set of instructions will help walk you through how to get this dataset in your workspace.
# MAGIC
# MAGIC 1. Navigate to Marketplace and search **Airbnb Sample Data** and click on the tile that reads **Airbnb Sample Data**.
# MAGIC 1. Next, click **Get instant access** and follow the on-screen instructions to bring that dataset in.
# MAGIC 1. Create a unique Databricks share name. If a name is already in use, you will need to use a different name. Copy the same name into the cell below. For example:
# MAGIC >`databricks_share_name=<unique_name>`. 

# COMMAND ----------

## TODO
databricks_share_name = "dbacademy_airbnb_sample_data" # Delta share name

# COMMAND ----------

# MAGIC %md
# MAGIC 1. As a part of the classroom setup, a helper function has been configured for you process the dataset from the Delta share. Run the cell to process the CSV `sf-airbnb.csv` from the Airbnb Delta share volume `v01`. 

# COMMAND ----------

df = process_csv(databricks_share_name)

# COMMAND ----------

# MAGIC %md
# MAGIC ### A4. Initialize the Databricks Function Client
# MAGIC
# MAGIC Initialize the [Databricks Function Client](https://github.com/unitycatalog/unitycatalog/tree/b2d072e56661aedb84cce9be60292b2c54e12224/ai/core#databricks-managed-uc), which is a specialized interface for creating, managing, and running UC functions in Databricks. 
# MAGIC
# MAGIC For building agent tools with the open source UC library, please see [this documentation](https://docs.unitycatalog.io/ai/client/#databricks-function-client). This demonstration will focus on leveraging Databricks-managed UC for building SQL agent tools.

# COMMAND ----------

from unitycatalog.ai.core.databricks import DatabricksFunctionClient

# client = DatabricksFunctionClient() # For classic compute
client = DatabricksFunctionClient(execution_mode="serverless") # For serverless compute

# COMMAND ----------

# MAGIC %md
# MAGIC ## B. Define and Register UC Python Functions
# MAGIC
# MAGIC Before digging into the code, it's important to understand some terminology:
# MAGIC
# MAGIC - Any function registered via Unity Catalog, regardless of being written in SQL or Python, is considered a **user-defined function (UDF)**
# MAGIC - **Python functions** leverage the full computational power of Python, including access to libraries like pandas, numpy, scipy, and custom packages
# MAGIC
# MAGIC In this notebook we will use the term **Python function** or **function** to mean a function that is or will be registered to UC, hence a Python UDF. 
# MAGIC
# MAGIC > For more information on UDFs in Unity Catalog, please see [this documentation](https://docs.databricks.com/aws/en/udf/unity-catalog).
# MAGIC
# MAGIC In the code snippets below, we will show different ways to register a Python-based UDF and query from UC. Ultimately, you should use whatever methods you're most comfortable with.

# COMMAND ----------

# MAGIC %md
# MAGIC 1. First, let's drop any existing functions with the same name as what will be created below.

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP FUNCTION IF EXISTS airbnb_posting_info;
# MAGIC DROP FUNCTION IF EXISTS airbnb_posting_info_sql;

# COMMAND ----------

# MAGIC %md
# MAGIC ### B1. Best Practices for Python Agent Tools
# MAGIC
# MAGIC #### Required Practices
# MAGIC
# MAGIC 1. **Explicit type hints**: Always provide valid Python type hints for all arguments and return values. This is required by the UC function model and helps both automation and LLMs to correctly infer input/output expectations
# MAGIC 1. **No variable arguments**: Do not use `*args` or `**kwargs`. All parameters should be explicitly named and typed
# MAGIC 1. **Supported data types**: Ensure input and output types are supported by both Python and Databricks SQL/Spark type systems. Refer to the Spark Supported Data Types documentation ([Databricks docs](https://docs.databricks.com/aws/en/generative-ai/agent-framework/create-custom-tool) and [Spark docs](https://spark.apache.org/docs/latest/sql-ref-datatypes.html)) to avoid incompatibility
# MAGIC 1. **Write comprehensive docstrings**: Use [Google-style formatting](https://google.github.io/styleguide/pyguide.html#383-functions-and-methods), clearly defining what the function does, each argument, and the return value. The function docstring is parsed to generate tool metadata that LLMs and agents use for routing
# MAGIC     - Make meaningful, precise descriptions that help the LLM understand when to use the tool
# MAGIC 1. **Import libraries inside the function**: If your function requires external libraries, import them _inside_ the function body. Imports outside the function are not resolved at runtime when the function is called as a tool

# COMMAND ----------

# MAGIC %md
# MAGIC ### B2. Python Tool: Extract Airbnb Listing Information
# MAGIC
# MAGIC In this demonstration, we will create a single function that does the following:
# MAGIC
# MAGIC 1. Fetches the HTML content from an Airbnb posting using the listing ID
# MAGIC 2. Extracts and parses key information including the description, number of reviews, and rating
# MAGIC 3. Returns formatted text that can be easily consumed by an AI agent
# MAGIC
# MAGIC We will demonstrate this using two registration methods:
# MAGIC
# MAGIC 1. **Pure Python approach**: Define the function in Python and register it using `DatabricksFunctionClient()`
# MAGIC 2. **SQL wrapper approach**: Wrap the Python function in SQL syntax using `CREATE OR REPLACE FUNCTION`
# MAGIC
# MAGIC Both approaches produce the same result, so choose the one that fits your workflow best.

# COMMAND ----------

def airbnb_posting_info(id: int) -> str:
    """
    Fetches Airbnb posting information as formatted text.

    Args:
        id (int): Airbnb listing ID (e.g., 958)

    Returns:
        str: Formatted listing information (description, reviews, and rating) or error message
    """
    import requests
    import re

    api_url = f"https://www.airbnb.com/rooms/{id}"
    
    try:
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            html = response.text
            
            # Extract description
            desc = re.search(r'"metaDescription":"([^"]+)"', html)
            if desc:
                description = desc.group(1).replace('\\n', ' ')
                parts = description.split(' · ')
                description = ' · '.join(parts[2:]) if len(parts) > 2 else description
            else:
                description = "Description not found"
            
            # Extract review count and rating
            reviews = re.search(r'"reviewCount":(\d+)', html)
            rating = re.search(r'"starRating":([\d.]+)', html)
            
            reviews = reviews.group(1) if reviews else "N/A"
            rating = rating.group(1) if rating else "N/A"
            
            return f"""Description: {description}

Reviews: {reviews}
Rating: {rating} stars"""
        else:
            return f'Request failed with status code: {response.status_code}'
    
    except requests.exceptions.RequestException as e:
        return f'Request error: {str(e)}'

# COMMAND ----------

# MAGIC %md
# MAGIC ### B3. Test the Function at Notebook Level
# MAGIC
# MAGIC Before registering the function to Unity Catalog, it's important to test it at the notebook level to ensure it works as expected. This allows you to catch any errors early and validate the output format.

# COMMAND ----------

info = airbnb_posting_info(958)
print(info)

# COMMAND ----------

# MAGIC %md
# MAGIC ### B4. Register the Tool Using `DatabricksFunctionClient()`
# MAGIC
# MAGIC Now that we've validated our function works correctly, we can register it to Unity Catalog using the `DatabricksFunctionClient`. 
# MAGIC
# MAGIC We use `client.create_python_function()` and pass the following parameters:
# MAGIC
# MAGIC - **`func`**: The Python function object we just created (`airbnb_posting_info`)
# MAGIC - **`catalog`**: The catalog name, which we stored earlier as `catalog_name`
# MAGIC - **`schema`**: The schema name, which we stored earlier as `schema_name`
# MAGIC - **`replace`**: Set to `True` to overwrite the stored Python function if it already exists

# COMMAND ----------

function_info = client.create_python_function(
  func=airbnb_posting_info,
  catalog=catalog_name,
  schema=schema_name,
  replace=True
)

# COMMAND ----------

# MAGIC %md
# MAGIC ### B5. Register the Tool Using SQL
# MAGIC
# MAGIC We can also use SQL syntax to create the function `airbnb_posting_info_sql` by wrapping it in a `CREATE OR REPLACE FUNCTION` statement. 
# MAGIC
# MAGIC Here are the key syntax elements for creating a Python UDF with SQL:
# MAGIC
# MAGIC 1. **Add comments**: Include a `COMMENT` for the input parameter `id` and the function itself to prepare for tool calling in AI Playground
# MAGIC 2. **Return type**: Specify a supported [SQL datatype](https://docs.databricks.com/aws/en/sql/language-manual/sql-ref-datatypes) (in this case, `STRING`)
# MAGIC 3. **Designate language**: Use `LANGUAGE PYTHON` to indicate this is a Python UDF
# MAGIC 4. **Code delimiters**: Wrap the Python code in `$$` delimiters
# MAGIC 5. **Return statement**: End the Python code block with `return` and call the Python function

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE FUNCTION airbnb_posting_info_sql(
# MAGIC     id INT COMMENT "The Airbnb posting ID"
# MAGIC ) 
# MAGIC RETURNS STRING 
# MAGIC LANGUAGE PYTHON 
# MAGIC COMMENT "Fetches formatted Airbnb listing information including description, reviews, and rating."
# MAGIC AS $$
# MAGIC     def airbnb_posting_info(id):
# MAGIC         """
# MAGIC         Fetches Airbnb posting information as formatted text.
# MAGIC
# MAGIC         Args:
# MAGIC             id (int): Airbnb listing ID (e.g., 958)
# MAGIC
# MAGIC         Returns:
# MAGIC             str: Formatted listing information (description, reviews, and rating) or error message
# MAGIC         """
# MAGIC         import requests
# MAGIC         import re
# MAGIC
# MAGIC         api_url = f"https://www.airbnb.com/rooms/{id}"
# MAGIC
# MAGIC         try:
# MAGIC             response = requests.get(api_url, timeout=10)
# MAGIC             
# MAGIC             if response.status_code == 200:
# MAGIC                 html = response.text
# MAGIC                 
# MAGIC                 # Extract description
# MAGIC                 desc = re.search(r'"metaDescription":"([^"]+)"', html)
# MAGIC                 if desc:
# MAGIC                     description = desc.group(1).replace('\\n', ' ')
# MAGIC                     parts = description.split(' · ')
# MAGIC                     description = ' · '.join(parts[2:]) if len(parts) > 2 else description
# MAGIC                 else:
# MAGIC                     description = "Description not found"
# MAGIC                 
# MAGIC                 # Extract review count and rating
# MAGIC                 reviews = re.search(r'"reviewCount":(\d+)', html)
# MAGIC                 rating = re.search(r'"starRating":([\d.]+)', html)
# MAGIC                 
# MAGIC                 reviews = reviews.group(1) if reviews else "N/A"
# MAGIC                 rating = rating.group(1) if rating else "N/A"
# MAGIC                 
# MAGIC                 return f"""Description: {description}
# MAGIC
# MAGIC Reviews: {reviews}
# MAGIC Rating: {rating} stars"""
# MAGIC             else:
# MAGIC                 return f'Request failed with status code: {response.status_code}'
# MAGIC
# MAGIC         except requests.exceptions.RequestException as e:
# MAGIC             return f'Request error: {str(e)}'
# MAGIC     return airbnb_posting_info(id)
# MAGIC $$

# COMMAND ----------

# MAGIC %md
# MAGIC ### B6. Test the Tool with `DatabricksFunctionClient()`
# MAGIC
# MAGIC Next, let's test the Python-based function using the `execute_function()` API. Notice we can execute both the Python-registered function and the SQL wrapper version. Both approaches should produce the same results since they contain identical Python code.

# COMMAND ----------

result = client.execute_function(
    function_name=f"{catalog_name}.{schema_name}.airbnb_posting_info",
    parameters={
        "id": 958
    }
)

print(result.value)

# COMMAND ----------

result = client.execute_function(
    function_name=f"{catalog_name}.{schema_name}.airbnb_posting_info_sql",
    parameters={
        "id": 958
    }
)

print(result.value)

# COMMAND ----------

# MAGIC %md
# MAGIC ### B7. Test the Tool with SQL Syntax
# MAGIC
# MAGIC We can also test both of our functions using SQL syntax. Since both functions contain the same Python code, we expect identical results.

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT airbnb_posting_info(958) AS listing_info

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT airbnb_posting_info_sql(958) AS listing_info

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Testing Python Tools with AI Playground
# MAGIC
# MAGIC Now that we have created and tested our Python functions, we can use them as tools in AI Playground to create an interactive agent. AI Playground provides a no-code interface for testing how LLMs interact with your custom tools.

# COMMAND ----------

# MAGIC %md
# MAGIC ### C1. Navigate to AI Playground
# MAGIC
# MAGIC To test your Python functions as agent tools in AI Playground:
# MAGIC
# MAGIC 1. Navigate to **Playground** from your Databricks workspace
# MAGIC 2. Select a model with the **Tools enabled** label (e.g., `GPT OSS 120B` or another tool-capable model) from the model selection dropdown menu at the top of the Playground
# MAGIC 3. Click **Use endpoint** to begin your session

# COMMAND ----------

# MAGIC %md
# MAGIC ### C2. Attaching Tools to Your Agent
# MAGIC
# MAGIC Before we attach any tools, let's demonstrate the limitation. Try asking this question in AI Playground:
# MAGIC
# MAGIC > "Out of the following IDs, tell me which one has the highest rating: 958, 5858"
# MAGIC
# MAGIC The response you receive will be something like:
# MAGIC
# MAGIC > "I don't have access to specific data about Airbnb listings or their ratings. To answer this question, I would need access to a dataset containing this information. Could you provide the data or let me know where I can access it?"
# MAGIC
# MAGIC Now, let's fix that by adding our Python function as a tool:
# MAGIC
# MAGIC 1. Click **Tools > + Add tool**
# MAGIC 2. Under **UC Function**, select **Hosted Function** as the tool type
# MAGIC 3. Select the function you created: `airbnb_posting_info` or `airbnb_posting_info_sql`
# MAGIC 4. Click **Save** at the bottom right
# MAGIC 5. Validate that the tool is equipped. You should see **Tools (1)** in the **Tools** dropdown menu

# COMMAND ----------

# MAGIC %md
# MAGIC ### C3. Inspecting Tool Usage
# MAGIC
# MAGIC Now that we have our tool attached, let's examine how we can inspect that the tool was properly used. If it wasn't used correctly, we can always go back to our function definition and improve the docstring to help the LLM recognize when the tool should be used.
# MAGIC
# MAGIC #### Checking what the agent has access to
# MAGIC Before sending actual queries for the use case, you can check to see what your agent has access to with something like 
# MAGIC > What tools can you use?
# MAGIC or 
# MAGIC > What tools do you have access to?
# MAGIC
# MAGIC You will see a response that lists all the tools available (it should list the two we attached).
# MAGIC
# MAGIC #### Begin sending questions
# MAGIC After validating the tool has been equipped, let's ask our question again:
# MAGIC
# MAGIC > "Out of the following IDs, tell me which one has the highest rating: 958, 5858"
# MAGIC
# MAGIC You can now see the reasoning of the agent in the output. It will show something like:
# MAGIC
# MAGIC >  "Explain in detail why you are going to use this tool": "We need to retrieve the Airbnb posting information, specifically the rating, for listing ID 958 in order to compare it with the rating of listing ID 5858 and determine which has the higher rating."
# MAGIC
# MAGIC Followed by the JSON object showing the function calls:
# MAGIC
# MAGIC ```json
# MAGIC {
# MAGIC   "id": 958
# MAGIC }
# MAGIC ```
# MAGIC and 
# MAGIC ```json
# MAGIC {
# MAGIC   "id": 5858
# MAGIC }
# MAGIC ```
# MAGIC
# MAGIC The agent will then interpret the results and provide a natural language response like:
# MAGIC
# MAGIC > "Listing 958 has the higher rating.
# MAGIC > - ID 958: 4.89 stars (501 reviews)
# MAGIC > - ID 5858: 4.87 stars (105 reviews)
# MAGIC > 
# MAGIC > Therefore, the listing with ID 958 holds the higher rating."
# MAGIC
# MAGIC #### Try These Additional Questions
# MAGIC
# MAGIC - "What is the description of listing 958?"
# MAGIC - "Which listing has more reviews: 958 or 5858?"
# MAGIC - "Compare the ratings of listings 958, 5858, and 1234"
# MAGIC
# MAGIC **Note**: You can add up to 20 tools to your agent. The LLM will automatically select the appropriate tool(s) based on the user's query.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusion
# MAGIC
# MAGIC You've now learned how to bridge the gap between advanced data analytics and AI agents by creating Python-based functions in Unity Catalog. Throughout this demonstration, you've gained hands-on experience with:
# MAGIC
# MAGIC - **Building UC Python functions** for AI agents with proper documentation and type hints
# MAGIC - **Leveraging Python's advantages** including external API calls, text processing, and complex data parsing
# MAGIC - **Testing your functions** through both the `DatabricksFunctionClient()` and SQL syntax
# MAGIC - **Deploying and testing agent tools** in AI Playground
# MAGIC - **Monitoring agent behavior** to identify when and how Python tools are utilized during agent interactions
# MAGIC
# MAGIC The Python function you've created demonstrates capabilities that would be difficult or impossible to achieve with SQL alone, including making HTTP requests, parsing HTML content with regular expressions, and formatting complex text outputs for agent consumption.

# COMMAND ----------

# MAGIC %md
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>