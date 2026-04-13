# Databricks notebook source
# MAGIC %md
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning">

# COMMAND ----------

# MAGIC %md
# MAGIC # Demo - Building SQL Functions as Agent Tools with AI Playground
# MAGIC ## Overview
# MAGIC This demonstration focuses on how to create Unity Catalog (UC) SQL-based functions that can be leveraged as tools by AI agents/provided as tools to AI agents. 
# MAGIC
# MAGIC Modern AI applications require agents that can interact with data and perform analytical tasks. By leveraging Unity Catalog's function registry with SQL functions, you can create robust, scalable solutions that combine the governance and security of UC with the analytical power of SQL for AI agents.
# MAGIC
# MAGIC ### Learning Objectives
# MAGIC _By the end of this demo, you will be able to:_
# MAGIC - Using both SQL syntax and `DatabricksFunctionClient()`, you will 
# MAGIC     - Create and register SQL functions in Unity Catalog for Agent use cases
# MAGIC     - Perform initial testing of your UC SQL function
# MAGIC - Understand how to equip SQL functions with proper context for AI Agent use cases
# MAGIC - Test your UC SQL function using AI Playground
# MAGIC - Identify when a SQL tool has been used and understand how the agent utilized the tool in AI Playground
# MAGIC
# MAGIC **Note:** This demonstration focuses on building UC SQL functions and implementing best practices for agent tools that can be tested and deployed using AI Playground. _It does not cover more advanced frameworks like DSPy or LangChain._

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

# MAGIC %sql
# MAGIC USE CATALOG "labuser14506312_1775100548";
# MAGIC SELECT current_catalog();

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
# MAGIC ## B. Define and Register UC SQL Functions
# MAGIC
# MAGIC Before digging into the code, it's important to suss out some terminology. 
# MAGIC - Built-in functions like `SUM` and `AVG` are SQL functions, but these are specifically called **system functions**. However, a **SQL function** is any reusable computation that can be called in a SQL statement, even ones defined by users.
# MAGIC - Any function registered via Unity Catalog, regardless of being written in SQL or Python, is considered a **user-defined function (UDF)**.
# MAGIC
# MAGIC In this notebook we will use the term **SQL function** or **function** to mean a function that is or will be registered to UC, hence a SQL UDF. 
# MAGIC
# MAGIC > For more information on UDFs in Unity Catalog, please see [this documentation](https://docs.databricks.com/aws/en/udf/unity-catalog). 

# COMMAND ----------

# MAGIC %md
# MAGIC 1. First, let's drop any existing functions with the same name as what will be created below.

# COMMAND ----------

# MAGIC %sql
# MAGIC DROP FUNCTION IF EXISTS avg_neigh_price;
# MAGIC DROP FUNCTION IF EXISTS cnt_by_room_type;

# COMMAND ----------

# MAGIC %md
# MAGIC ### B1. SQL Tool 1: Airbnb Data Analysis
# MAGIC
# MAGIC We start by creating SQL functions that will serve as our agent tools for analyzing the San Francisco Airbnb listings data. These functions include proper documentation that will help the agent understand how to use them. This tool will be created with **SQL only**. 
# MAGIC
# MAGIC #### Recommendations for SQL Functions
# MAGIC The following SQL functions follow recommended practices:
# MAGIC 1. **Clear parameter names and types**: Use descriptive parameter names with appropriate SQL data types
# MAGIC 2. **Comprehensive comments**: Use `COMMENT` clauses for both the function and each parameter to provide clear descriptions
# MAGIC 3. **Deterministic behavior**: Mark functions as `DETERMINISTIC` when they always return the same result for the same inputs
# MAGIC 4. **Proper return type**: Explicitly specify the return data type
# MAGIC 5. **Error handling**: Consider edge cases like NULL values in the function logic

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE OR REPLACE FUNCTION avg_neigh_price(
# MAGIC   neighborhood_name STRING COMMENT "The neighborhood name to filter by (e.g., 'Mission', 'Upper Market')"
# MAGIC )
# MAGIC RETURNS DOUBLE
# MAGIC LANGUAGE SQL
# MAGIC DETERMINISTIC
# MAGIC COMMENT 'Calculates the average listing price for a specific neighborhood in San Francisco. Returns the average price as a numeric value. Price strings are cleaned and converted to numeric values before averaging.'
# MAGIC RETURN 
# MAGIC SELECT AVG(CAST(REGEXP_REPLACE(price, '[^0-9.]', '') AS DOUBLE))
# MAGIC FROM sf_airbnb_listings
# MAGIC WHERE neighbourhood_cleansed = neighborhood_name
# MAGIC   AND price IS NOT NULL
# MAGIC   AND REGEXP_REPLACE(price, '[^0-9.]', '') != ''

# COMMAND ----------

# MAGIC %md
# MAGIC ### B2. Tool 2: Property Analysis
# MAGIC
# MAGIC Let's create another useful function that counts properties by room type in a given neighborhood. This tool will leverage the `create_function()` API from `DatabricksFunctionClient()` that we instantiated earlier. We do this by 
# MAGIC 1. Converting the SQL query to a Python string called `sql_query`
# MAGIC 1. Pass that string to `create_function` by setting `sql_function_body=sql_query`

# COMMAND ----------

sql_query = f"""
CREATE OR REPLACE FUNCTION {catalog_name}.{schema_name}.cnt_by_room_type(
  neighborhood_name STRING COMMENT "The neighborhood name to filter by",
  room_type_filter STRING COMMENT "The room type to count (e.g., 'Private room' or 'Shared room')"
)
RETURNS BIGINT
LANGUAGE SQL
DETERMINISTIC
COMMENT 'Counts the number of Airbnb listings for a specific room type in a given neighborhood. Returns the count as an integer.'
RETURN
  SELECT COUNT(*)
  FROM {catalog_name}.{schema_name}.sf_airbnb_listings
  WHERE neighbourhood_cleansed = neighborhood_name
    AND room_type = room_type_filter
"""

sql_tool_2 = client.create_function(sql_function_body=sql_query)

# COMMAND ----------

# MAGIC %md
# MAGIC ### B4. Test Tool 1 Using SQL
# MAGIC
# MAGIC Let's verify that our SQL functions work correctly by testing them with various inputs directly in SQL. This helps ensure our functions behave as expected before integrating them with AI Playground. Here, we will test the first function using the syntax 
# MAGIC ```
# MAGIC SELECT <my_func>(my_variable)
# MAGIC AS <output_column_name>
# MAGIC ```
# MAGIC It's important to keep in mind that when leveraging LLMs with tool use, we want the LLM to be able to extract `my_variable` from our input prompt. For example, if we prompted 
# MAGIC
# MAGIC > Get the average price for the Mission neighborhood, please.
# MAGIC
# MAGIC then the LLM would use its set of tools (UC functions) to extract `Mission` and set it as `neighborhood_name` (as long as we have used some of the best practices mentioned earlier). 

# COMMAND ----------

# MAGIC %sql
# MAGIC -- Test average price function
# MAGIC SELECT avg_neigh_price('Mission') AS mission_avg_price

# COMMAND ----------

# MAGIC %md
# MAGIC ### B5. Test Tool 2 Using `DatabricksFunctionClient()`
# MAGIC
# MAGIC Now let's test our SQL functions using the `DatabricksFunctionClient()`. By first running a test where we know the input and output, we can more accurately evaluate the tool when sending a query to an agent using an LLM in the AI Playground. For example, with looking up the neighborhood name `Mission` and counting the number of `Private room` properties, the agent will be able to answer a question like 
# MAGIC > How many properties in Mission have a private room?
# MAGIC
# MAGIC Recall that `neighborhood_name` and `room_type_filter` are both input variables for the function `cnt_by_room_type()`.

# COMMAND ----------

# Test the count function
result = client.execute_function(
    function_name=f"{catalog_name}.{schema_name}.cnt_by_room_type",
    parameters={
        "neighborhood_name": "Mission",
        "room_type_filter": "Private room"
    }
)

print(f"Number of private rooms in Mission: {result.value}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## C. Testing SQL Tools with AI Playground
# MAGIC
# MAGIC Now that we have created and tested our SQL functions, we can use them as tools in AI Playground to create an interactive agent that can answer questions about San Francisco Airbnb listings.

# COMMAND ----------

# MAGIC %md
# MAGIC ### C1. Navigate to AI Playground
# MAGIC
# MAGIC To test your SQL functions as agent tools in AI Playground:
# MAGIC
# MAGIC 1. Navigate to **Playground** from your Databricks workspace
# MAGIC 1. Select a model with the **Tools enabled** label (e.g., `GPT OSS 20B`) from the model selection dropdown menu at the top of the **Playground**
# MAGIC 1. Click **Use endpoint**

# COMMAND ----------

# MAGIC %md
# MAGIC ### C2. Attaching Tools
# MAGIC As an example, before we attach any tools, let's ask the question from before: 
# MAGIC > How many properties in Mission have a private room?
# MAGIC
# MAGIC The response you receive will be something like 
# MAGIC
# MAGIC > I'm not sure which "Mission" you're referring to or which property listings you'd like to count. Could you let me know:
# MAGIC The city or region named Mission (e.g., Mission, Kansas; the Mission District in San Francisco; Mission, Bolivia, etc.)
# MAGIC The source of the property data (e.g., Airbnb listings, Zillow, a CSV table you have, etc.)
# MAGIC Any other details that would help identify the dataset or the exact definition of "private room" you're using.
# MAGIC With that information I can give you an accurate count.
# MAGIC
# MAGIC Now, let's fix that by adding tools. 
# MAGIC 1. Click **Tools > + Add tool**
# MAGIC 1. Under **UC Function**, click on **Hosted Function** as the tool type and select one of the two tools you created above. 
# MAGIC 1. Click **Save** at the bottom right. 
# MAGIC
# MAGIC > You should see **Tools (2)** in the **Tools** dropdown menu. 

# COMMAND ----------

# MAGIC %md
# MAGIC ### C3. Inspecting Tool Usage
# MAGIC Now that we have our tools attached, let's look at how we can inspect that the tool was properly used. If it wasn't we can always go back to our definition of the tool above and clear up our `COMMENT` clauses to push the LLM to recognize when the tool should be used. 
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
# MAGIC
# MAGIC After validating the tool has been equipped, let's ask our question again:
# MAGIC
# MAGIC > How many properties in Mission have a private room?
# MAGIC
# MAGIC You can now see the reasoning of the agent as the output. It will show something like 
# MAGIC
# MAGIC > We need to count the number of Airbnb listings that are private rooms within the Mission neighborhood. This matches the user's request to determine how many properties in Mission have a private room.
# MAGIC
# MAGIC Followed by the JSON object
# MAGIC ```
# MAGIC {
# MAGIC   "neighborhood_name": "Mission",
# MAGIC   "room_type_filter": "Private room"
# MAGIC }
# MAGIC ```
# MAGIC where we see the LLM extracted `Mission` and `Private room` from the query. In the JSON output, you will also see an icon to open the query up in the SQL Editor. You will also find the JSON output the LLM uses. It will look something like 
# MAGIC ```
# MAGIC {
# MAGIC   "is_truncated": false,
# MAGIC   "columns": [
# MAGIC     "output"
# MAGIC   ],
# MAGIC   "rows": [
# MAGIC     [
# MAGIC       250
# MAGIC     ]
# MAGIC   ]
# MAGIC }
# MAGIC ```
# MAGIC And then finally, it will return the answer as something like 
# MAGIC > In the Mission neighborhood, there are 250 properties that are listed as private rooms.
# MAGIC
# MAGIC Next, try asking an additional question that's related to the tools covered in this demo. 
# MAGIC
# MAGIC **Note**: You can add up to 20 tools to your agent. The LLM will automatically select the appropriate tool(s) based on the user's query.

# COMMAND ----------

# MAGIC %md
# MAGIC ## D. Best Practices and Additional Resources
# MAGIC
# MAGIC Once your tools have been tested, the next step is to revisit best practices to ensure reliable results. 
# MAGIC - Improve your tool's functionality with the `COMMENT` clause for both the description of the tool and its parameters. Refining these can lead to better results. 
# MAGIC - Be simple and granular with the expected inputs and outputs. 
# MAGIC     - Create focused functions that do one thing well
# MAGIC     - Avoid overly complex functions with too many parameters
# MAGIC     - Consider creating multiple simple functions rather than one complex function
# MAGIC - For general best practices on creating and testing UDFs, please read more [here](https://docs.databricks.com/aws/en/udf/unity-catalog#best-practices-for-udfs). 
# MAGIC
# MAGIC
# MAGIC Now that we have our SQL tool ready to be used with an LLM, we are ready to build a toolkit to embed in an agent framework. This step is not covered in this demonstration.
# MAGIC
# MAGIC #### Additional Resources
# MAGIC - For more reading about how to prototype a tool-calling AI agent with the AI Playground, please see [this link](https://docs.databricks.com/aws/en/generative-ai/agent-framework/ai-playground-agent)
# MAGIC - For more reading on choosing the proper tool approach, please see [this link](https://docs.databricks.com/aws/en/generative-ai/agent-framework/agent-tool)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Conclusion
# MAGIC
# MAGIC You've now learned how to begin closing the gap between data analytics and AI agents by creating SQL-based functions in Unity Catalog. Throughout this demonstration, you've gained hands-on experience with:
# MAGIC
# MAGIC - **Building UC SQL functions** for AI agents using both pure SQL syntax and properly documented approaches with metadata
# MAGIC - **Testing your functions** through multiple methods—direct SQL execution, the `DatabricksFunctionClient()`, and AI Playground
# MAGIC - **Monitoring agent behavior** to identify when and how SQL tools are utilized during agent interactions
# MAGIC
# MAGIC By combining Unity Catalog's governance framework with SQL's analytical capabilities, you're now equipped to build secure, scalable AI agent solutions that can intelligently interact with your data. These skills enable you to create production-ready agent tools following best practices that leverage both the security of UC and the power of SQL analytics.

# COMMAND ----------

# MAGIC %md
# MAGIC &copy; 2025 Databricks, Inc. All rights reserved. Apache, Apache Spark, Spark, the Spark Logo, Apache Iceberg, Iceberg, and the Apache Iceberg logo are trademarks of the <a href="https://www.apache.org/" target="blank">Apache Software Foundation</a>.<br/>
# MAGIC <br/><a href="https://databricks.com/privacy-policy" target="blank">Privacy Policy</a> | 
# MAGIC <a href="https://databricks.com/terms-of-use" target="blank">Terms of Use</a> | 
# MAGIC <a href="https://help.databricks.com/" target="blank">Support</a>